import sqlite3
from pathlib import Path
import os

class DatabaseConnection:
    def __init__(self, db_file="library.db"):
        self.connection = None
        self.db_file = db_file
        
    def connect(self):
        try:
            db_path = Path(self.db_file).resolve()
            
            if not db_path.exists():
                print(f"Error: Database file not found!")
                print(f"Looking for: {db_path}")
                print(f"Current directory: {os.getcwd()}")
                return False
            
            self.connection = sqlite3.connect(str(db_path))
            
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Books'")
            if not cursor.fetchone():
                print("Error: Books table not found in database!")
                cursor.close()
                return False
            cursor.close()
            
            return True
            
        except sqlite3.Error as e:
            print(f"Error connecting to SQLite database: {e}")
            return False
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query, params=None):
        try:
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
            else:
                self.connection.commit()
                result = cursor.rowcount
            
            cursor.close()
            return result
            
        except sqlite3.Error as e:
            print(f"Error executing query: {e}")
            return None
    
    def get_all_books(self):
        query = """
        SELECT book_id, title, author, genre, isbn
        FROM Books
        ORDER BY title
        """
        return self.execute_query(query)
    
    def search_books(self, search_term):
        query = """
        SELECT book_id, title, author, genre, isbn
        FROM Books
        WHERE title LIKE ? 
           OR author LIKE ? 
           OR genre LIKE ? 
           OR isbn LIKE ?
        ORDER BY title
        """
        search_pattern = f"%{search_term}%"
        return self.execute_query(query, (search_pattern, search_pattern, search_pattern, search_pattern))
    
    def add_book(self, title, author, genre, isbn=None):
        query = """
        INSERT INTO Books (title, author, genre, isbn)
        VALUES (?, ?, ?, ?)
        """
        params = (title, author, genre, isbn)
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            book_id = cursor.lastrowid
            cursor.close()
            return book_id
        except sqlite3.Error as e:
            print(f"Error adding book: {e}")
            return None
    
    def update_book(self, book_id, title, author, genre, isbn):
        query = """
        UPDATE Books
        SET title=?, author=?, genre=?, isbn=?
        WHERE book_id=?
        """
        params = (title, author, genre, isbn, book_id)
        
        result = self.execute_query(query, params)
        return result is not None and result > 0
    
    def delete_book(self, book_id):
        query = "DELETE FROM Books WHERE book_id=?"
        result = self.execute_query(query, (book_id,))
        return result is not None and result > 0
    
    def get_book_count(self):
        query = "SELECT COUNT(*) FROM Books"
        result = self.execute_query(query)
        return result[0][0] if result else 0