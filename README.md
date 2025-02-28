# Neural Ticker
#### Video Demo:  https://youtu.be/fAvsVnW0c5M
#### Description:

NeuralTicker is a web application built with Flask, designed to help users track stock performance, discover new investment opportunities, and gain AI-powered insights into their portfolio. Utilizing a SQLite database for user and stock data, `yfinance` for real-time market information, and Google's Gemini 2.0 Flash AI model for intelligent analysis, NeuralTicker provides a user-friendly interface for managing a personal stock watchlist and making more informed investment decisions.

The platform boasts user authentication with secure password handling, a dynamic stock search feature pulling data directly from a CSV and `yfinance`, a personalized watchlist with real-time updates, and a detailed stock view augmented by AI insights. It aims to offer a seamless and informative stock tracking experience for both novice and experienced investors.

## File Descriptions

*   **`app.py`**: The core of the application. This file manages Flask routes, handles user authentication (registration, login, logout, and password change), stock watchlist management (adding, removing), search functionality, and AI integration. It initializes the Flask app, configures sessions, establishes the database connection using the `database.py` abstraction, and defines all the web application's endpoints. Critically, it constructs the AI prompt based on stock performance data.
*   **`database.py`**: Provides a simplified SQL API built on SQLAlchemy. It offers functions for executing queries, escaping values, and handling database errors, ensuring secure and easy database interactions. It also manages connections and disconnections within the Flask application context.
*   **`helper.py`**: Contains helper functions for extracting and processing data from `yfinance` responses. These functions transform raw market data into usable performance metrics, allowing for clear and concise presentation of weekly, monthly, and yearly stock performance.
*   **`my_database.py`**: Responsible for setting up and initializing the SQLite database. It creates the `users`, `stocks`, and `watchlist` tables if they don't exist. It also populates the `stocks` table with initial data from `static/stock_data.csv`, providing a starting point for the application's search functionality.
*   **`neuralTicker.db`**: The SQLite database file where all application data is stored.
*   **`requirements.txt`**: Lists all Python packages required to run the application. Use `pip install -r requirements.txt` to install dependencies.
*   **`flask_session/`**: Stores session data when the Flask application is running, configured to use the filesystem for session management.
*   **`static/`**: Contains static files for the application.
    *   `key.txt`: Stores the API key for the Google Gemini AI service.
    *   `stock_data.csv`: Provides initial data for the `stocks` table, including stock symbols, names, and ISINs sourced from the Xetra stock exchange.
    *   `style.css`: Contains CSS styling rules, now leveraging the Pico CSS framework for a modern and accessible UI.
    *   `logos/`: Contains logo images for various companies sourced from Traderepublic, using SVG format. A `not-found.svg` image is used when a specific logo isn't available.
*   **`templates/`**: Contains HTML templates for rendering the application's UI using Jinja2.
    *   `error.html`: Displays error messages.
    *   `index.html`: The main application page, displaying the user's stock watchlist and allowing performance timeframe selection.
    *   `layout.html`: The base template, providing the overall structure and styling (Pico CSS and dark theme) for all other templates, including the header and navigation.
    *   `login.html`: The login page.
    *   `register.html`: The registration page with server-side validation for password strength.
    *   `search.html`: The stock search page, allowing users to find stocks by name or ticker and add them to their watchlist.
    *   `settings.html`: Allows users to change their password.
    *   `stock.html`: Displays detailed information about a selected stock, including AI-powered analysis using Google's Gemini 2.0 Flash model.

## Design Choices and Debates

Several design choices were considered during the development of NeuralTicker:

*   **Database Choice**: While cloud-based database solutions like PostgreSQL were considered, SQLite was selected for its simplicity, ease of deployment, and suitability for a project of this scale. Its serverless nature reduces complexity and simplifies initial setup.
*   **AI Integration**: Gemini 2.0 Flash API from Google was chosen for its sophisticated ability to understand and respond to complex prompts, combined with its access to real-time information via Google Search. The carefully crafted prompt ensures that the AI provides relevant and actionable insights based on recent stock performance and news. The Gemini 2.0 Flash model was selected due to its speed and availability, at the small expense of reduced reasoning capability.
*   **Performance Metrics**: Weekly, monthly, and yearly performance metrics were selected to provide a comprehensive view of a stock's recent and long-term performance.
*   **Front-End Framework**: Initially starting with only CSS became unwieldy. Pico.css was chosen for its simplicity, accessibility-first design, and suitability for this project's scale. The dark theme provided by Pico.css was also considered a plus.
*   **API Selection**: The `yfinance` API was chosen for its comprehensive stock information, ease of implementation, and strong community support.