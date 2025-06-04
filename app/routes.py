import sqlite3
from flask import Blueprint, render_template, request
from init_db import DB_PATH

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    results = None
    columns = []
    error = None
    if request.method == 'POST':
        query = request.form.get('query')
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.execute(query)
                if cursor.description:
                    columns = [d[0] for d in cursor.description]
                    results = cursor.fetchall()
                else:
                    # Non-select queries
                    conn.commit()
                    results = []
        except Exception as e:
            error = str(e)
    return render_template('index.html', results=results, columns=columns, error=error)


