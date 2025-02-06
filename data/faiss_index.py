import faiss
import numpy as np
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("🚨 OPENAI_API_KEY is missing!")

# Initialize OpenAI client
client = openai.OpenAI(api_key=api_key)

# Load stored documents
documents = np.load("document_texts.npy", allow_pickle=True)

# Function to generate text embeddings
def get_embedding(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return np.array(response.data[0].embedding)

# Generate embeddings for all documents
print("🔄 Generating embeddings for documents...")
embeddings = np.array([get_embedding(doc) for doc in documents])

# Create FAISS index
dimension = embeddings.shape[1]  # Get the embedding vector size
index = faiss.IndexFlatL2(dimension)  # L2 (Euclidean) distance index
index.add(embeddings)  # Add embeddings to FAISS index

# Save FAISS index
faiss.write_index(index, "faiss_index.bin")
print("✅ FAISS index successfully created and saved!")

