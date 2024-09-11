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


# --- ERROR ROUTES ---

@app.errorhandler(400) # bad request
def err400(error):
    return render_template('error.html', error_type="Bad Request", error_title="Sorry! We cannot process your request.", error_subtitle="Double check your inputs and try again.")

@app.errorhandler(401) # no authorisation
def err401(error):
    return render_template('error.html', error_type="Unauthorised Access", error_title="You do not have authorisation to view this content.", error_subtitle="Please log in to access this page.")

@app.errorhandler(403) # forbidden resource
def err403(error):
    return render_template('error.html', error_type="Forbidden", error_title="You do not have access to view this content.", error_subtitle="Please contact us if you believe this to be a mistake.")

@app.errorhandler(404) # resource not found
def err404(error):
    return render_template('error.html', error_type="Resource Not Found", error_title="Sorry! We could not find that page.", error_subtitle="Check the URL or return to the &nbsp;<a href='" + url_for('home') + "'>home page</a>.")

@app.errorhandler(500) # internal server error
def err500(error): # !!! REPLACE MY EMAIL WITH SITE EMAIL ONCE SET UP !!!
    return render_template('error.html', error_type="Internal Server Error", error_title="Sorry, something went wrong on our end.", error_subtitle="Check back later or report the issue &nbsp; <a href='mailto: dylan.bullock.965@accesscreative.ac.uk'>here</a> &nbsp; by email.")


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

@app.route('/profile')
def profile():
    username = session.get('username')
    email = session.get('email')
    return render_template('profile.html', username=username, email=email)

@app.route('/settings')
def settings():
    return render_template('settings.html')


# --- ADMIN ROUTES ---

@app.route('/admin')
@app.route('/dashboard')
def admin_dashboard():
    if not session or session.get('role') != 'Admin':
        news_title, news_content, news_author = get_news()
        return render_template('index.html', news_title=news_title, news_content=news_content, news_author=news_author)
    else:
        with db.connect(db_path) as conn:
            users = db.get_all_users(conn)


        return render_template('dashboard.html', users=users)

# --- MAIN ---

db.create_db(db_path)
with db.connect(db_path) as conn:
    db.default_admin(conn)

if __name__ == "__main__":
    app.run()