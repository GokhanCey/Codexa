import sqlite3

DB_PATH = "codexa.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            index_name TEXT,
            api_key TEXT,
            category TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_project(name, index_name, api_key, category):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO projects (name, index_name, api_key, category) VALUES (?, ?, ?, ?)",
              (name, index_name, api_key, category))
    conn.commit()
    conn.close()

def get_project(api_key):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM projects WHERE api_key=?", (api_key,))
    project = c.fetchone()
    conn.close()
    return project

def create_elastic_index(index_name):
    from elasticsearch import Elasticsearch
    import os
    from dotenv import load_dotenv

    load_dotenv()
    ELASTIC_URL = os.getenv("ELASTIC_URL")
    ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")

    if not ELASTIC_URL or not ELASTIC_API_KEY:
        raise ValueError("Elastic credentials not set in .env")

    es = Elasticsearch(ELASTIC_URL, api_key=ELASTIC_API_KEY)

    if es.indices.exists(index=index_name):
        return 

    es.indices.create(index=index_name, ignore=400)
