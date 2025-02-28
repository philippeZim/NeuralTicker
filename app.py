from database import SQL
from my_database import setup
from helper import get_data, get_data_single
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import os
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
setup()
db = SQL("sqlite:///neuralTicker.db")

# ai setup
with open("static/key.txt", "r") as f:
    key = f.read()
client = genai.Client(api_key=key)
model_id = "gemini-2.0-flash"

# Tool for Google search
google_search_tool = Tool(
    google_search=GoogleSearch()
)


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
        time_frame = request.form.get('time_frame')
        print("seeeeeeee:", time_frame)
        db.execute("UPDATE users SET performance = ? WHERE id = ?;", time_frame, session["user_id"])
        return redirect("/")
    else:
        if not "user_id" in session or not session["user_id"]:
            return redirect("login")

        user = db.execute("SELECT * FROM users WHERE id = ?;", session["user_id"])[0]
        stock_ids = db.execute("SELECT * FROM watchlist WHERE user_id = ?;", session["user_id"])

        stocks = []
        if stock_ids:
            stock_datas = []
            for stock_id in stock_ids:
                stock_data = db.execute("SELECT * FROM stocks WHERE id = ?;", stock_id["stock_id"])[0]
                stock_datas.append(stock_data)
            yfinance_data = get_data([x["ticker"] for x in stock_datas])
            for i in range(len(stock_datas)):
                path = f"/static/logos/{stock_datas[i]["isin"]}.svg"
                if not os.path.exists("." + path):
                    path = "/static/logos/not-found.svg"
                stock = {
                    "id": stock_datas[i]["id"],
                    "logo": path,
                    "name": stock_datas[i]["name"],
                    "price": round(yfinance_data[i]["price"], 2),
                    "performance": round(yfinance_data[i][user["performance"]], 2)
                }
                stocks.append(stock)
        return render_template("index.html", stocks=stocks, performance=user["performance"])

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form.get("search")
        query = f"%{query}%"
        stocks = db.execute("SELECT * FROM stocks WHERE name LIKE ?;", query)
        stocks += db.execute("SELECT * FROM stocks WHERE ticker LIKE ?;", query)
        for stock in stocks:
            path = f"/static/logos/{stock["isin"]}.svg"
            if os.path.exists("." + path):
                stock["logo"] = path
            else:
                stock["logo"] = "/static/logos/not-found.svg"
        return render_template("search.html", stocks=stocks)
    else:
        return render_template("search.html")


@app.route("/addToWatchlist", methods=["POST"])
def addToWatchlist():
    stock_id = request.form.get("stock_id")
    try:
        db.execute("INSERT INTO watchlist (user_id, stock_id) VALUES(?, ?)", session["user_id"], stock_id)
    except:
        pass
    return "", 204

@app.route("/delFromWatchlist", methods=["POST"])
def delFromWatchlist():
    stock_id = request.form.get("stock_id")
    try:
        db.execute("DELETE FROM watchlist WHERE user_id = ? AND stock_id = ?", session["user_id"], stock_id)
    except:
        pass
    return redirect("/")

@app.route("/stock", methods=["POST"])
def stock():
    stock_id = request.form.get("stock_id")
    data = db.execute("SELECT * FROM stocks WHERE id = ?", stock_id)[0]
    ticker = data["ticker"]
    yfinance_data = get_data_single(ticker)
    path = f"/static/logos/{data["isin"]}.svg"
    if not os.path.exists("." + path):
        path = "/static/logos/not-found.svg"
    stock = {
        "id": data["id"],
        "logo": path,
        "name": data["name"],
        "isin": data["isin"],
        "ticker": data["ticker"],
        "price": round(yfinance_data["price"], 2),
        "week": round(yfinance_data["week"], 2),
        "month": round(yfinance_data["month"], 2),
        "year": round(yfinance_data["year"], 2)
    }
    return render_template("stock.html", stock=stock)


@app.route("/ai", methods=["POST"])
def ai():
    data = request.get_json()
    prompt = f"""Role: You are a seasoned financial analyst advising investors on stock performance.

Task: Analyze the performance of {data["name"]} stock given the following data:
- Weekly Performance: {data["week"]}%
- Monthly Performance: {data["month"]}%
- Yearly Performance: {data["year"]}%

Process:

1. **Step-by-Step Reasoning (Chain-of-Thought):**
    Before presenting your final analysis, detail your thought process. Consider factors at different time scales:
        a. Short-Term (Weekly): What immediate events or sentiments might drive weekly fluctuations?
        b. Mid-Term (Monthly): What broader trends or company news could explain monthly performance?
        c. Long-Term (Yearly): What fundamental shifts or macroeconomic conditions are likely influencing the yearly performance?

2. **Factor Analysis:**
    Analyze the performance by considering both:
        a. Macro-economic Factors: (e.g., interest rates, inflation, sector trends, global events)
        b. Company-Specific Factors: (e.g., earnings reports, product releases, management changes, competitive landscape)

3. **Actionable Insights & Further Investigation:**
    Focus on providing actionable insights for investors. Based on your analysis, suggest concrete areas an investor should investigate further to make informed decisions.

4. **Self-Critique and Refinement:**
    After drafting your initial analysis, review and critique it for clarity, depth, and the actionability of insights. Rewrite your analysis incorporating your self-critique to enhance its quality.

Output: Present your refined analysis of {data["name"]} stock performance."""
    response = client.models.generate_content(
        model=model_id,
        contents=prompt,
        config=GenerateContentConfig(
            tools=[google_search_tool],
            response_modalities=["TEXT"],
        )
    )
    text = response.text.strip()
    return jsonify({'resp': text})


@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        old_pass = request.form.get("old_pass")
        new_pass = request.form.get("new_pass")
        confirmation = request.form.get("confirmation")

        if not old_pass or not new_pass or not confirmation:
            message = "empty field submitted"
            return render_template("error.html", message=message)
        if new_pass != confirmation:
            message = "passwords do not match"
            return render_template("error.html", message=message)
        if len(new_pass) < 5:
            message = "password to short"
            return render_template("error.html", message=message)
        entry = db.execute("SELECT * FROM users WHERE name = ?", session["user_id"])

        if len(entry) != 1 or not check_password_hash(entry[0]["hash"], old_pass):
            message = "wrong password"
            return render_template("error.html", message=message)
        pass_hash = generate_password_hash(new_pass)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", pass_hash, session["user_id"])

    else:
        username = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]["name"]
        return render_template("settings.html", username=username)














