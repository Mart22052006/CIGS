import os
from openai import OpenAI
import asyncpg
import docx  # python-docx
from quart import Quart, render_template, request
from dotenv import load_dotenv

load_dotenv()

app = Quart(__name__)

OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
DB_URL = os.getenv("SYNC_DB_URL", "")

client = OpenAI(api_key=OPEN_AI_API_KEY)

# Create table statement (if it doesn't exist)
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS embeddings_table (
    id SERIAL PRIMARY KEY,
    chunk_text TEXT,
    embedding  VECTOR(1024)  -- You can store as JSON or a Postgres vector type if configured
);
"""

CREATE_EXTENSION_SQL = "CREATE EXTENSION IF NOT EXISTS vector"


async def init_db():
    """Initialize the database and ensure the table exists."""
    try:
        pool = await asyncpg.create_pool(DB_URL)
        conn = await pool.acquire()
        await conn.execute(CREATE_TABLE_SQL)
        await conn.close()
        print("Database initialized and table ready.")
    except Exception as e:
        print("Error initializing database:", e)


async def create_extension():
    """Create the vector extension in the database."""
    try:
        pool = await asyncpg.create_pool(DB_URL)
        conn = await pool.acquire()
        await conn.execute(CREATE_EXTENSION_SQL)
        await conn.close()
        print("Vector extension created.")
    except Exception as e:
        print("Error creating extension:", e)


@app.before_serving
async def setup():
    """Initialize the database on startup."""
    await init_db()
    await create_extension()


@app.route("/")
async def index():
    return await render_template("index.html")


@app.route("/upload", methods=["POST"])
async def upload_file():
    """Handle file upload and embedding."""
    try:

        files = await request.files

        if "file" not in files:
            return "No file part in the request", 400

        file = files["file"]
        filename = file.filename

        if filename == "":
            return "No file selected", 400

        ext = os.path.splitext(filename)[1].lower()
        if ext in [".doc", ".docx"]:
            doc_file = docx.Document(file)
            full_text = "\n".join(para.text for para in doc_file.paragraphs)
        elif ext == ".txt":
            full_text = (file.read()).decode("utf-8", errors="ignore")
        else:
            return "Unsupported file type", 400

        chunk_size = 500
        chunks = [
            full_text[i : i + chunk_size].strip()
            for i in range(0, len(full_text), chunk_size)
        ]

        chunks = [chunk for chunk in chunks if chunk]

        pool = await asyncpg.create_pool(DB_URL)
        conn = await pool.acquire()

        for chunk in chunks:
            response = client.embeddings.create(
                model="text-embedding-3-large", input=chunk, dimensions=1024
            )
            embedding = response.data[0].embedding

            embedding_str = str(embedding)

            insert_sql = """
            INSERT INTO embeddings_table (chunk_text, embedding)
            VALUES ($1, $2)
            """
            await conn.execute(insert_sql, chunk, embedding_str)

        await conn.close()

        return "File processed and embeddings stored successfully!"

    except Exception as e:
        print("Error processing file:", str(e))
        return f"Error processing file: {str(e)}", 500


if __name__ == "__main__":
    # Run the Quart app
    app.run(host="0.0.0.0", port=5003)
