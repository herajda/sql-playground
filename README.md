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
* [ ] Frontend input for SQL queries
* [ ] Output panel for query results or error messages
* [ ] Schema visualization (ERD/UML-style)
* [ ] Syntax highlighting (optional)

## Setup Instructions

1. Install dependencies: `pip install -r requirements.txt`
2. Initialize the database with `python init_db.py`
3. Start the development server using `python run.py`
4. Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser.
