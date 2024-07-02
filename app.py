from flask import Flask, jsonify, request
import sqlite3
import hashlib

app = Flask(__name__)

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('registered_users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to create the users table if it doesn't exist
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT NOT NULL UNIQUE,
                      password TEXT NOT NULL,
                      first_name TEXT NOT NULL,
                      last_name TEXT NOT NULL
                      )''')
    conn.commit()
    conn.close()

# Initialize the database table
create_table()

@app.route('/')
def home():
    return "Hello, Flask"

@app.route('/api/data/register', methods=['POST'])
def register():
    request_data = request.json

    username = request_data.get('username')
    password = request_data.get('password')
    confirm_password = request_data.get('confirm_password')
    first_name = request_data.get('first_name')
    last_name = request_data.get('last_name')

    if not (username and password and confirm_password and first_name and last_name):
        return jsonify({'message': 'All fields are required'}), 400

    if password != confirm_password:
        return jsonify({'message': 'Passwords do not match'}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password, first_name, last_name) VALUES (?, ?, ?, ?)',
                       (username, hashed_password, first_name, last_name))
        conn.commit()
        return jsonify({'message': f'User {username} registered successfully!'}), 200
    except sqlite3.IntegrityError:
        return jsonify({'message': 'Username already exists'}), 400
    finally:
        conn.close()

@app.route('/api/data/login', methods=['POST'])
def login():
    request_data = request.json

    username = request_data.get('username')
    password = request_data.get('password')

    if not (username and password):
        return jsonify({'message': 'Username and password are required'}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
        user = cursor.fetchone()

        if user:
            return jsonify({'message': 'User logged in successfully!'}), 200
        else:
            return jsonify({'message': 'Invalid username or password'}), 401
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({'message': 'Failed to login'}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
