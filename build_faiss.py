import pandas as pd
import numpy as np
import faiss
import openai
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("🚨 OPENAI_API_KEY is missing!")
openai.api_key = api_key

# Read the CSV file containing plant data (ensure your CSV has the proper columns)
df = pd.read_csv("data/plants.csv")

# If your CSV does not already have the Dutch translation and the "why_good" fields,
# you can create them here using OpenAI API calls.

def translate_to_dutch(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Je bent een vertaalassistent."},
                {"role": "user", "content": f"Vertaal de volgende verzorgingsinstructie voor planten naar het Nederlands: '{text}'"}
            ],
            temperature=0.3,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def generate_why_good(plant_name):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Je bent een deskundige over planten."},
                {"role": "user", "content": f"Geef in één korte zin aan waarom de plant '{plant_name}' een goede keuze is voor binnen of op kantoor."}
            ],
            temperature=0.7,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Why-good generation error for {plant_name}: {e}")
        return ""

# Add/Update Dutch translation and why_good columns if they don't exist
if "maintenance_dutch" not in df.columns:
    print("Translating maintenance instructions to Dutch...")
    df["maintenance_dutch"] = df["maintenance"].apply(translate_to_dutch)
    time.sleep(1)

if "why_good" not in df.columns:
    print("Generating why_good descriptions...")
    df["why_good"] = df["name"].apply(generate_why_good)
    time.sleep(1)

# Function to create a combined text document from a row
def create_document(row) -> str:
    parts = []
    if pd.notnull(row["name"]):
        parts.append(f"Naam: {row['name']}")
    if pd.notnull(row.get("title", "")):
        parts.append(f"Titel: {row['title']}")
    if pd.notnull(row["height"]):
        parts.append(f"Hoogte: {row['height']}")
    if pd.notnull(row["category"]):
        parts.append(f"Categorie: {row['category']}")
    if pd.notnull(row["maintenance_dutch"]):
        parts.append(f"Verzorging: {row['maintenance_dutch']}")
    if pd.notnull(row["why_good"]):
        parts.append(f"Waarom goed: {row['why_good']}")
    return "\n".join(parts)

# Create the combined text for each plant record
df["combined_text"] = df.apply(create_document, axis=1)

# Save the documents as a NumPy array for later use by FAISS
documents = df["combined_text"].tolist()
np.save("data/document_texts.npy", np.array(documents))
print("✅ document_texts.npy has been created with combined Dutch data.")

# --- Now create the FAISS index ---
# Define a function to get embeddings for the text
def get_embedding(text: str) -> np.ndarray:
    response = openai.Embedding.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return np.array(response["data"][0]["embedding"], dtype=np.float32)

print("🔄 Generating embeddings for each document...")
embeddings_list = []
for doc in documents:
    embedding = get_embedding(doc)
    embeddings_list.append(embedding)
    time.sleep(0.5)  # Pause to avoid hitting API rate limits

embeddings = np.vstack(embeddings_list)
print("✅ Embeddings generated.")

# Create a FAISS index with these embeddings
dimension = embeddings.shape[1]  # typically 1536 for text-embedding-ada-002
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)
faiss.write_index(index, "data/faiss_index.bin")
print("✅ FAISS index successfully created and saved as 'data/faiss_index.bin'!")

