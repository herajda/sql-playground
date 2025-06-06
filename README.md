# SQL Playground

SQL Playground is a simple web application built with Python and Flask. Its purpose is to help users learn and experiment with SQL in a web-based environment, using a pre-populated SQLite3 database. It is ideal for teacher-student interaction and classroom use.
## Features

SQL Playground provides an interactive environment where users can:

* View the structure of database tables, including columns, data types, and relationships.
* Enter SQL queries into a text input box and see the results displayed directly on the page.
* Receive clear error messages and helpful feedback when queries are incorrect.
* Work with a predefined SQLite3 database hosted on the server.
* Explore and understand database design through automatic UML-style schema visualization.
* 
This project is useful for learning, demonstrations, and hands-on practice with SQL syntax—no local setup required. Its design makes it especially effective in educational settings.

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

## Admin Interface

Once the server is running, visit `http://localhost:5000/admin` in your browser to access the admin page. The login form asks for the password specified by the `ADMIN_PASSWORD` environment variable (defaults to `admin123`). After signing in you can:

* Toggle read-only mode for the playground.
* Upload additional `.db` files and activate them as the current database.
* Delete previously uploaded databases.
* Create new databases from SQL text, from an uploaded SQL file, or via the OpenAI integration when `OPENAI_API_KEY` is set.

These actions allow you to manage the databases available to users without restarting the container.
