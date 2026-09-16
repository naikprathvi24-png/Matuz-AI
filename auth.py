import sqlite3
import hashlib
import os


DB_NAME = "users.db"


def init_db():
    """Create the users table if it does not exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password):
    """Securely hash a password using SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(name, email, password):
    """Create a new user account."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
            """,
            (name.strip(), email.strip().lower(), hash_password(password))
        )

        conn.commit()
        return True, "Account created successfully."

    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."

    finally:
        conn.close()


def login_user(email, password):
    """Check login credentials."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, email
        FROM users
        WHERE email = ? AND password = ?
        """,
        (email.strip().lower(), hash_password(password))
    )

    user = cursor.fetchone()

    conn.close()

    if user:
        return True, {
            "id": user[0],
            "name": user[1],
            "email": user[2]
        }

    return False, None


init_db()