import sqlite3
import textwrap
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
import pickle

# # Initialize Ollama model
# ollama = Ollama(model_path="path/to/ollama/model")

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
def create_db():
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

# Example usage
if __name__ == "__main__":
    transcript = """
    0.00 - 30.00: towards the end of 2018 you mentioned that you guarantee you could make a 50% annual return if you had to start again with under $1 million the question is if tomorrow you woke up in the body of a of of P bodyy old P body but that's fine and your name was now Warren alakat and you had some money to Inver
30.00 - 60.00: on a full-time basis what method or methods would you use to achieve that return would it involve flipping through 20,000 pages of Moody's manual or similar Publications or finding you you know to find buts or would it be hunting for great companies at a fair price as Mr MW or would it be a combination of both with opportunity cost serving as the final Arbiter of which method to use given that your investing opportunity has now broaden significantly thank you
60.00 - 90.00: cop good question I'm glad you came and the uh the answer would be in my particular case it would be going through the 20,000 pages and since we were talking about railroads you know I went through the Moody Transportation manual a couple of times that was 1500 or 2,000 Pages or well probably 1500 pages and I found all kinds of interesting things when I was 50 or when when I
90.00 - 120.00: was uh 20 or 21 and I don't imagine there's anybody here that knows about the Green Bay and Western railroad company but uh there were hundreds and hundreds of railroad companies and I like to read about every one of them the green band Western uh in those days everybody had a nickname for for railroads I mean that was that was just what Northern Pacific was the Nipper and you know TB snow
120.00 - 150.00: was one of them in the East that used to go up to Cornell and uh the green band Western was known as grab baggage and walk and gbnw and they had an they had a bond that was actually the common stock and they had a common stock that was actually a bond and you know that that could lead to unusual things but they wouldn't lead unusual things that would
150.00 - 180.00: work for you with many millions of dollars but but if you collected a whole bunch of those which I set out to do and actually that's what impressed Charlie when I first met him because I knew all the details of all these little companies on the west coast that he thought I would never have heard of but but I knew about the Los Angeles Athletic Club or whatever it might be and he thought he was the only one that knew about that and that that that uh
180.00 - 210.00: that became an instant point of connection so to answer your question uh I would I would I don't know what the equivalent of Moody's manuals or anything would be now but I would I would try and know everything about everything small and I would find something and with a million dollars you could earn 50% a year but you have to be in love with the subject uh you can't just be in love with the money you really got to just
210.00 - 240.00: find it like a you know essentially like you know people find other things in other fields cuz they just love looking for it a biologist looks for something because they they they want to find something they and it's built in I don't know how the human brain works that much and I don't think anybody understands too well how the human brain works but but there's different people that that uh just find it exciting
240.00 - 270.00: to expand their knowledge in a given area we uh you know I know Great British players I know great chess players actually uh Kasparov came to Al met Mrs B I've had the luck of of meeting a lot of people that are unbelievably Smart in their own Arena and do some unbelievably dumb things in other areas so all I know is
270.00 - 300.00: the human brain is complicated and but it does its best when you find out what your brain is really suited for and then you just uh pound the hell out from that point and that's what I would be doing if I if I had a small amount of money and I wanted to make 50% a year but I also wanted to just play the game and you can't do it if you really if you don't find the the game of Interest whether it's Bridge or whether you know whatever it may be chess or this case
300.00 - 330.00: finding Securities that are undervalued but it sounds to me like you're on the right track I mean anybody that will come all the way to this annual meeting has got something in their mind other than Bridge or chess uh so I'm glad you came and come again next year
"""
    create_db()

    url = "youtube.com/watch?v=12345"

     # Process the transcript and store embeddings
    conn = process_transcript(url, transcript)
    
    # Example query
    query = "whom did kasparov meet?"
    
    fetch_records(url)
    print("now seraching top 3 matches")

    # Search for top 3 relevant embedding matches
    top_matches = search_top_matches(query, url)
    
    # Print the top matches
    for match in top_matches:
        print(f"Chunk: {match[0]}, Similarity: {match[1]}")
    
    conn.close()