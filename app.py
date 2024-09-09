from flask import Flask, render_template

app = Flask(__name__)


# --- ROUTES ---

@app.route('/')
@app.route('/index')
@app.route('/home')
def home():
    return render_template('index.html')


# --- MAIN ---

if __name__ == "__main__":
    app.run()