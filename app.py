from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"   # required for session

# ---------------- DB CONNECTION ----------------
def get_db():
    return sqlite3.connect("database.db")

# ---------------- INIT DB ----------------
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
        except:
            return "User already exists!"

        return redirect('/login')

    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            return redirect('/')
        else:
            return "Invalid credentials"

    return render_template('login.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- HOME (TASK LIST) ----------------
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        cursor.execute("INSERT INTO tasks (title, user_id) VALUES (?, ?)", 
                       (title, session['user_id']))
        conn.commit()

    cursor.execute("SELECT * FROM tasks WHERE user_id=?", (session['user_id'],))
    tasks = cursor.fetchall()
    conn.close()

    return render_template('index.html', tasks=tasks)

# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/')

# ---------------- COMPLETE ----------------
@app.route('/complete/<int:id>')
def complete(id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("UPDATE tasks SET status='Completed' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/')

# ---------------- EDIT ----------------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        new_title = request.form['title']
        cursor.execute("UPDATE tasks SET title=? WHERE id=?", (new_title, id))
        conn.commit()
        return redirect('/')

    cursor.execute("SELECT * FROM tasks WHERE id=?", (id,))
    task = cursor.fetchone()
    conn.close()

    return render_template('edit.html', task=task)

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)