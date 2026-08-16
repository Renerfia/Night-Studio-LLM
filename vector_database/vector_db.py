import chromadb
import google.genai as genai
from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv()

vector_db = Path("./chroma_db")
client = chromadb.PersistentClient(vector_db)
collection = client.get_or_create_collection("resolved_questions")


embedding_client = genai.Client()


#these function is for later use when adding memory system.
def text_to_embeddings(text):
    response = embedding_client.models.embed_content(
        model="gemini-embedding-2",
        contents=text
    )
    if not response.embeddings:
        raise ValueError("No embedding returned for the provided text.")

    # Google returns a list of ContentEmbedding objects; Chroma expects a raw
    # list of floats for a single vector.
    return list(response.embeddings[0].values)

def add_text_to_chromadb(post_id,text):
    embeddings = text_to_embeddings(text)
    collection.add(
        ids=[post_id],
        documents=[text],
        embeddings=[embeddings]
    )

def retrieve_memory(query,n=5):
    "Retrieve memories from the vector database"
    query_embedding = text_to_embeddings(query)
    memories = collection.query(query_embeddings=query_embedding,n_results=n)

    return memories["documents"][0]

def check_id(post_id:str)->bool:
    """Checks if similar id exists in the chromadb or not."""

    result = collection.get(ids=[post_id])

    return len(result["ids"]) > 0 