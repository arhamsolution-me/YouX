import sqlite3
import os
import json
from datetime import datetime

class MemoryService:
    def __init__(self, db_path="youx_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Table for chat history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Table for long-term facts/preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS facts (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def add_chat(self, role, content):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO chat_history (role, content) VALUES (?, ?)', (role, content))
        conn.commit()
        conn.close()

    def get_recent_history(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT role, content FROM chat_history ORDER BY id DESC LIMIT ?', (limit,))
        history = cursor.fetchall()
        conn.close()
        # Reverse to get chronological order
        return [{"role": r, "content": c} for r, c in reversed(history)]

    def save_fact(self, key, value):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO facts (key, value, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        conn.commit()
        conn.close()

    def get_fact(self, key):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM facts WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def clear_memory(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM chat_history')
        conn.commit()
        conn.close()
