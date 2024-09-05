import sqlite3

# Step 1: Connect to an in-memory database
conn = sqlite3.connect(':memory:')

def createdb():

    # Step 2: Create a cursor object
    cursor = conn.cursor()

    # Step 3: Create a table
    cursor.execute('''
    CREATE TABLE datasource (
        id INTEGER PRIMARY KEY,
        url TEXT,
        summary TEXT
    )
    ''')

# create function to fetch if url exists in db or not and return summary if exists else return empty string
def fetch_summary(url):
    cursor = conn.cursor()
    cursor.execute('SELECT summary FROM datasource WHERE url = ?', (url,))
    row = cursor.fetchone()
    return row[0] if row else ''

# create function to insert url and summary in db
def insert_summary(url, summary):
    cursor = conn.cursor()
    cursor.execute('INSERT INTO datasource (url, summary) VALUES (?, ?)', (url, summary))
    conn.commit()

# create function to showcase all records in db
def show_records():
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM datasource')
    for row in cursor.fetchall():
        print(row)


   
