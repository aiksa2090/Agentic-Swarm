import sqlite3
import os

DB_FILE = "swarm_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # جدول الجلسات
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            topic TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # جدول المحادثات للعملاء
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            agent_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )
    ''')
    
    # جدول المسودات 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drafts (
            session_id TEXT PRIMARY KEY,
            content TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )
    ''')
    
    conn.commit()
    conn.close()

# دوال مساعدة متزامنة 

def save_message(session_id: str, agent_id: int, role: str, content: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (session_id, agent_id, role, content)
        VALUES (?, ?, ?, ?)
    ''', (session_id, agent_id, role, content))
    conn.commit()
    conn.close()

def create_session(session_id: str, topic: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sessions (id, topic, status)
        VALUES (?, ?, ?)
    ''', (session_id, topic, "running"))
    conn.commit()
    conn.close()

def update_session_status(session_id: str, status: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('UPDATE sessions SET status = ? WHERE id = ?', (status, session_id))
    conn.commit()
    conn.close()

def update_draft(session_id: str, content: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO drafts (session_id, content)
        VALUES (?, ?)
        ON CONFLICT(session_id) DO UPDATE SET content=excluded.content, updated_at=CURRENT_TIMESTAMP
    ''', (session_id, content))
    conn.commit()
    conn.close()

def get_draft(session_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT content FROM drafts WHERE session_id = ?', (session_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else ""

def get_all_messages(session_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT agent_id, role, content, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp ASC', (session_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

