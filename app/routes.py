import os
import sqlite3
from flask import Blueprint, request, jsonify, abort
from werkzeug.utils import secure_filename
from .db_manager import (
    get_active_db,
    set_active_db,
    list_databases,
    UPLOAD_DIR,
    DEFAULT_DB,
)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")


def require_admin(req):
    pwd = req.headers.get("X-Admin-Password")
    if pwd != ADMIN_PASSWORD:
        abort(401)

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
        with sqlite3.connect(get_active_db()) as conn:
            cursor = conn.execute(query)
            if cursor.description:
                columns = [d[0] for d in cursor.description]
                results = cursor.fetchall()
            else:
                conn.commit()
    except Exception as e:
        error = str(e)
    return jsonify({'results': results, 'columns': columns, 'error': error})


@main.route('/api/schema', methods=['GET'])
def schema_api():
    """Return database schema information."""
    tables = []
    with sqlite3.connect(get_active_db()) as conn:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
        for (name,) in cur.fetchall():
            colcur = conn.execute(f"PRAGMA table_info({name})")
            columns = [{'name': r[1], 'type': r[2]} for r in colcur.fetchall()]
            tables.append({'name': name, 'columns': columns})
    return jsonify({'tables': tables})


@main.route('/api/admin/databases', methods=['GET'])
def admin_list():
    """List stored databases and currently active one."""
    require_admin(request)
    dbs = list_databases()
    active = os.path.basename(get_active_db())
    return jsonify({'databases': dbs, 'active': active})


@main.route('/api/admin/upload', methods=['POST'])
def admin_upload():
    """Upload a new database file."""
    require_admin(request)
    if 'file' not in request.files:
        return jsonify({'error': 'missing file'}), 400
    f = request.files['file']
    filename = secure_filename(f.filename)
    if not filename.endswith('.db'):
        return jsonify({'error': 'only .db files allowed'}), 400
    dest = os.path.join(UPLOAD_DIR, filename)
    f.save(dest)
    return jsonify({'status': 'ok'})


@main.route('/api/admin/activate', methods=['POST'])
def admin_activate():
    """Activate one of the stored databases."""
    require_admin(request)
    data = request.get_json(force=True)
    name = data.get('name')
    if not name:
        return jsonify({'error': 'missing name'}), 400
    # check uploads first
    candidate = os.path.join(UPLOAD_DIR, name)
    if not os.path.exists(candidate):
        candidate = os.path.join(os.path.dirname(DEFAULT_DB), name)
        if not os.path.exists(candidate):
            return jsonify({'error': 'not found'}), 404
    set_active_db(candidate)
    return jsonify({'status': 'ok'})


@main.route('/api/admin/delete', methods=['POST'])
def admin_delete():
    """Delete a stored database."""
    require_admin(request)
    data = request.get_json(force=True)
    name = data.get('name')
    if not name:
        return jsonify({'error': 'missing name'}), 400
    if name == os.path.basename(DEFAULT_DB):
        return jsonify({'error': 'cannot delete default'}), 400
    path = os.path.join(UPLOAD_DIR, name)
    if not os.path.exists(path):
        return jsonify({'error': 'not found'}), 404
    if os.path.samefile(path, get_active_db()):
        set_active_db(DEFAULT_DB)
    os.remove(path)
    return jsonify({'status': 'ok'})


@main.route('/api/admin/create', methods=['POST'])
def admin_create():
    """Create a new database from a SQL script."""
    require_admin(request)
    data = request.get_json(force=True)
    name = data.get('name')
    schema = data.get('schema')
    if not name or not name.endswith('.db'):
        return jsonify({'error': 'invalid name'}), 400
    if not schema:
        return jsonify({'error': 'missing schema'}), 400
    filename = secure_filename(name)
    dest = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(dest):
        return jsonify({'error': 'already exists'}), 400
    try:
        with sqlite3.connect(dest) as conn:
            conn.executescript(schema)
            conn.commit()
    except Exception as e:
        if os.path.exists(dest):
            os.remove(dest)
        return jsonify({'error': str(e)}), 400
    return jsonify({'status': 'ok'})


@main.route('/api/admin/create_from_file', methods=['POST'])
def admin_create_from_file():
    """Create a new database from an uploaded SQL schema file."""
    require_admin(request)
    if 'file' not in request.files:
        return jsonify({'error': 'missing file'}), 400
    name = request.form.get('name')
    if not name or not name.endswith('.db'):
        return jsonify({'error': 'invalid name'}), 400
    filename = secure_filename(name)
    dest = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(dest):
        return jsonify({'error': 'already exists'}), 400
    data = request.files['file'].read().decode('utf-8', errors='ignore')
    if not data:
        return jsonify({'error': 'empty file'}), 400
    try:
        with sqlite3.connect(dest) as conn:
            conn.executescript(data)
            conn.commit()
    except Exception as e:
        if os.path.exists(dest):
            os.remove(dest)
        return jsonify({'error': str(e)}), 400
    return jsonify({'status': 'ok'})
