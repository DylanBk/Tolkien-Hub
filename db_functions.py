import bcrypt
import os
import sqlite3

db_path = './instance/users.db'


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
        conn.close()

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