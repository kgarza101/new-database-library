from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from database import DatabaseConnection
import hashlib
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
port = int(os.environ.get('PORT', 5000))

#Database connections
library_db = DatabaseConnection('library.db')
users_db = DatabaseConnection('usercred.db')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def home():
    if "username" in session:
        return redirect(url_for("library"))
    return redirect(url_for("login"))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_pw = hash_password(password)
        if users_db.connect():
            cursor = users_db.connection.cursor()
            cursor.execute("SELECT username, is_admin FROM users WHERE username=? AND password=?",
                           (username, hashed_pw))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                session['username'] = result[0]
                session['is_admin'] = bool(result[1])
                flash("Login successful.", "success")
                return redirect(url_for('library'))
            
        flash("Invalid username or password", "danger")
    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        is_admin = "is_admin" in request.form
        
        if len(username) < 3:
            flash("Username must be at least 3 characters", "danger")
            return render_template("register.html")
        
        if len(password) < 5:
            flash("Password must be at least 5 characters", "danger")
            return render_template("register.html")
        
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return render_template("register.html")
        
        if users_db.connect():
            cursor = users_db.connection.cursor()
            cursor.execute("SELECT username FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                flash("Username already exists", "danger")
                cursor.close()
                return render_template("register.html")
            
            #Creates user and stores data into db
            hashed_pw = hash_password(password)
            cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                (username, hashed_pw, 1 if is_admin else 0)
            )
            users_db.connection.commit()
            cursor.close()
            
    return render_template("register.html")

@app.route('/library')
def library():
    if "username" not in session:
        return redirect(url_for("login"))
    
    books = []
    if library_db.connect():
        books = library_db.get_all_books()        
    return render_template("library.html",
                           username = session['username'],
                           is_admin = session.get('is_admin', False),
                           books = books)
    
@app.route('/api/books', methods = ['GET'])
def get_books():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    if library_db.connect():
        books = library_db.get_all_books()
        return jsonify(books)
    return jsonify([])

@app.route('/api/books/search', methods = ['GET'])
def search_books():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    search_term = request.args.get('q', '')
    if library_db.connect():
        books = library_db.search_books(search_term)
        return jsonify(books)
    return jsonify([])

@app.route('/api/books', methods = ['POST'])
def add_book():
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    if library_db.connect():
        book_id = library_db.add_book(
            data.get("title"),
            data.get("author"),
            data.get("genre", ""),
            data.get("isbn", ""))
        if book_id:
            return jsonify({"success": True, "id": book_id})
    return jsonify({"error": "Failed to add book"}), 500

#Add book
@app.route('/api/books/<int:book_id>', methods = ['PUT'])
def update_book(book_id):
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    if library_db.connect():
        success = library_db.update_book(
            book_id,
            data.get("title"),
            data.get("author"),
            data.get("genre", ""),
            data.get("isbn", ""))
        return jsonify({"success": bool(success)})
    return jsonify({"error": "Database error"}), 500

#Delete book
@app.route('/api/books/<int:book_id>', methods = ['DELETE'])
def delete_book(book_id):
    if "username" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    if library_db.connect():
        success = library_db.delete_book(book_id)
        return jsonify({"success": bool(success)})
    return jsonify({"error": "Database error"}), 500

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)


