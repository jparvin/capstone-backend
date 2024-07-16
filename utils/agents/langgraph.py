from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from typing import Annotated, Sequence, TypedDict
import operator
from langchain_pinecone import PineconeVectorStore
from database.vector_store import get_langchain_pinecone
import functools
from langchain_core.messages import AIMessage
import os 

MODEL = "gpt-4o"
TEMPERATURE = 0.1
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

class Graph():
    def __init__(self, user_id:int, session_id:int) -> None:
        self.vectorstore: PineconeVectorStore = get_langchain_pinecone(namespace=f"{user_id}_{session_id}")
        self.model: ChatOpenAI = ChatOpenAI(temperature=TEMPERATURE, model=MODEL, api_key=OPENAI_API_KEY)

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
        docs = self.vectorstore.similarity_search_by_vector_with_score(
            filter={"source": {"$in": docs}}, query=inqiury
        )
        print("retrieved docs", docs)
        return docs
    
    @tool
    def doc_search(
        self,
        files: Annotated[list[str], "This is a list of code files to search from"],
        inqiury: Annotated[str, "This is the inquiry to search for"],
    ):
        """
        Use this to retrieve information from a list of code files. It will perform a vector search on the code files and return the most relevant information
        based on the inquiry provided.
        """
        docs = self.vectorstore.similarity_search_by_vector_with_score(
            filter={"source": {"$in": docs}}, query=inqiury
        )
        print("retrieved docs", docs)
        return docs
    
    # This defines the object that is passed between each node
    # in the graph. We will create different nodes for each agent and tool
    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
        sender: str

    # Helper function to create a node for a given agent
    def agent_node(state, agent, name):
        result = agent.invoke(state)
        # We convert the agent output into a format that is suitable to append to the global state
        if isinstance(result, ToolMessage):
            pass
        else:
            result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
        return {
            "messages": [result],
            # Since we have a strict workflow, we can
            # track the sender so we know who to pass to next.
            "sender": name,
        }

    def agent_setup(self):
        # Research agent and node
        documentation_agent = self.create_agent(
            self.model,
            [self.doc_search],
            system_message="You should use the doc_search tool to search for information in the documentation.",
        )
        research_node = functools.partial(self.agent_node, agent=documentation_agent, name="Documentation Agent")

        # chart_generator
        chart_agent = self.create_agent(
            self.model,
            [python_repl],
            system_message="Any charts you display will be visible by the user.",
        )
        chart_node = functools.partial(self.agent_node, agent=chart_agent, name="chart_generator")