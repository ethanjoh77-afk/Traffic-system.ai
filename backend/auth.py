import sqlite3
import hashlib
import jwt
import datetime

SECRET_KEY = "supersecretkey123"

# ---------------- INIT DB ----------------
def init_auth_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        paid INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

# ---------------- HASH ----------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------- REGISTER ----------------
def register_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

# ---------------- LOGIN ----------------
def login_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )

    user = c.fetchone()
    conn.close()

    if user:
        token = jwt.encode({
            "username": username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=5)
        }, SECRET_KEY, algorithm="HS256")

        return token

    return None

# ---------------- VERIFY ----------------
def verify_token(token):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data
    except:
        return None

# ---------------- PAYMENT ----------------
def set_paid(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("UPDATE users SET paid=1 WHERE username=?", (username,))
    conn.commit()
    conn.close()

def is_paid(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT paid FROM users WHERE username=?", (username,))
    result = c.fetchone()
    conn.close()

    return result and result[0] == 1