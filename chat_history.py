import sqlite3
from datetime import datetime


DB_NAME = "users.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return sqlite3.connect(DB_NAME)


# ============================================================
# CREATE CHAT TABLE
# ============================================================

def init_chat_db():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (chat_id) REFERENCES chats(id)
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# CREATE NEW CHAT
# ============================================================

def create_chat(user_id, title="New Chat"):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO chats
        (user_id, title, created_at)
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            title,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    chat_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return chat_id


# ============================================================
# SAVE MESSAGE
# ============================================================

def save_message(chat_id, role, content):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO messages
        (chat_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            chat_id,
            role,
            content,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    conn.commit()
    conn.close()


# ============================================================
# GET USER CHATS
# ============================================================

def get_user_chats(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, created_at
        FROM chats
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    )

    chats = cursor.fetchall()

    conn.close()

    return chats


# ============================================================
# GET CHAT MESSAGES
# ============================================================

def get_chat_messages(chat_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT role, content
        FROM messages
        WHERE chat_id = ?
        ORDER BY id ASC
        """,
        (chat_id,)
    )

    messages = cursor.fetchall()

    conn.close()

    return messages


# ============================================================
# CHECK CHAT BELONGS TO USER
# ============================================================

def chat_belongs_to_user(chat_id, user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id
        FROM chats
        WHERE id = ? AND user_id = ?
        """,
        (chat_id, user_id)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


# ============================================================
# DELETE CHAT
# ============================================================

def delete_chat(chat_id, user_id):

    conn = get_connection()
    cursor = conn.cursor()

    # Delete messages first
    cursor.execute(
        """
        DELETE FROM messages
        WHERE chat_id = ?
        """,
        (chat_id,)
    )

    # Delete chat
    cursor.execute(
        """
        DELETE FROM chats
        WHERE id = ? AND user_id = ?
        """,
        (chat_id, user_id)
    )

    conn.commit()
    conn.close()


# ============================================================
# UPDATE CHAT TITLE
# ============================================================

def update_chat_title(chat_id, user_id, title):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE chats
        SET title = ?
        WHERE id = ? AND user_id = ?
        """,
        (
            title[:60],
            chat_id,
            user_id
        )
    )

    conn.commit()
    conn.close()


# ============================================================
# INITIALIZE
# ============================================================

init_chat_db()