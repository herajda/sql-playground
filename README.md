# SQL Playground

SQL Playground is a simple web application built with Python and Flask. Its purpose is to help users learn and experiment with SQL in a web-based environment, using a pre-populated SQLite3 database.

## Project Idea

The goal of this project is to provide an interactive environment where users can:

* View the structure of the database tables (columns, types, relationships).
* Enter SQL queries into a text input box and see the results displayed on the web page.
* Receive error messages and helpful feedback if the query is incorrect.
* Work with a predefined SQLite3 database hosted on the server.
* Explore and understand database design via automatic UML-style schema visualization.

This project is useful for learning, demonstrations, and experimenting with SQL syntax without needing to install any software locally.

## Features (Planned)

* [x] Flask web server scaffold
* [x] SQLite3 database with sample data
* [x] Frontend input for SQL queries
* [x] Output panel for query results or error messages
* [x] Schema visualization (ERD/UML-style)
* [x] Syntax highlighting for the SQL editor
* [x] UML-style schema viewer powered by Mermaid
* [x] Password protected admin mode to manage databases
* [x] Create databases from SQL scripts in the admin interface

## Setup Instructions

1. Install backend dependencies: `pip install -r requirements.txt`
2. Initialize the database with `python init_db.py`
3. Start the Flask API using `python run.py` (default URL: [http://127.0.0.1:5000/](http://127.0.0.1:5000/))
4. In `frontend/`, run `npm install` to install frontend packages.
5. Launch the Svelte app with `npm run dev` and open [http://127.0.0.1:5173/](http://127.0.0.1:5173/).
6. Admin endpoints require the `X-Admin-Password` header. The default password is `admin123`.
7. The admin interface is available at `/admin` and requires the same password.
8. The admin page also lets you create a new database by entering SQL or uploading a schema file.
