from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from langchain_community.chat_message_histories import ChatMessageHistory  # Instead of from langchain.memory import ChatMessageHistory
from autogen.agentchat import register_function
from typing import Dict, List, Optional, TypedDict
import os
from dotenv import load_dotenv
import json
import pandas as pd
import requests
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import logging
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.retrievers.bm25 import BM25Retriever
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.prompts import ChatPromptTemplate
from llama_index.llms.openai import OpenAI as LlamaOpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.storage.docstore import SimpleDocumentStore
import asyncio
from typing import Any
# Load environment variables
load_dotenv()
# First try the proper import
try:
    from langchain_core.caches import BaseCache
    from langchain_core.callbacks import Callbacks 
    from langchain_openai import ChatOpenAI
    ChatOpenAI.model_rebuild()
except ImportError:
    # Fallback to community version
    from langchain_community.chat_models import ChatOpenAI
# ========== Configuration ==========
config_list = [
    {
        "model": "gpt-4o-mini",
        "api_key": os.getenv("OPENAI_API_KEY"),
    }
]

# Document store configurations
DOCSTORE = os.getenv("DOCSTORE").split(",")
COLLECTION = os.getenv("COLLECTION").split(",")
Chroma_DATABASE = os.getenv("Chroma_DATABASE").split(",")
LLM_MODEL = os.getenv("LLM_MODEL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
QA_PROMPT_STR = os.getenv("QA_PROMPT_STR")
LLM_INSTRUCTION = os.getenv("LLM_INSTRUCTION")
NO_METADATA = os.getenv("NO_METADATA")
METADATA_INSTRUCTION = os.getenv("METADATA_INSTRUCTION").split(",")
BING_API_KEY = os.getenv("BING_API_KEY")

# Initialize Chroma embedding function
openai_ef = OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"), 
    model_name=EMBEDDING_MODEL
)

# Initialize your agents first
search_agent = AssistantAgent(
    name="Search_Expert",
    llm_config={"config_list": [{"model": "gpt-4"}]}
)

db_agent = AssistantAgent(
    name="Database_Expert", 
    llm_config={"config_list": [{"model": "gpt-4"}]}
)

doc_agent = AssistantAgent(
    name="Document_Expert",
    llm_config={"config_list": [{"model": "gpt-4"}]}
)
# ========== Tool Definitions ==========

class BingSearchTool:
    """Bing Search Tool"""
    
    def __init__(self):
        self.name = "bing_search"
        self.description = "Performs web searches using Bing API"
        self.api_key = os.getenv('BING_API_KEY')
    
    def run(self, query: str) -> str:
        """Execute the Bing search"""
        if not query:
            return "Error: No query provided"
            
        url = f'https://api.bing.microsoft.com/v7.0/search?q={query}'
        headers = {'Ocp-Apim-Subscription-Key': self.api_key}
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                results = response.json()
                summaries = []
                for result in results.get('webPages', {}).get('value', []):
                    title = result.get('name', 'No Title')
                    snippet = result.get('snippet', 'No summary available.')
                    summaries.append(f"**{title}**: {snippet}")
                return "\n\n".join(summaries) if summaries else "No results found."
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Search error: {str(e)}"
from google.adk.agents.llm_agent import LlmAgent
from google.adk.events import Event
from google.genai.types import Content, Part
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams
from dotenv import load_dotenv
import asyncio
from typing import Dict
from pydantic import BaseModel

from pydantic import BaseModel
from typing import List, Dict, Any

class PostgresToolOutput(BaseModel):
    answer: str
    sources: List[str]

    async def run(self, args: Dict[str, Any]) -> PostgresToolOutput:
        query = args.get("query")
        if not query:
            return PostgresToolOutput(answer="No query provided", sources=[])

        try:
            agent = await self._initialize_agent()
            context = {
                "query": query,
                "session_id": "postgres_session",
                "user_id": "current_user"
            }

            result = ""
            async for event in agent.run_async(context):
                if hasattr(event, 'content'):
                    content = event.content
                    if hasattr(content, 'model_dump'):  # Pydantic v2+
                        content = content.model_dump()
                    elif hasattr(content, 'dict'):  # Pydantic v1
                        content = content.dict()
                    result += str(content)

            return PostgresToolOutput(
                answer=result if result else f"No results for: {query}",
                sources=["PostgreSQL Database"]
            )
        except Exception as e:
            return PostgresToolOutput(
                answer=f"Database error: {str(e)}",
                sources=[]
            )

class PostgresTool:
    """PostgreSQL Query Tool with MCP Integration"""

    def __init__(self):
        self.name = "postgres_query"
        self.description = "Query PostgreSQL database using MCP"
        self._agent = None
        self._initialized = False

    async def _initialize_agent(self):
        if self._initialized:
            return self._agent

        print("Initializing agent...")
        try:
            print("Building connection params...")
            connection_params = StdioConnectionParams(
                server_params={
                    "command": "python",
                    "args": ["C:/Krushna/Work/Reddit_MCP/mcp-postgres/mcp-postgres/postgres_server.py"],
                    "timeout": 60.0
                }
            )
            print("Building toolset...")
            toolset = MCPToolset(connection_params=connection_params)
            print("Getting tools...")
            tools = await toolset.get_tools()
            print("Tools:", tools)
            print("Building LlmAgent...")
            self._agent = LlmAgent(
                name=self.name,
                model="gemini-2.5-flash-preview-04-17",
                instruction="You are a PostgreSQL expert. Help the user explore and query the database.",
                tools=tools
            )
            self._initialized = True
            print("LlmAgent ready!")
            return self._agent

        except Exception as e:
            import traceback
            print("Exception in _initialize_agent():", e)
            traceback.print_exc()
            raise RuntimeError(f"Failed to initialize PostgreSQL agent: {str(e)}")

    @property
    def args_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The SQL query or natural language question"
                }
            },
            "required": ["query"]
        }
        
    async def run(self, args: Dict[str, Any]) -> PostgresToolOutput:
        query = args.get("query")
        if not query:
            return PostgresToolOutput(answer="No query provided", sources=[])

        try:
            agent = await self._initialize_agent()
            context = {
                "query": query,
                "session_id": "postgres_session",
                "user_id": "current_user"
            }

            result = ""
            async for event in agent.run_async(context):
                if hasattr(event, 'content'):
                    content = event.content
                    if hasattr(content, 'model_dump'):
                        content = content.model_dump()
                    elif hasattr(content, 'dict'):
                        content = content.dict()
                    result += str(content)

            return PostgresToolOutput(
                answer=result if result else f"No results for: {query}",
                sources=["PostgreSQL Database"]
            )
        except Exception as e:
            return PostgresToolOutput(
                answer=f"Database error: {str(e)}",
                sources=[]
            )
        
def intellidoc_tool(department: str, query_text: str) -> Dict:
    """Search internal documents for answers."""
    try:
        department_index = {
            "Adv-Manufacturing": 0,
            "Adv-Inventory": 1,
            "Adv-HumanResources": 2,
            "Adv-Purchasing": 3,
            "Adv-Sales": 4
        }.get(department, 0)

        docstore_file = DOCSTORE[department_index]
        collection_name = COLLECTION[department_index]
        db_path = Chroma_DATABASE[department_index]

        collection = init_chroma_collection(db_path, collection_name)
        vector_store = ChromaVectorStore(chroma_collection=collection)
        docstore = SimpleDocumentStore.from_persist_path(docstore_file)
        storage_context = StorageContext.from_defaults(
            docstore=docstore,
            vector_store=vector_store
        )
        
        vector_index = VectorStoreIndex(
            nodes=[],
            storage_context=storage_context,
            embed_model=OpenAIEmbedding(api_key=os.getenv("OPENAI_API_KEY"))
        )
        
        bm25_retriever = BM25Retriever.from_defaults(
            docstore=docstore,
            similarity_top_k=2
        )
        
        retrieved_nodes = hybrid_retrieve(
            query_text, docstore, vector_index, bm25_retriever, alpha=0.8
        )
        context_str = "\n\n".join([
            node.get_content().replace('{', '').replace('}', '') 
            for node in retrieved_nodes
        ])

        fmt_qa_prompt = QA_PROMPT_STR.format(
            context_str=context_str,
            query_str=query_text
        )

        chat_text_qa_msgs = [
            ChatMessage(role=MessageRole.SYSTEM, content=LLM_INSTRUCTION),
            ChatMessage(role=MessageRole.USER, content=fmt_qa_prompt),
        ]

        text_qa_template = ChatPromptTemplate(chat_text_qa_msgs)
        result = vector_index.as_query_engine(
            text_qa_template=text_qa_template,
            llm=LlamaOpenAI(model=LLM_MODEL)
        ).query(query_text)
        
        return {
            "answer": result.response,
            "sources": ["Internal Documents"]
        }
    except Exception as e:
        return {
            "answer": f"Document search error: {str(e)}",
            "sources": []
        }

# ========== Initialize Tools ==========
bing_tool = BingSearchTool()
postgres_tool = PostgresTool()

# ========== Create Agents First ==========
user_proxy = UserProxyAgent(
    name="User_Proxy",
    human_input_mode="TERMINATE",
    system_message="A proxy for the user.",
    code_execution_config=False,
)

search_agent = AssistantAgent(
    name="Search_Expert",
    system_message="You perform web searches using Bing.",
    llm_config={"config_list": config_list},
)

db_agent = AssistantAgent(
    name="Database_Expert",
    system_message="You query PostgreSQL databases.",
    llm_config={"config_list": config_list},
)

doc_agent = AssistantAgent(
    name="Document_Expert",
    system_message="You search internal documents.",
    llm_config={"config_list": config_list},
)

user_proxy = UserProxyAgent(
    name="User_Proxy",
    human_input_mode="TERMINATE",
    system_message="A proxy for the user.",
    code_execution_config=False,
)

# ========== Register Tools After Agent Creation ==========
def bing_search_wrapper(query: str):
    return {"answer": bing_tool.run(query), "sources": ["Bing Search"]}

async def postgres_query_wrapper(query: str):
    result = await postgres_tool.run({"query": query})
    return result.model_dump()



def intellidoc_tool(query: str, department: str):
    return {"answer": f"Doc results for {query}", "sources": ["Internal Docs"]}


# Register tools with the specific agents
# Register tools with the specific agents
register_function(
    bing_search_wrapper,
    caller=search_agent,
    executor=user_proxy,  # User proxy will handle execution
    name="bing_search",
    description="Search the web using Bing API"
)

register_function(
    postgres_query_wrapper,
    caller=db_agent,
    executor=user_proxy,  # User proxy will handle execution
    name="postgres_query",
    description="Query PostgreSQL database"
)

register_function(
    intellidoc_tool,
    caller=doc_agent,
    executor=user_proxy,  # User proxy will handle execution
    name="intellidoc",
    description="Search internal documents"
)

# ========== Group Chat Setup ==========
# Create group chat
groupchat = GroupChat(
    agents=[user_proxy, search_agent, db_agent, doc_agent],
    messages=[],
    max_round=10
)

manager = GroupChatManager(groupchat=groupchat, llm_config={"config_list": config_list})

# ========== Helper Functions ==========
def init_chroma_collection(db_path: str, collection_name: str):
    """Initialize ChromaDB collection."""
    try:
        db = chromadb.PersistentClient(path=db_path)
        collection = db.get_or_create_collection(
            collection_name, 
            embedding_function=openai_ef
        )
        return collection
    except Exception as e:
        raise RuntimeError(f"Error initializing Chroma collection: {str(e)}")

def hybrid_retrieve(query: str, docstore, vector_index, bm25_retriever, alpha=0.5):
    """Perform hybrid retrieval using BM25 and vector search."""
    try:
        bm25_results = bm25_retriever.retrieve(query)
        vector_results = vector_index.as_retriever(similarity_top_k=2).retrieve(query)
    except Exception as e:
        raise RuntimeError(f"Error with retriever: {str(e)}")
    
    combined_results = {}
    for result in bm25_results:
        combined_results[result.id_] = combined_results.get(result.id_, 0) + (1 - alpha)
    for result in vector_results:
        combined_results[result.id_] = combined_results.get(result.id_, 0) + alpha

    sorted_results = sorted(combined_results.items(), key=lambda x: x[1], reverse=True)
    return [docstore.get_document(doc_id) for doc_id, _ in sorted_results[:4]]

# ========== Execution Function ==========
async def run_adk_workflow_async(question: str):
    """Async version of the workflow"""
    await user_proxy.a_initiate_chat(
        manager,
        message=question
    )

def run_adk_workflow(question: str):
    """Synchronous entry point"""
    asyncio.run(run_adk_workflow_async(question))
