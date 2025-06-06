"""
1. Run: `pip install openai lancedb tantivy pypdf sqlalchemy phidata` to install the dependencies
2. Run: `python cookbook/rag/04_agentic_rag_lancedb.py` to run the agent
"""
import sys
sys.path.append("../")
from cigs.agent import Agent
from cigs.model.openai import OpenAIChat
from cigs.embedder.openai import OpenAIEmbedder
from cigs.knowledge.pdf import PDFUrlKnowledgeBase
from cigs.vectordb.lancedb import LanceDb, SearchType

# Create a knowledge base of PDFs from URLs
knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://phi-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    # Use LanceDB as the vector database and store embeddings in the `recipes` table
    vector_db=LanceDb(
        table_name="recipes",
        uri="tmp/lancedb",
        search_type=SearchType.vector,
        embedder=OpenAIEmbedder(model="text-embedding-3-small"),
    ),
)
# Load the knowledge base: Comment after first run as the knowledge base is already loaded
knowledge_base.load()

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    knowledge=knowledge_base,
    # Add a tool to search the knowledge base which enables agentic RAG.
    # This is enabled by default when `knowledge` is provided to the Agent.
    search_knowledge=True,
    show_tool_calls=True,
    markdown=True,
)
agent.print_response("How do I make chicken and galangal in coconut milk soup", stream=True)
