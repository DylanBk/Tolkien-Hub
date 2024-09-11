import bcrypt
import datetime
import os
import sqlite3

db_path = './instance/users.db'

datetime = datetime.datetime
# --- SET UP FUNCTIONS ---

def connect(db_path):
    return sqlite3.connect(db_path)

def db_exists(db_path):
    if os.path.exists(db_path):
        return True
    else:
        return False

def create_table(conn, table_name, columns):
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS {} ({})".format(table_name, ", ".join(columns)))
    conn.commit()

def create_db(db_path):
    db = db_exists(db_path)

    if db:
        print("Database Already Exists")
    else:
        print("Creating Database...")

        conn = connect(db_path)
    
        conn.execute("PRAGMA foreign_keys = ON")

        create_table(conn, "users", ["uid INTEGER PRIMARY KEY AUTOINCREMENT", "email TEXT UNIQUE", "username TEXT NOT NULL", "password TEXT NOT NULL", "role TEXT DEFAULT 'User'"])
        create_table(conn, "news", ["id INTEGER PRIMARY KEY AUTOINCREMENT", "title TEXT NOT NULL", "content TEXT NOT NULL", "author TEXT NOT NULL", "date TEXT NOT NULL", "time TEXT NOT NULL"])

        conn.close()

def default_admin(conn):
    c = conn.cursor()
    c.execute("UPDATE users SET role = 'Admin' WHERE email = 'admin@domain.com'")
    return c.rowcount


# --- USER CRUD FUNCTIONS

def create_user(conn, user_data):
    email, username, password, role = user_data

    c = conn.cursor()

    salt = bcrypt.gensalt()
    password = bcrypt.hashpw(password.encode('utf-8'), salt)

    c.execute("INSERT INTO users (email, username, password, role) VALUES (?, ?, ?, ?)", (email, username, password, role))
    return c.lastrowid

def get_user_by_email(conn, email):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email, ))
    return c.fetchone()


# --- WEBSITE CRUD FUNCTIONS ---

def create_news_item(conn, data):
    title, content, author = data

    c = conn.cursor()

    try:
        c.execute("INSERT INTO news (title, content, author, date, time) VALUES (?, ?, ?, ?, ?)", (title, content, author, datetime.now().date(), datetime.now().time()))
        return c.lastrowid
    except Exception as e:
        print(f"Error: {e}")
        return str(e)
    

def read_news(conn):
    c = conn.cursor()

    try:
        query = ("SELECT title, content, author FROM news ORDER BY id DESC LIMIT 1;")
        c.execute(query)
        title, content, author = c.fetchone()
        return title, content, author
    except Exception as e:
        print(f"Error: {e}")
        return str(e)