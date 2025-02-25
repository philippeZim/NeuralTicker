from database import SQL

db = SQL("sqlite:///neuralTicker.db")

def setup():
    # Create users table
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            hash TEXT NOT NULL
        );
        """)

    # Create index on users(name)
    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_users_name ON users(name);
        """)

    # Create stocks table
    db.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            isin TEXT UNIQUE NOT NULL,
            wkn TEXT UNIQUE NOT NULL,
            mnemonic TEXT NOT NULL,
            ticker TEXT
        );
        """)

    # Create index on stocks(ISIN) for faster lookups
    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_stocks_isin ON stocks(isin);
        """)
    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_stocks_name ON stocks(name);
        """)

    db.execute("""
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                stock_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
                UNIQUE(user_id, stock_id)
            );
        """)

def load_stock_data():
    with open("./static/stock_data.csv", "r") as f:
        lines = [l.rstrip().split(";") for l in f]

    for x in lines[1:]:
        print(x)
        name = x[0] if x[0] else None
        isin = x[1] if x[1] else None
        wkn = x[2] if x[2] else None
        mnemonic = x[3] if x[3] else None
        ticker = x[4] if x[4] else None
        try:
            db.execute("INSERT INTO stocks (name, isin, wkn, mnemonic, ticker) VALUES (?, ?, ?, ?, ?)", name, isin, wkn, mnemonic, ticker)
        except:
            pass


def search_stock(query):
    query = f"%{query}%"  # Prepare for SQL LIKE query
    results = db.execute("SELECT * FROM stocks WHERE name LIKE ?;", query)
    results += db.execute("SELECT * FROM stocks WHERE ticker LIKE ?;", query)
    return results

print(search_stock("goog"))