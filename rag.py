import sqlite3
import textwrap
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
import pickle


conn = sqlite3.connect(':memory:')

# Function to split transcript into 30-second chunks
def split_transcript(transcript):
    lines = transcript.strip().split('\n')
    chunks = [line.split(': ')[1] for line in lines]
    print(len(chunks))
    print(chunks[0])
    return chunks

# Function to generate embeddings for a chunk
def generate_embedding(chunk):
    embeddingFunction = OllamaEmbeddingFunction(url="http://localhost:11434/api/embeddings", model_name="nomic-embed-text")
    return embeddingFunction([chunk])

# Function to create the in-memory database and table
def create_embedddb():
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE embeddings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        chunk TEXT,
        embedding BLOB
    )
    ''')
    # conn.commit()
    # return conn

# Function to insert embedding into the database
def insert_embedding(url, chunk, embedding):
    cursor = conn.cursor()
    embedding_blob = pickle.dumps(embedding)
    cursor.execute('''
    INSERT INTO embeddings (url, chunk, embedding) VALUES (?, ?, ?)
    ''', (url, chunk, embedding_blob))
    conn.commit()

# Function to process the transcript and store embeddings
def process_transcript(url, transcript):
    chunks = split_transcript(transcript)
    for chunk in chunks:
        embedding = generate_embedding(chunk)
        insert_embedding(url, chunk, embedding)
    return conn

def fetch_records(url):
    cursor = conn.cursor()
    cursor.execute('SELECT chunk, embedding FROM embeddings where url = ?', (url,))
    rows = cursor.fetchall()
    print(len(rows))
    # print(rows)

# Function to flatten nested lists
def flatten(nested_list):
    return [item for sublist in nested_list for item in sublist]


# Function to search for top 3 relevant embedding matches
def search_top_matches(query,url, top_k=3):
    query_embedding = generate_embedding(query)
    query_embedding = flatten(query_embedding)
    cursor = conn.cursor()
    cursor.execute('SELECT chunk, embedding FROM embeddings where url = ?', (url,))
    rows = cursor.fetchall()
    print("rows found")
    print(len(rows))
    
    # Calculate cosine similarity
    def cosine_similarity(vec1, vec2):
        if len(vec1) != len(vec2):
            print(len(vec1))
            print(len(vec2))
            raise ValueError("Vectors are of different lengths")
        dot_product = sum(p*q for p,q in zip(vec1, vec2))
        magnitude = (sum([val**2 for val in vec1])**0.5) * (sum([val**2 for val in vec2])**0.5)
        if not magnitude:
            return 0
        return dot_product/magnitude

    similarities = [(chunk, cosine_similarity(query_embedding, flatten(pickle.loads(embedding)))) for chunk, embedding in rows]
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]
