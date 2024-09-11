import bcrypt
from datetime import timedelta
# from dotenv import load_dotenv
from flask import Flask, redirect, render_template,request, session, url_for
import os
import db_functions as db

app = Flask(__name__)
# load_dotenv()
# app.secret_key = os.environ.get('SECRET_KEY')
app.secret_key = "secret"
print(os.environ.get('SECRET_KEY'))
app.permanent_session_lifetime = timedelta(minutes=5)

db_path = './instance/users.db'


# --- UTILS ---

def get_news():
    with db.connect(db_path) as conn:
        title, content, author = db.read_news(conn)

    return title, content, author


# --- ROUTES ---

@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    news_title, news_content, news_author = get_news()
    return render_template('index.html', news_title=news_title, news_content=news_content, news_author=news_author)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session:
        news_title, news_content, news_author = get_news()
        return render_template('index.html', news_title=news_title, news_content=news_content, news_author=news_author)

    if request.method == "POST":
        try:
            print(request.form)
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            print(email, username, password)
            user_data = [email, username, password, "User"]

            with db.connect(db_path) as conn:
                db.create_user(conn, user_data)

            return render_template('login.html')
        except Exception as e:
            print(f"Error: {e}")
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session:
        news_title, news_content, news_author = get_news()
        return render_template('index.html', news_title=news_title, news_content=news_content, news_author=news_author)

    if request.method == "POST":
        try:
            email = request.form['email']
            password = request.form['password']

            with db.connect(db_path) as conn:
                user = db.get_user_by_email(conn, email)

            if user:
                if bcrypt.checkpw(password.encode('utf-8'), user[3]):
                    session.permanent = True
                    session['user_id'] = user[0]
                    session['email'] = user[1]
                    session['username'] = user[2]
                    session['role'] = user[4]
                    conn.close()

                    news_title, news_content, news_author = get_news()
                    return render_template('index.html', news_title=news_title, news_content=news_content, news_author=news_author)
                else:
                    return render_template('login.html', error_message="Incorrect Password")
            else:
                return render_template('login.html', error_message="A user with this email does not exist")
        except Exception as e:
            print(f"Error: {e}")
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    if session:
        session.pop('user_id', None)
        session.pop('email', None)
        session.pop('username', None)
        session.pop('role', None)
        session.clear()

    news_title, news_content, news_author = get_news()
    return render_template('index.html', news_title=news_title, news_content=news_content, news_author=news_author)

@app.route('/settings')
def settings():
    return render_template('settings.html')


# --- ADMIN ROUTES ---

@app.route('/dashboard')
def admin_dashboard():
    if not session or session.get('role') != 'Admin':
        news_title, news_content, news_author = get_news()
        return render_template('index.html', news_title=news_title, news_content=news_content, news_author=news_author)
    else:
        return render_template('dashboard.html')

# --- MAIN ---

db.create_db(db_path)
with db.connect(db_path) as conn:
    db.default_admin(conn)

if __name__ == "__main__":
    app.run()