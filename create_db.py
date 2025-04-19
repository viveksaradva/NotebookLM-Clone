import os
import sqlite3

# Create the database file
db_path = "documind.db"
if os.path.exists(db_path):
    os.remove(db_path)

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    hashed_password TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
)
''')

# Create documents table
cursor.execute('''
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    document_id TEXT UNIQUE,
    file_path TEXT,
    file_type TEXT,
    chunk_count INTEGER DEFAULT 0,
    owner_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users (id)
)
''')

# Create highlights table
cursor.execute('''
CREATE TABLE highlights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT,
    highlight_type TEXT,
    sentence_type TEXT,
    note TEXT,
    document_id INTEGER,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Create chat_sessions table
cursor.execute('''
CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE,
    document_id INTEGER,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
)
''')

# Create chat_messages table
cursor.execute('''
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    role TEXT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions (id)
)
''')

# Commit changes and close connection
conn.commit()
conn.close()

print("Database created successfully with all tables!")
