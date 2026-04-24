"""
╔══════════════════════════════════════════════════════╗
║         AgriCRM — Python Flask + MySQL Backend       ║
╚══════════════════════════════════════════════════════╝

SETUP INSTRUCTIONS:
─────────────────────────────────────────
1. Install dependencies:
   pip install flask flask-cors mysql-connector-python python-dotenv

2. Create MySQL database:
   Run the SQL in schema.sql file

3. Configure .env file (or edit config below)

4. Run:
   python app.py

5. Open browser: http://localhost:5000
   Login: admin / admin123
─────────────────────────────────────────
"""

from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import hashlib
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__, static_folder='.')
app.secret_key = os.getenv('SECRET_KEY', 'agricrm_secret_2025_xyz')
CORS(app, supports_credentials=True)

# ══════════════════════════════════════
# DATABASE CONFIG — edit these values
# ══════════════════════════════════════
DB_CONFIG = {
    'host':     os.getenv('DB_HOST', 'localhost'),
    'port':     int(os.getenv('DB_PORT', 3306)),
    'user':     os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', ''),        # ← your MySQL password
    'database': os.getenv('DB_NAME', 'agricrm'),
    'autocommit': True
}

# ══════════════════════════════════════
# DB HELPER
# ══════════════════════════════════════
def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[DB ERROR] {e}")
        return None

def query(sql, params=None, fetch=True):
    conn = get_db()
    if not conn:
        return None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        if fetch:
            return cur.fetchall()
        return cur.lastrowid
    except Error as e:
        print(f"[QUERY ERROR] {e}")
        return None
    finally:
        conn.close()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ══════════════════════════════════════
# SERVE STATIC HTML
# ══════════════════════════════════════
@app.route('/')
def index():
    return send_from_directory('.', 'login.html')

@app.route('/<path:f>')
def static_files(f):
    return send_from_directory('.', f)

# ══════════════════════════════════════
# AUTH
# ══════════════════════════════════════
@app.route('/api/login', methods=['POST'])
def login():
    d = request.get_json()
    username = d.get('username', '').strip()
    password = d.get('password', '').strip()

    rows = query(
        "SELECT id, username, name, email FROM users WHERE username=%s AND password=%s AND is_active=1",
        (username, hash_pw(password))
    )
    if rows:
        u = rows[0]
        session['user_id'] = u['id']
        query("UPDATE users SET last_login=NOW() WHERE id=%s", (u['id'],), fetch=False)
        log_activity(u['id'], 'LOGIN', f"User {username} logged in")
        return jsonify({'success': True, 'user': {'id': u['id'], 'username': u['username'], 'name': u['name'], 'email': u['email']}})

    return jsonify({'success': False, 'message': 'Invalid username or password'}), 401


@app.route('/api/register', methods=['POST'])
def register():
    d = request.get_json()
    name     = d.get('name', '').strip()
    username = d.get('username', '').strip()
    email    = d.get('email', '').strip()
    password = d.get('password', '').strip()

    if not all([name, username, email, password]):
        return jsonify({'success': False, 'message': 'All fields required'}), 400
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400

    # Check duplicate
    existing = query("SELECT id FROM users WHERE username=%s OR email=%s", (username, email))
    if existing:
        return jsonify({'success': False, 'message': 'Username or email already taken'}), 409

    uid = query(
        "INSERT INTO users (name, username, email, password, created_at) VALUES (%s,%s,%s,%s,NOW())",
        (name, username, email, hash_pw(password)), fetch=False
    )
    return jsonify({'success': True, 'message': 'Account created', 'user_id': uid})


@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    d = request.get_json()
    email = d.get('email', '').strip()
    rows = query("SELECT id FROM users WHERE email=%s", (email,))
    # In production: send actual reset email
    # For demo: always return success
    return jsonify({'success': True, 'message': f'Reset link sent to {email}'})


@app.route('/api/profile', methods=['POST'])
def update_profile():
    d = request.get_json()
    uid = session.get('user_id', 1)
    fields = []
    params = []
    if d.get('name'):    fields.append('name=%s');     params.append(d['name'])
    if d.get('email'):   fields.append('email=%s');    params.append(d['email'])
    if d.get('password'):
        fields.append('password=%s')
        params.append(hash_pw(d['password']))
    if fields:
        params.append(uid)
        query(f"UPDATE users SET {','.join(fields)} WHERE id=%s", tuple(params), fetch=False)
    return jsonify({'success': True, 'message': 'Profile updated'})


# ══════════════════════════════════════
# FARMERS
# ══════════════════════════════════════
@app.route('/api/farmers', methods=['GET'])
def get_farmers():
    rows = query("SELECT * FROM farmers ORDER BY created_at DESC")
    return jsonify({'success': True, 'farmers': rows or []})


@app.route('/api/farmers', methods=['POST'])
def save_farmers():
    """Bulk sync from frontend localStorage"""
    d = request.get_json()
    farmers = d.get('farmers', [])
    query("DELETE FROM farmers", fetch=False)
    for f in farmers:
        query(
            "INSERT INTO farmers (name,phone,location,land_size,primary_crop,other_crops,status,notes,joined_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (f.get('name'), f.get('phone'), f.get('location'), f.get('land'),
             f.get('crop'), f.get('otherCrop'), f.get('status','Active'),
             f.get('notes'), f.get('date') or None),
            fetch=False
        )
    return jsonify({'success': True, 'saved': len(farmers)})


@app.route('/api/farmers/add', methods=['POST'])
def add_farmer():
    d = request.get_json()
    fid = query(
        "INSERT INTO farmers (name,phone,location,land_size,primary_crop,other_crops,status,notes,joined_date,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())",
        (d.get('name'), d.get('phone'), d.get('location'), d.get('land'),
         d.get('crop'), d.get('otherCrop'), d.get('status','Active'),
         d.get('notes'), d.get('date') or None),
        fetch=False
    )
    log_activity(session.get('user_id',1), 'ADD_FARMER', f"Added farmer: {d.get('name')}")
    return jsonify({'success': True, 'id': fid})


@app.route('/api/farmers/<int:fid>', methods=['PUT'])
def update_farmer(fid):
    d = request.get_json()
    query(
        "UPDATE farmers SET name=%s,phone=%s,location=%s,land_size=%s,primary_crop=%s,other_crops=%s,status=%s,notes=%s WHERE id=%s",
        (d.get('name'), d.get('phone'), d.get('location'), d.get('land'),
         d.get('crop'), d.get('otherCrop'), d.get('status','Active'), d.get('notes'), fid),
        fetch=False
    )
    return jsonify({'success': True})


@app.route('/api/farmers/<int:fid>', methods=['DELETE'])
def delete_farmer(fid):
    query("DELETE FROM farmers WHERE id=%s", (fid,), fetch=False)
    return jsonify({'success': True})


# ══════════════════════════════════════
# MARKET PRICES
# ══════════════════════════════════════
@app.route('/api/market', methods=['GET'])
def get_market():
    rows = query("SELECT * FROM market_prices ORDER BY date DESC, created_at DESC")
    return jsonify({'success': True, 'market': rows or []})


@app.route('/api/market', methods=['POST'])
def save_market():
    d = request.get_json()
    prices = d.get('market', [])
    query("DELETE FROM market_prices", fetch=False)
    for p in prices:
        query(
            "INSERT INTO market_prices (crop_name,price_per_quintal,market_name,price_date,trend,grade) VALUES (%s,%s,%s,%s,%s,%s)",
            (p.get('crop'), p.get('price'), p.get('market'), p.get('date') or None,
             p.get('trend','→ Stable'), p.get('grade','A Grade')),
            fetch=False
        )
    return jsonify({'success': True})


@app.route('/api/market/add', methods=['POST'])
def add_market():
    d = request.get_json()
    pid = query(
        "INSERT INTO market_prices (crop_name,price_per_quintal,market_name,price_date,trend,grade,created_at) VALUES (%s,%s,%s,%s,%s,%s,NOW())",
        (d.get('crop'), d.get('price'), d.get('market'), d.get('date') or None,
         d.get('trend','→ Stable'), d.get('grade','A Grade')),
        fetch=False
    )
    return jsonify({'success': True, 'id': pid})


@app.route('/api/market/<int:pid>', methods=['PUT'])
def update_market(pid):
    d = request.get_json()
    query(
        "UPDATE market_prices SET crop_name=%s,price_per_quintal=%s,market_name=%s,price_date=%s,trend=%s,grade=%s WHERE id=%s",
        (d.get('crop'), d.get('price'), d.get('market'), d.get('date') or None,
         d.get('trend','→ Stable'), d.get('grade','A Grade'), pid),
        fetch=False
    )
    return jsonify({'success': True})


@app.route('/api/market/<int:pid>', methods=['DELETE'])
def delete_market(pid):
    query("DELETE FROM market_prices WHERE id=%s", (pid,), fetch=False)
    return jsonify({'success': True})


# ══════════════════════════════════════
# TASKS / REMINDERS
# ══════════════════════════════════════
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    rows = query("SELECT * FROM tasks ORDER BY due_date ASC, created_at DESC")
    return jsonify({'success': True, 'tasks': rows or []})


@app.route('/api/tasks/add', methods=['POST'])
def add_task():
    d = request.get_json()
    tid = query(
        "INSERT INTO tasks (title,task_type,priority,farmer_name,due_date,notes,status,created_at) VALUES (%s,%s,%s,%s,%s,%s,'Pending',NOW())",
        (d.get('title'), d.get('type'), d.get('priority','Normal'),
         d.get('farmer'), d.get('due') or None, d.get('notes')),
        fetch=False
    )
    return jsonify({'success': True, 'id': tid})


@app.route('/api/tasks/<int:tid>/complete', methods=['POST'])
def complete_task(tid):
    query("UPDATE tasks SET status='Done', completed_at=NOW() WHERE id=%s", (tid,), fetch=False)
    return jsonify({'success': True})


# ══════════════════════════════════════
# STATS
# ══════════════════════════════════════
@app.route('/api/stats', methods=['GET'])
def get_stats():
    farmers_count = query("SELECT COUNT(*) as c FROM farmers")[0]['c']
    market_count  = query("SELECT COUNT(*) as c FROM market_prices")[0]['c']
    tasks_pending = query("SELECT COUNT(*) as c FROM tasks WHERE status='Pending'")[0]['c']
    avg_price_row = query("SELECT AVG(price_per_quintal) as avg FROM market_prices")
    avg_price = round(avg_price_row[0]['avg'] or 0)
    return jsonify({
        'success': True,
        'farmers': farmers_count,
        'market_items': market_count,
        'tasks_pending': tasks_pending,
        'avg_price': avg_price
    })


# ══════════════════════════════════════
# ACTIVITY LOG
# ══════════════════════════════════════
def log_activity(user_id, action, detail):
    query(
        "INSERT INTO activity_log (user_id, action, detail, created_at) VALUES (%s,%s,%s,NOW())",
        (user_id, action, detail), fetch=False
    )

@app.route('/api/activity', methods=['GET'])
def get_activity():
    rows = query("SELECT * FROM activity_log ORDER BY created_at DESC LIMIT 50")
    return jsonify({'success': True, 'activity': rows or []})


# ══════════════════════════════════════
# FINANCE  (income / expense tracker)
# ══════════════════════════════════════
@app.route('/api/finance', methods=['GET'])
def get_finance():
    rows = query("SELECT * FROM finance_entries ORDER BY entry_date DESC, created_at DESC")
    return jsonify({'success': True, 'finance': rows or []})

@app.route('/api/finance', methods=['POST'])
def save_finance_bulk():
    """Bulk sync from frontend localStorage"""
    d = request.get_json()
    items = d.get('finance', [])
    query("DELETE FROM finance_entries", fetch=False)
    for f in items:
        query(
            "INSERT INTO finance_entries (entry_type,amount,category,entry_date,farmer_name,description) VALUES (%s,%s,%s,%s,%s,%s)",
            (f.get('type','Income'), f.get('amount',0), f.get('category'),
             f.get('date') or None, f.get('farmer'), f.get('desc')),
            fetch=False
        )
    return jsonify({'success': True, 'saved': len(items)})

@app.route('/api/finance/add', methods=['POST'])
def add_finance():
    d = request.get_json()
    fid = query(
        "INSERT INTO finance_entries (entry_type,amount,category,entry_date,farmer_name,description,created_at) VALUES (%s,%s,%s,%s,%s,%s,NOW())",
        (d.get('type','Income'), d.get('amount',0), d.get('category'),
         d.get('date') or None, d.get('farmer'), d.get('desc')),
        fetch=False
    )
    log_activity(session.get('user_id',1), 'ADD_FINANCE', f"{d.get('type')} ₹{d.get('amount')} — {d.get('category')}")
    return jsonify({'success': True, 'id': fid})

@app.route('/api/finance/<int:fid>', methods=['DELETE'])
def delete_finance(fid):
    query("DELETE FROM finance_entries WHERE id=%s", (fid,), fetch=False)
    return jsonify({'success': True})

@app.route('/api/finance/summary', methods=['GET'])
def finance_summary():
    inc_row = query("SELECT COALESCE(SUM(amount),0) AS s FROM finance_entries WHERE entry_type='Income'")
    exp_row = query("SELECT COALESCE(SUM(amount),0) AS s FROM finance_entries WHERE entry_type='Expense'")
    income  = float(inc_row[0]['s'] or 0)
    expense = float(exp_row[0]['s'] or 0)
    return jsonify({'success': True, 'income': income, 'expense': expense, 'profit': income - expense})


# ══════════════════════════════════════
# FEEDBACK & REVIEWS
# ══════════════════════════════════════
@app.route('/api/feedback/app', methods=['GET'])
def get_app_feedback():
    rows = query("SELECT * FROM app_feedback ORDER BY created_at DESC")
    avg_row = query("SELECT AVG(rating) AS a, COUNT(*) AS c FROM app_feedback")
    avg = float(avg_row[0]['a'] or 0) if avg_row else 0
    cnt = avg_row[0]['c'] if avg_row else 0
    return jsonify({'success': True, 'feedback': rows or [], 'average': round(avg, 1), 'count': cnt})

@app.route('/api/feedback/app', methods=['POST'])
def add_app_feedback():
    d = request.get_json()
    name    = (d.get('name') or 'Anonymous').strip()[:100]
    rating  = max(1, min(5, int(d.get('rating', 5))))
    comment = (d.get('comment') or '').strip()[:1000]
    if not comment:
        return jsonify({'success': False, 'message': 'Comment required'}), 400
    fid = query(
        "INSERT INTO app_feedback (name,rating,comment,created_at) VALUES (%s,%s,%s,NOW())",
        (name, rating, comment), fetch=False
    )
    return jsonify({'success': True, 'id': fid})

@app.route('/api/feedback/farmer', methods=['GET'])
def get_farmer_reviews():
    rows = query("SELECT * FROM farmer_reviews ORDER BY created_at DESC")
    return jsonify({'success': True, 'reviews': rows or []})

@app.route('/api/feedback/farmer', methods=['POST'])
def add_farmer_review():
    d = request.get_json()
    farmer = (d.get('farmer') or '').strip()[:100]
    review = (d.get('review') or '').strip()[:2000]
    if not farmer or not review:
        return jsonify({'success': False, 'message': 'Farmer and review required'}), 400
    rating = max(1, min(5, int(d.get('rating', 5))))
    rid = query(
        "INSERT INTO farmer_reviews (farmer_name,rating,review,review_date,created_at) VALUES (%s,%s,%s,%s,NOW())",
        (farmer, rating, review, d.get('date') or None), fetch=False
    )
    return jsonify({'success': True, 'id': rid})


# ══════════════════════════════════════
# RUN
# ══════════════════════════════════════
if __name__ == '__main__':
    print("=" * 55)
    print("  🌾  AgriCRM Backend Starting...")
    print("  🌐  URL  : http://localhost:5000")
    print("  🔑  Login: admin / admin123")
    print("  🗄️   DB   : MySQL —", DB_CONFIG['database'])
    print("=" * 55)
    app.run(debug=True, port=5000, host='0.0.0.0')
