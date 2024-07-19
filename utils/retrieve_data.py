from models.other_models import InquiryFields, SourceTypes
from langchain_aws import ChatBedrock, ChatBedrockConverse
from .agents.prompt_agent import PromptAgent
from .agents.review_agent import ReviewAgent
from .agents.simple_agent import conversation_chat
from .agents.documentation_agent import query_documentation, retrieve_docs
from .agents.code_agent import query_code, retrieve_code
from sqlalchemy.orm import Session
from models.db_models import  Chat, SessionModel
from langchain_community.chat_message_histories import ChatMessageHistory
from models.request_bodies import ChatDocumentationResponse, ChatContext
from .agents.aws_setup import BedrockLLM
MODEL = "anthropic.claude-3-5-sonnet-20240620-v1:0"
TEMPERATURE = 0.5

   
class ChatWithAI:
    def __init__(self, user_id:int, session_id:int, db:Session) -> None:
        self.user_id = user_id
        self.session_id = session_id
        self.db = db
        self.namespace = self.get_namespace()
        self.chat_history = self.get_chat_history()
        self.model: ChatBedrock = BedrockLLM.get_bedrock_chat(model_id=MODEL, temperature=TEMPERATURE)
    
    def get_chat_history(self, chat_limit:int = 4) -> ChatMessageHistory:
        chat_history= ChatMessageHistory()
        conversation_history = self.db.query(Chat).filter(Chat.session_id == self.session_id).order_by(Chat.id.asc()).limit(chat_limit).all()
        for chat in conversation_history:
            if chat.role == "bot" or chat.role == "AI":
                chat_history.add_ai_message(chat.content)
            else:
                chat_history.add_user_message(chat.content)
        return chat_history
    
    def get_namespace(self):
        session = self.db.query(SessionModel).filter(SessionModel.id == self.session_id).first()
        return session.pinecone

    def change_model(self, model:str = MODEL, temp:float = TEMPERATURE):
        self.model = BedrockLLM.get_bedrock_chat(model_id=model, temperature=temp)
        return self.model

    def get_prompts(self, question):
        promptAgent = PromptAgent(self.model, self.db, self.session_id, self.user_id)
        if promptAgent.determine_scope(question):
            return promptAgent.parse_prompt(question)
        else:
            return conversation_chat(self.user_id, self.session_id, question, self.model)
    
    ## This is the function being used in our generation ##
    def start_chain_only_sources(self, question):
        print("Original Prompt: ", question)
        promptAgent = PromptAgent(self.change_model(temp=.1), self.db, self.session_id, self.user_id)
        context_question = promptAgent.clarify_original_question(self.chat_history, question)
        print("Context Question: ", context_question)
        queries = promptAgent.parse_prompt(context_question)
        documentation_sources:list[ChatContext] = []
        code_sources:list[ChatContext] = []
        for query in queries:
            source = query.source
            inquiry = query.inquiry
            files = query.files
            print(f"Source: {source}\n"
                f"Inquiry: {inquiry}\n"
                f"Files: {files}\n")
            if source == SourceTypes.documentation:
                print("Starting Documentation Retrieval")
                response = retrieve_docs(
                    files, 
                    inquiry, 
                    self.namespace
                )
                documentation_sources.append(response)
            elif source == SourceTypes.code:
                print("Starting Code Retrieval")
                response = retrieve_code(
                    files, 
                    inquiry, 
                    self.namespace
                )
                code_sources.append(response)
            elif source == SourceTypes.clarification:
                print("Starting Clarification")
                return {"response" : conversation_chat(self.chat_history, self.session_id, question, self.model)}
        print("Starting Review Agent")
        masterAgent = ReviewAgent(self.model)
        response = masterAgent.review_sources(original_question=question, context_question=context_question, documentation_sources=documentation_sources, code_sources=code_sources, chat_history=self.chat_history)
        return {"response" : response, "documentation_sources":documentation_sources, "code_sources":code_sources}
        

    def start_chain(self, question):
        promptAgent = PromptAgent(self.model, self.db, self.session_id, self.user_id)
        promptAgent = PromptAgent(self.change_model(temp=.1), self.db, self.session_id, self.user_id)
        context_question = promptAgent.clarify_original_question(self.chat_history, question)
        print("Context Question: ", context_question)
        queries = promptAgent.parse_prompt(context_question)
        documentation_responses:list[ChatDocumentationResponse] = []
        code_responses:list[ChatDocumentationResponse] = []
        for query in queries:
            source = query.source
            inquiry = query.inquiry
            files = query.files
            print(f"Source: {source}\n"
                f"Inquiry: {inquiry}\n"
                f"Files: {files}\n")
            if source == SourceTypes.documentation:
                response = query_documentation(
                    files, 
                    inquiry, 
                    self.model, 
                    self.namespace
                )
                documentation_responses.append(response)
            elif source == SourceTypes.code:
                response = query_code(
                    files, 
                    inquiry, 
                    self.model, 
                    self.namespace
                )
                code_responses.append(response)
            elif source == SourceTypes.clarification:
                return {"response" : conversation_chat(self.chat_history, self.session_id, question, self.model) }
        
        masterAgent = ReviewAgent(self.model)
        response = masterAgent.review_sources_and_prompts(original_question=question, context_question=context_question, documentation_responses=documentation_responses, code_responses=code_responses)
        return {"response" : response, "documentation_responses" :  documentation_responses, "code_responses" : code_responses}
    