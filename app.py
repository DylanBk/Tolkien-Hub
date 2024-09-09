from dotenv import load_dotenv
from flask import Flask, redirect, render_template,request, session, url_for
import os
import db_functions as db

app = Flask(__name__)
load_dotenv()
app.secret_key = os.environ.get('SECRET_KEY')

db_path = './instance/users.db'


def get_news():
    pass


# --- ROUTES ---

@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    with open('./news/news.txt', 'r') as f:
        lines = f.readlines()
        news_title = lines[0]
        news_content = lines[1]

    try:
        news_image = './news/news-image.png'
    except:
        news_image = False

    if news_image:
        return render_template('index.html', news_title=news_title, news_content=news_content, news_image=news_image)
    else:
        return render_template('index.html', news_title=news_title, news_content=news_content)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        with db.connect(db_path) as conn:
            db.create_user(conn, email, username, password, role="User")

        return redirect('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        pass
    else:
        return redirect('index.html')


# --- MAIN ---

db.create_db(db_path)
with db.connect(db_path) as conn:
    pass # add default admin

if __name__ == "__main__":
    app.run()