import bcrypt
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, redirect, render_template,request, session, url_for
import os
import db_functions as db

app = Flask(__name__)
load_dotenv()
# app.secret_key = os.environ.get('SECRET_KEY')
app.secret_key = "secret"
print(os.environ.get('SECRET_KEY'))
app.permanent_session_lifetime = timedelta(minutes=30)

db_path = './instance/users.db'


# --- UTILS ---

def get_news():
    with open('./news/news.txt', 'r') as f:
        lines = f.readlines()
        news_title = lines[0]
        news_content = lines[1]

    try:
        news_image = './news/news-image.png'
    except:
        news_image = False

    return news_title, news_content, news_image


# --- ROUTES ---

@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    news_title, news_content, news_image = get_news()
    return render_template('index.html', news_title=news_title, news_content=news_content, news_image=news_image)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session:
        news_title, news_content, news_image = get_news()
        return render_template('index.html', news_title=news_title, news_content=news_content, news_image=news_image)

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

            news_title, news_content, news_image = get_news()
            return render_template('index.html', news_title=news_title, news_content=news_content, news_image=news_image)
        except Exception as e:
            print(f"Error: {e}")
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session:
        news_title, news_content, news_image = get_news()
        return render_template('index.html', news_title=news_title, news_content=news_content, news_image=news_image)

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

                    news_title, news_content, news_image = get_news()
                    return render_template('index.html', news_title=news_title, news_content=news_content, news_image=news_image)
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

    news_title, news_content, news_image = get_news()
    return render_template('index.html', news_title=news_title, news_content=news_content, news_image=news_image)

@app.route('/settings')
def settings():
    return render_template('settings.html')

# --- MAIN ---

db.create_db(db_path)
with db.connect(db_path) as conn:
    pass # add default admin

if __name__ == "__main__":
    app.run()