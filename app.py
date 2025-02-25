from database import SQL
from my_database import setup
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
setup()
db = SQL("sqlite:///neuralTicker.db")


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response




@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")


        if not username or not password or not confirmation:
            message = "Username or Password or Confirmation was empty"
            return render_template("error.html", message=message)
        if len(password) < 5:
            message = "Password was shorter than 5 characters"
            return render_template("error.html", message=message)
        if not (password == confirmation):
            message = "Password did not match confirmation"
            return render_template("error.html", message=message)

        pass_hash = generate_password_hash(password)

        try:
            db.execute("INSERT INTO users (name, hash) VALUES(?, ?)", username, pass_hash)
        except:
            message = "username already exists"
            return render_template("error.html", message=message)

        return redirect("/login")

    else:
        return render_template("register.html")



@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            message = "Username or Password was empty"
            return render_template("error.html", message=message)

        entry = db.execute("SELECT * FROM users WHERE name = ?", username)

        if len(entry) != 1 or not check_password_hash(entry[0]["hash"], password):
            message = "invalid username and/or password"
            return render_template("error.html", message=message)

        session["user_id"] = entry[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session["user_id"] = None
    return redirect("/")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        pass
    else:
        # get users selected stocks

        return render_template("index.html")