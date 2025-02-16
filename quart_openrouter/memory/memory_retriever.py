import asyncpg
from typing import List
import logging
from openai import OpenAI
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


client = OpenAI(
    api_key=OPENAI_API_KEY,
)


# Utils
def get_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-large", input=text, dimensions=1024
    )
    embedding = response.data[0].embedding
    return embedding


class MemoryRetriever:

    def __init__(
        self,
        db_url: str,
    ):
        self.db_url = db_url
        self.pool = None

    async def init_db(self):
        """
        Initializes the connection pool to the PostgreSQL database using asyncpg.
        """
        self.pool = await asyncpg.create_pool(self.db_url)

    # Warning: Increasing the limit above 2 may result in hallucinations
    async def fetch_memories(self, user_query: str, limit: int = 2) -> List[dict]:
        if not user_query:
            raise ValueError("user_query is required.")

        vector = get_embedding(user_query)

        query = f"""
        SELECT "chunk_text"
        FROM "embeddings_table"
        ORDER BY "embedding" <-> $1::vector
        LIMIT $2;
        """

        async with self.pool.acquire() as connection:
            results = await connection.fetch(query, str(vector), limit)

        results = [dict(row) for row in results]
        return results

    async def close(self):
        """
        Closes the database connection pool.
        """
        await self.pool.close()
