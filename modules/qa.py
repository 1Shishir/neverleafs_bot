''' qa.py - Handles Q/A functionality using FAISS and OpenAI '''
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import faiss
import numpy as np
import openai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("🚨 OPENAI_API_KEY is missing!")

# Set OpenAI API key
openai.api_key = api_key

# Load FAISS index & stored text data
index = faiss.read_index("data/faiss_index.bin")
documents = np.load("data/document_texts.npy", allow_pickle=True)

# Initialize router
router = APIRouter()

def get_embedding(text: str) -> np.ndarray:
    """
    Generate an embedding for the given text using OpenAI's API.
    """
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return np.array(response["data"][0]["embedding"])

def search_faiss(query: str, top_k: int = 1) -> list:
    """
    Search the FAISS index for documents related to the query.
    Returns a list of matching documents.
    """
    query_vector = get_embedding(query).reshape(1, -1)
    distances, indices = index.search(query_vector, top_k)
    return [documents[i] for i in indices[0] if i >= 0] if indices[0].size > 0 else []

# API request model
class QueryRequest(BaseModel):
    query: str

@router.post("/query")
async def query_faiss_endpoint(request: QueryRequest):
    """
    Endpoint to process a user query:
    - Checks for greetings and responds accordingly.
    - Searches the FAISS index for context.
    - Constructs a prompt and retrieves an answer from GPT-4.
    The response will always be in Dutch.
    """
    try:
        user_query = request.query.strip().lower()
        greetings = ["hello", "hi", "hey", "good morning", "good evening", "good afternoon"]
        
        if any(greet in user_query for greet in greetings):
            return {"response": "Hallo! Hoe kan ik je helpen met planten van Neverleafs? 🌿"}
        
        best_match = search_faiss(user_query)

        if best_match:
            context = best_match[0]
            prompt = (f"Je bent een expert op het gebied van planten van Neverleafs.nl. "
                      f"Op basis van de volgende context: {context}, "
                      f"geef een korte en bondige beantwoording in het Nederlands voor de volgende vraag: {user_query}")
        else:
            prompt = (f"Je bent een expert op het gebied van planten van Neverleafs.nl. "
                      f"Geef een korte en bondige beantwoording in het Nederlands voor de volgende vraag: {user_query}")

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system", 
                    "content": "Je bent een expert op het gebied van planten van Neverleafs.nl. Geef altijd een beknopt en behulpzaam antwoord in het Nederlands."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )

        return {"response": response["choices"][0]["message"]["content"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

