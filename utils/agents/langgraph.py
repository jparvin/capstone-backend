from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
import operator
from langchain_pinecone import PineconeVectorStore
from database.vector_store import get_langchain_pinecone
import functools
import os 
from langgraph.graph import END, StateGraph, START
from sqlalchemy.orm import Session
from models.db_models import File
from langchain_core.documents import Document

MODEL = "gpt-4o"
TEMPERATURE = 0.1
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

class Graph():
    def __init__(self, user_id:int, session_id:int, db:Session):
        self.vectorstore: PineconeVectorStore = get_langchain_pinecone(namespace=f"{user_id}_{session_id}")
        self.model: ChatOpenAI = ChatOpenAI(temperature=TEMPERATURE, model=MODEL, api_key=OPENAI_API_KEY)
        self.members = ["Documentation Agent", "Code Agent", "Scope Agent"]
        self.db = db
        self.session_id = session_id
        self.user_di = user_id

    def create_agent(self, tools: list, system_prompt: str):
        # Each worker node will be given a name and some tools.
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    system_prompt,
                ),
                MessagesPlaceholder(variable_name="messages"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        agent = create_openai_tools_agent(self.model, tools, prompt)
        executor = AgentExecutor(agent=agent, tools=tools)
        return executor
    
    def agent_node(self, state, agent, name):
        result = agent.invoke(state)
        if isinstance(result, ToolMessage):
            pass
        else:
            result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
        return {
            "messages": [result],
            "sender": name,
        }
    

    
    def create_base_agent(self, tools, system_message: str):
        """Create an agent."""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK, another assistant with different tools "
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any of the other assistants have the final answer or deliverable,"
                    " prefix your response with FINAL ANSWER so the team knows to stop."
                    " You have access to the following tools: {tool_names}.\n{system_message}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        return prompt | self.model.bind_tools(tools)

    @tool
    def doc_search(
        self,
        docs: Annotated[list[str], "This is a list of documents to search from"],
        inqiury: Annotated[str, "This is the inquiry to search for"],
    ):
        """
        Use this to retrieve information from a list of documents. It will perform a vector search on the documents and return the most relevant information
        based on the inquiry provided.
        """
        docs: list[Document] = self.vectorstore.similarity_search_by_vector_with_score(
            filter={"source": {"$in": docs}}, query=inqiury
        )
        print("retrieved docs", docs)
        return "\n\n".join(
        [
            f'<Document name="{doc.metadata.get("title", "")}">\n{doc.page_content}\n</Document>'
            for doc in docs
        ]
        )
    
    @tool
    def code_search(
        self,
        files: Annotated[list[str], "This is a list of code files to search from"],
        inqiury: Annotated[str, "This is the inquiry to search for"],
    ):
        """
        Use this to retrieve information from a list of code files. It will perform a vector search on the code files and return the most relevant information
        based on the inquiry provided.
        """
        docs: list[Document] = self.vectorstore.similarity_search_by_vector_with_score(
            filter={"source": {"$in": files}}, query=inqiury
        )
        print("retrieved docs", docs)
        return "\n\n".join(
        [
            f'<Document name="{doc.metadata.get("title", "")}">\n{doc.page_content}\n</Document>'
            for doc in docs
        ]
        )
    
    @tool
    def scope_search(
        self,
        category: Annotated[str, "The category of document to search for, either code or documentation"],
    ):
        """
        Use this to retrieve the available files within a category. The two categories are code and documentation.
        Code includes all files that contain code.
        Documentation includes all files that contain system requirements, product requirements, or other supporting documentation.
        """
        docs = self.db.query(File).filter(File.session_id == self.session_id and File.category == category).all()
        file_names="\n".join([file.filename for file in docs])
        return file_names
    
    # This defines the object that is passed between each node
    # in the graph. We will create different nodes for each agent and tool
    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
        sender: str

    def agent_setup(self):
        system_prompt = (
        "You are a supervisor tasked with managing a conversation between the"
        " following workers:  {members}. Given the following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status. When finished,"
        " respond with FINISH."
        )
        # Our team supervisor is an LLM node. It just picks the next agent to process
        # and decides when the work is completed
        options = ["FINISH"] + self.members
        # Using openai function calling can make output parsing easier for us
        function_def = {
            "name": "route",
            "description": "Select the next role.",
            "parameters": {
                "title": "routeSchema",
                "type": "object",
                "properties": {
                    "next": {
                        "title": "Next",
                        "anyOf": [
                            {"enum": options},
                        ],
                    }
                },
                "required": ["next"],
            },
        }
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "system",
                    "Given the conversation above, who should act next?"
                    " Or should we FINISH? Select one of: {options}",
                ),
            ]
        ).partial(options=str(options), members=", ".join(self.members))


        supervisor_chain = (
            prompt
            | self.model.bind_functions(functions=[function_def], function_call="route")
            | JsonOutputFunctionsParser()
        )

        documentation_agent = self.create_agent(
            [self.doc_search],
            system_prompt="You should use the doc_search tool to search for information in the documentation.",
        )
        documentation_node = PregelNode(
        config={'tags': [], 'metadata': {}},
        channels={'messages': 'messages', 'sender': 'sender'},
        triggers=['branch:supervisor:condition:Documentation Agent'],
        mapper=functools.partial(_coerce_state, Graph.AgentState),
        writers=[
            ChannelWrite('Documentation Agent', messages='messages', sender='sender')
        ]
    )

        
        code_agent = self.create_agent(
            [self.code_search],
            system_prompt="You should use the code search tool to search for specific code files or information within code files.",
        )
        code_node = functools.partial(self.agent_node, agent=code_agent, name="Code Agent")

        scope_agent = self.create_agent(
            [self.scope_search],
            system_prompt="You should use the scope search tool to view what files are available in each category",
        )
        scope_node = functools.partial(self.agent_node, agent=scope_agent, name="Scope Agent")
        workflow = StateGraph(self.AgentState)

        workflow.add_node("supervisor", supervisor_chain)
        workflow.add_node("Documentation Agent", documentation_node)
        workflow.add_node("Code Agent", code_node)
        workflow.add_node("Scope Agent", scope_node)

        for member in self.members:
            workflow.add_edge(member, "supervisor")

        conditional_map = {k: k for k in self.members}
        conditional_map["FINISH"] = END
        workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)
        workflow.add_edge(START, "supervisor")
        graph = workflow.compile()
        print(graph)

        for s in graph.stream(
        {
            "messages": [
                HumanMessage(content="Give me a summary of the system overview and functional requirements from the Product Requirements doc")
            ]
        }
        ):
            if "__end__" not in s:
                print(s)
                print("----")