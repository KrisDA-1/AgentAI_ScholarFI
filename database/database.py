# database/database.py
import psycopg2
import streamlit as st

def get_connection():
    return psycopg2.connect(
        host=st.secrets["DB_HOST"],
        port=st.secrets["DB_PORT"],
        database=st.secrets["DB_NAME"],
        user=st.secrets["DB_USER"],
        password=st.secrets["DB_PASSWORD"]
    )

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # --- USERS ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password BYTEA NOT NULL
    );
    """)

    # --- TRANSACTIONS ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        amount NUMERIC NOT NULL,
        category VARCHAR(255),
        note TEXT,
        date DATE NOT NULL,
        type VARCHAR(50) NOT NULL
    );
    """)

    # --- GOALS ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name VARCHAR(255) NOT NULL,
        target_amount NUMERIC NOT NULL,
        current_amount NUMERIC DEFAULT 0,
        deadline DATE
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()


# import sqlite3
# from pathlib import Path

# DB_PATH = Path("database/scholarfi.db")

# def init_db():
#     conn = sqlite3.connect(DB_PATH)
#     cursor = conn.cursor()

#     # --- USERS ---
#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS users (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         name TEXT NOT NULL,
#         email TEXT UNIQUE NOT NULL,
#         password BLOB NOT NULL
#     )
#     """)

#     # --- TRANSACTIONS ---
#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS transactions (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         user_id INTEGER NOT NULL,
#         amount REAL NOT NULL,
#         category TEXT,
#         note TEXT,
#         date TEXT NOT NULL,
#         type TEXT NOT NULL,
#         FOREIGN KEY(user_id) REFERENCES users(id)
#     )
#     """)

#     # --- GOALS ---
#     cursor.execute("""
#     CREATE TABLE IF NOT EXISTS goals (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         user_id INTEGER NOT NULL,
#         name TEXT NOT NULL,
#         target_amount REAL NOT NULL,
#         current_amount REAL DEFAULT 0,
#         deadline TEXT,
#         FOREIGN KEY(user_id) REFERENCES users(id)
#     )
#     """)

#     conn.commit()
#     conn.close()


# def get_connection():
#     return sqlite3.connect(DB_PATH)
