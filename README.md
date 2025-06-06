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

## Running with Docker

### Build the image

```bash
docker build -t sql-playground .
```

### Run the container


```bash
docker run -p 5000:5000 \
  -e ADMIN_PASSWORD=<your password> \
  -e OPENAI_API_KEY=<your key> \
  sql-playground
```

The container exposes port 5000 and accepts optional environment variables such as `ADMIN_PASSWORD` and `OPENAI_API_KEY` for customizing the admin password or enabling the OpenAI features. They can be provided with `-e` flags when running the image.
