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

        create_table(conn, "users", ["uid INTEGER PRIMARY KEY AUTOINCREMENT", "email TEXT UNIQUE", "username TEXT UNIQUE", "password TEXT NOT NULL", "role TEXT DEFAULT 'User'", "profile_picture BLOB", "about_user TEXT DEFAULT 'Hey there!'"])
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

def get_all_users(conn):
    c = conn.cursor()
    c.execute("SELECT uid, email, username, role, profile_picture FROM users")
    return c.fetchall()

def get_user_by_username(conn, username):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    return c.fetchone()

def get_user_by_email(conn, email):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email, ))
    return c.fetchone()

def get_user_by_uid(conn, uid):
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE uid = ?", (uid, ))
    return c.fetchone()

def update_user_profile_picture(conn, uid, profile_picture):
    c = conn.cursor()
    c.execute("UPDATE users SET profile_picture = ? WHERE uid = ?", (profile_picture, uid))
    return c.lastrowid

def update_user(conn, col, value, uid):
    c = conn.cursor()
    query = f"UPDATE users SET {col} = ? WHERE uid = ?"
    c.execute(query, (value, uid))
    return c.lastrowid

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