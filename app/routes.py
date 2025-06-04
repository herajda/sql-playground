import sqlite3
from flask import Blueprint, request, jsonify
from init_db import DB_PATH

main = Blueprint('main', __name__)


@main.route('/api/query', methods=['POST'])
def query_api():
    """Execute SQL query and return JSON response."""
    data = request.get_json(force=True)
    query = data.get('query', '')
    results = []
    columns = []
    error = None
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(query)
            if cursor.description:
                columns = [d[0] for d in cursor.description]
                results = cursor.fetchall()
            else:
                conn.commit()
    except Exception as e:
        error = str(e)
    return jsonify({'results': results, 'columns': columns, 'error': error})


