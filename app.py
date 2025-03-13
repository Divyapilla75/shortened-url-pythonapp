from flask import Flask, request, redirect, render_template, jsonify
from flask_restful import Api, Resource
import sqlite3
import random
import string
from datetime import datetime
import os

app = Flask(__name__)
api = Api(app)

# def get_db_connection():
#     conn = sqlite3.connect('database.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# def get_db_connection():
#     db_path = "/data/database.db"  # Use a persistent location
#     conn = sqlite3.connect(db_path)
#     conn.row_factory = sqlite3.Row
#     return conn

def get_db_connection():
    db_path = "/data/database.db"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def generate_short_url():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

# Initialize database with required fields
conn = get_db_connection()
conn.execute('''
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        short TEXT UNIQUE,
        original TEXT,
        visit_count INTEGER DEFAULT 0,
        expiry TIMESTAMP NULL
    )
''')
conn.commit()
conn.close()

#--------------------New Code--------------------------------------------
@app.route('/api/stats/<short_url>', methods=['GET'])
def get_stats(short_url):
    conn = get_db_connection()
    url_entry = conn.execute('SELECT original, visit_count, expiry FROM urls WHERE short = ?', (short_url,)).fetchone()
    conn.close()

    if not url_entry:
        return jsonify({"error": "Short URL not found"}), 404

    return jsonify({
        "original_url": url_entry["original"],
        "visit_count": url_entry["visit_count"],
        "expiry": url_entry["expiry"] if url_entry["expiry"] else "No Expiry"
    })
#---------------------------------------------------------------------------------
#
@app.route('/api/expand/<short_url>', methods=['GET'])
def expand_url(short_url):
    conn = get_db_connection()
    url_entry = conn.execute('SELECT original FROM urls WHERE short = ?', (short_url,)).fetchone()
    conn.close()

    if url_entry:
        return jsonify({"original_url": url_entry[0]})
    else:
        return jsonify({"error": f"Short URL '{short_url}' not found"}), 404


#-----------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

# @app.route('/shorten', methods=['POST'])
# def shorten():
#     original_url = request.form['url']
#     expiry = request.form.get('expiry')  # Optional
#
#     short_url = generate_short_url()
#
#     conn = get_db_connection()
#     conn.execute('INSERT INTO urls (short, original, expiry) VALUES (?, ?, ?)',
#                  (short_url, original_url, expiry))
#     conn.commit()
#     conn.close()
#
#     return f'Short URL: <a href="/{short_url}">{request.host}/{short_url}</a>'

# @app.route('/shorten', methods=['POST'])
# def shorten():
#     original_url = request.form['url']
#     expiry = request.form.get('expiry')  # Optional expiry time in YYYY-MM-DD HH:MM:SS format
#
#     short_url = generate_short_url()
#
#     conn = get_db_connection()
#     conn.execute('INSERT INTO urls (short, original, expiry, visit_count) VALUES (?, ?, ?, ?)',
#                  (short_url, original_url, expiry, 0))
#     conn.commit()
#     conn.close()
#
#     return jsonify({"short_url": f"{request.host}/{short_url}"})
#------------New Code------------------------------------------
@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.form['url']
    expiry = request.form.get('expiry')  # Read expiry input

    short_url = generate_short_url()

    # Convert expiry string to timestamp, or store NULL
    expiry_timestamp = None
    if expiry:
        try:
            expiry_timestamp = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return jsonify({"error": "Invalid expiry format. Use YYYY-MM-DD HH:MM:SS"}), 400

    conn = get_db_connection()
    conn.execute('INSERT INTO urls (short, original, expiry, visit_count) VALUES (?, ?, ?, ?)',
                 (short_url, original_url, expiry_timestamp, 0))
    conn.commit()
    conn.close()

    return jsonify({"short_url": f"{request.host}/{short_url}"})

#-------------------------------------------------------------------------------------

@app.route('/<short_url>')
def redirect_to_original(short_url):
    conn = get_db_connection()
    url_entry = conn.execute('SELECT original, visit_count, expiry FROM urls WHERE short = ?', (short_url,)).fetchone()

    if not url_entry:
        return 'URL not found', 404

    # Check expiration
    if url_entry['expiry']:
        expiry_time = datetime.strptime(url_entry['expiry'], "%Y-%m-%d %H:%M:%S")
        if datetime.utcnow() > expiry_time:
            return 'URL expired', 410

    # Update visit count
    conn.execute('UPDATE urls SET visit_count = visit_count + 1 WHERE short = ?', (short_url,))
    conn.commit()
    conn.close()

    return redirect(url_entry['original'])

# REST API for shortening URL
class URLShortenerAPI(Resource):
    def post(self):
        data = request.json
        original_url = data.get('url')
        expiry = data.get('expiry')

        short_url = generate_short_url()
        conn = get_db_connection()
        conn.execute('INSERT INTO urls (short, original, expiry) VALUES (?, ?, ?)',
                     (short_url, original_url, expiry))
        conn.commit()
        conn.close()

        return jsonify({"short_url": f"{request.host}/{short_url}"})

api.add_resource(URLShortenerAPI, '/api/shorten')

# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)




# ---------------------------------------------------------------------------------------------------------
# #app.py
#
# from flask import Flask, request, redirect, render_template
# import sqlite3
# import random
# import string
#
# app = Flask(__name__)
#
#
# def get_db_connection():
#     conn = sqlite3.connect('database.db')
#     conn.row_factory = sqlite3.Row
#     return conn
#
#
# def generate_short_url():
#     return ''.join(random.choices(string.ascii_letters + string.digits, k=6))
#
#
# @app.route('/')
# def home():
#     return render_template('index.html')
#
#
# @app.route('/shorten', methods=['POST'])
# def shorten():
#     original_url = request.form['url']
#     short_url = generate_short_url()
#
#     conn = get_db_connection()
#     conn.execute('INSERT INTO urls (short, original) VALUES (?, ?)', (short_url, original_url))
#     conn.commit()
#     conn.close()
#
#     return f'Short URL: <a href="/{short_url}">{request.host}/{short_url}</a>'
#
#
# @app.route('/<short_url>')
# def redirect_to_original(short_url):
#     conn = get_db_connection()
#     url_entry = conn.execute('SELECT original FROM urls WHERE short = ?', (short_url,)).fetchone()
#     conn.close()
#
#     if url_entry:
#         return redirect(url_entry['original'])
#     else:
#         return 'URL not found', 404
#
#
# if __name__ == '__main__':
#     conn = get_db_connection()
#     conn.execute('''CREATE TABLE IF NOT EXISTS urls (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     short TEXT UNIQUE,
#                     original TEXT)''')
#     conn.commit()
#     conn.close()
#
#     app.run(debug=True)
#