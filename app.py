import base64
import bcrypt
from datetime import timedelta
# from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template,request, session, url_for
import os
import db_functions as db

app = Flask(__name__)
# load_dotenv()
# app.secret_key = os.environ.get('SECRET_KEY')
app.secret_key = "secret"
print(os.environ.get('SECRET_KEY'))
app.permanent_session_lifetime = timedelta(minutes=5)

db_path = './instance/users.db'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpg', 'gif', 'jfif'}


# --- UTILS ---

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_binary(file):
    if file and allowed_file(file.filename):
        image_data = file.read()

        return image_data
    return None

def convert_to_image(bin_image):
    if bin_image:
        image_b64 = base64.b64encode(bin_image).decode('utf-8')

    return image_b64

def get_news():
    with db.connect(db_path) as conn:
        title, content, author = db.read_news(conn)

    return title, content, author

def get_session_data():
    if session:
        user = {
            "user_id": session.get('user_id'),
            "email": session.get('email'),
            "username": session.get('username'),
            "role": session.get('role')
        }
        return user
    return


# --- ERROR ROUTES ---

@app.errorhandler(400) # bad request
def err400(error):
    if session:
        user = get_session_data()
        return render_template('error.html', error_type="Bad Request", error_title="Sorry! We cannot process your request.", error_subtitle="Double check your inputs and try again.", user=user)
    return render_template('error.html', error_type="Bad Request", error_title="Sorry! We cannot process your request.", error_subtitle="Double check your inputs and try again.")

@app.errorhandler(401) # no authorisation
def err401(error):
    if session:
        user = get_session_data()
        return render_template('error.html', error_type="Unauthorised Access", error_title="You do not have authorisation to view this content.", error_subtitle="Please log in to access this page.", user=user)
    return render_template('error.html', error_type="Unauthorised Access", error_title="You do not have authorisation to view this content.", error_subtitle="Please log in to access this page.")

@app.errorhandler(403) # forbidden resource
def err403(error):
    if session:
        user = get_session_data()
        return render_template('error.html', error_type="Forbidden", error_title="You do not have access to view this content.", error_subtitle="Please contact us if you believe this to be a mistake.", user=user)
    return render_template('error.html', error_type="Forbidden", error_title="You do not have access to view this content.", error_subtitle="Please contact us if you believe this to be a mistake.")

@app.errorhandler(404) # resource not found
def err404(error):
    if session:
        user = get_session_data
        return render_template('error.html', error_type="Resource Not Found", error_title="Sorry! We could not find that page.", error_subtitle="Check the URL or return to the &nbsp;<a href='" + url_for('home') + "'>home page</a>.", user=user)
    return render_template('error.html', error_type="Resource Not Found", error_title="Sorry! We could not find that page.", error_subtitle="Check the URL or return to the &nbsp;<a href='" + url_for('home') + "'>home page</a>.")

@app.errorhandler(500) # internal server error
def err500(error): # !!! REPLACE MY EMAIL WITH SITE EMAIL ONCE SET UP !!!
    if session:
        user = get_session_data()
        return render_template('error.html', error_type="Internal Server Error", error_title="Sorry, something went wrong on our end.", error_subtitle="Check back later or report the issue &nbsp; <a href='mailto: dylan.bullock.965@accesscreative.ac.uk'>here</a> &nbsp; by email.", user=user)
    return render_template('error.html', error_type="Internal Server Error", error_title="Sorry, something went wrong on our end.", error_subtitle="Check back later or report the issue &nbsp; <a href='mailto: dylan.bullock.965@accesscreative.ac.uk'>here</a> &nbsp; by email.")


# --- GENERAL ROUTES ---

@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    news_title, news_content, news_author = get_news()

    if session:
        user = get_session_data()
        return render_template('index.html', news_title=news_title, news_content=news_content, news_author=news_author, user=user)
    return render_template('index.html', news_title=news_title, news_content=news_content, news_author=news_author)

@app.route('/about')
def about():
    if session:
        user = get_session_data()
        return render_template('about.html', user=user)
    return render_template('about.html')


# --- USER AUTH ROUTES ---

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session:
        news_title, news_content, news_author = get_news()
        user = get_session_data()
        return render_template('index.html', news_title=news_title, news_content=news_content, news_author=news_author, user=user)

    if request.method == "POST":
        try:
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')
            user_data = [email, username, password, "User"]

            with db.connect(db_path) as conn:
                user_email_check = db.get_user_by_email(conn, email)

                if user_email_check:
                    return render_template('error.html', error_type="Bad Request", error_title="A user with that email already exists!", error_subtitle="Try logging in with that email.")
                
                user_username_check = db.get_user_by_username(conn, username)

                if user_username_check:
                    return render_template('error.html', error_type="Bad Request", error_title="A user with that name already exists", error_subtitle="Try again with a different username")

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
        user = get_session_data()
        return render_template('index.html', news_title=news_title, news_content=news_content, news_author=news_author, user=user)

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
                    user = get_session_data()
                    return render_template('index.html', news_title=news_title, news_content=news_content, news_author=news_author, user=user)
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


# --- PROFILE ROUTES

@app.route('/profile/<username>')
def profile(username):

    try:
        with db.connect(db_path) as conn:
            user_data = db.get_user_by_username(conn, username)

        user_data = list(user_data)
        user_data.remove(user_data[3])

        if user_data:
            if user_data[4]:
                image_data = convert_to_image(user_data[4])
            else:
                image_data = False

            user = get_session_data()
            return render_template('profile.html', user_data=user_data, pfp=image_data, user=user)
        else:
            return jsonify({"message": "User does not exist"}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": e}), 500

@app.route('/profile/<username>/edit')
def edit_profile(username):
    if session:
        if username == session.get('username') or session.get('role') == 'Admin':
            with db.connect(db_path) as conn:
                user_data = db.get_user_by_username(conn, username)

            user_data = list(user_data)
            user_data.remove(user_data[3])

            if user_data[4] is not None:
                image_data = convert_to_image(user_data[4])
            else:
                image_data = False

            user = get_session_data()
            return render_template('edit-profile.html', user_data=user_data, pfp=image_data, user=user)
        else:
            return render_template('error.html', error_type="Forbidden Resource", error_title="You do not have access to view this content.", error_subtitle="Please contact support if you believe this to be a mistake.")
    else:
        return render_template('error.html', error_type="Unauthorised Access", error_title="You do not have authorisation to view this content.", error_subtitle="Please sign in to view this page.")

@app.route('/profile/<username>/edit/change-pfp', methods=['GET', 'POST'])
def upload_profile_picture(username):
    if request.method == 'POST':
        if session:
            try:
                pfp = request.files.get('file')

                if pfp.filename == '':
                    return "No File Uploaded", 400

                bin_image = pfp.read()
                new_pfp = convert_to_image(bin_image)
                user_data = db.get_user_by_username(username)
                uid = user_data[0]

                with db.connect(db_path) as conn:
                    db.update_user_profile_picture(conn, uid, bin_image)

                return jsonify({
                    "message": "User PFP updated successfully",
                    "success": True,
                    "newUserPFP": new_pfp,
                    }), 200
            except Exception as e:
                print(f"Error: {e}")
                return jsonify({ "error": e }), 400
        else:
            news_title, news_content, news_author = get_news()
            return render_template('index.html', news_title=news_title, news_content=news_content, news_author=news_author)
    else:
        return redirect(url_for('edit_profile'))

@app.route('/profile/<username>/edit/change-username', methods=['GET', 'POST'])
def change_username(username):
    if request.method == 'POST':
        if session:
            if username == session.get('username'):
                try:
                    new_username = request.form.get('username')

                    with db.connect(db_path) as conn:
                        user = db.get_user_by_username(conn, username)
                        uid = user[0]
                        db.update_user(conn, "username", new_username, uid)

                    session['username'] = new_username

                    return redirect(url_for('edit_profile', username=new_username))
                except Exception as e:
                    print(f"Error: {e}")
                    return jsonify({"error": e}), 500
            return render_template('error.html', error_type="Forbidden Resource", error_title="You do not have access to view this content.", error_subtitle="Please contact support if you believe this to be a mistake.")
        return render_template('error.html', error_type="Unauthorised Access", error_title="You do not have authorisation to view this content.", error_subtitle="Please sign in to view this page.") 
    return redirect(url_for('home'))

@app.route('/profile/<username>/edit/change-email', methods=['GET', 'POST'])
def change_email(username):
    if request.method == 'POST':
        if session:
            if username == session.get('username'):
                try:
                    new_email = request.form.get('email')

                    with db.connect(db_path) as conn:
                        user = db.get_user_by_username(conn, username)
                        uid = user[0]
                        db.update_user(conn, "email", new_email, uid)

                    session['email'] = new_email

                    return redirect(url_for('edit_profile', username=session.get('username')))
                except Exception as e:
                    print(f"Error: {e}")
                    return jsonify({"error": e})
            return render_template('error.html', error_type="Forbidden Resource", error_title="You do not have access to view this content.", error_subtitle="Please contact support if you believe this to be a mistake.")
        return render_template('error.html', error_type="Unauthorised Access", error_title="You do not have authorisation to view this content.", error_subtitle="Please sign in to view this page.") 
    return redirect(url_for('home'))



# --- OTHER ROUTES ---

@app.route('/settings')
def settings():
    if session:
        user = get_session_data()
        return render_template('settings.html', user=user)
    return render_template('settings.html')


# --- ADMIN ROUTES ---

@app.route('/admin')
@app.route('/dashboard')
def admin_dashboard():
    if not session:
        return redirect(url_for('home'))
    elif session.get('role') != 'Admin':
        news_title, news_content, news_author = get_news()
        user = get_session_data()
        return render_template('index.html', news_title=news_title, news_content=news_content, news_author=news_author, user=user)

    with db.connect(db_path) as conn:
        users = db.get_all_users(conn)

    user_pfps = []

    for user in users:
        user_pfps.append(user[4])

    for x, user_pfp in enumerate(user_pfps):
        if user_pfp is not None:
            user_pfps[x] = convert_to_image(user_pfp)
        else:
            continue

    user_data_dict = dict(zip(users, user_pfps))

    user = get_session_data()
    return render_template('dashboard.html', users=user_data_dict, user_pfps=user_pfps, user=user)

# --- MAIN ---

db.create_db(db_path)
with db.connect(db_path) as conn:
    db.default_admin(conn)

if __name__ == "__main__":
    app.run()