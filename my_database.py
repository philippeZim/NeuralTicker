from database import SQL

db = SQL("sqlite:///neuralTicker.db")

def setup():
    # Create users table
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            hash TEXT NOT NULL
        )
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
            ticker TEXT NOT NULL
        )
        """)

    # Create index on stocks(ISIN) for faster lookups
    db.execute("""
        CREATE INDEX IF NOT EXISTS idx_stocks_isin ON stocks(isin);
        """)