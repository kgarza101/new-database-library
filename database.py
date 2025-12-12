import sqlite3
from pathlib import Path
import os

class DatabaseConnection:
    def __init__(self, db_file):
        self.db_file = db_file
        self.connection = None
        
    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_file)
            self.connection.row_factory = sqlite3.Row
            return True
        except sqlite3.Error as e:
            print(f"Error connecting to database {self.db_file}: {e}")
            return False
    
    def disconnect(self):
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query, params = None):
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith("SELECT"):
                result = [dict(row) for row in cursor.fetchall()] 
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
    
    def get_active_checkout(self, book_id):
        """Get the active checkout for a book (status = 'checked_out')"""
        try:
            query = """
            SELECT checkout_id, book_id, patron_id, checkout_date, due_date, status
            FROM Checkouts
            WHERE book_id = ? AND status = 'checked_out'
            """
            result = self.execute_query(query, (book_id,))
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting active checkout: {e}")
            return None
    
    def checkout_book(self, book_id, patron_id, checkout_date, due_date):
        """Create a new checkout record"""
        query = """
        INSERT INTO Checkouts (book_id, patron_id, checkout_date, due_date, status)
        VALUES (?, ?, ?, ?, 'checked_out')
        """
        params = (book_id, patron_id, checkout_date, due_date)
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            checkout_id = cursor.lastrowid
            cursor.close()
            return checkout_id
        except sqlite3.Error as e:
            print(f"Error checking out book: {e}")
            return None
    
    def checkin_book(self, book_id, patron_id):
        """Update checkout status to 'returned'"""
        query = """
        UPDATE Checkouts
        SET status = 'returned'
        WHERE book_id = ? AND patron_id = ? AND status = 'checked_out'
        """
        params = (book_id, patron_id)
        
        result = self.execute_query(query, params)
        return result is not None and result > 0
    
    def get_user_checkouts(self, patron_id, active_only=True):
        """Get all checkouts for a specific user"""
        if active_only:
            query = """
            SELECT c.checkout_id, c.book_id, c.patron_id, c.checkout_date, c.due_date, c.status,
                   b.title, b.author, b.genre, b.isbn
            FROM Checkouts c
            JOIN Books b ON c.book_id = b.book_id
            WHERE c.patron_id = ? AND c.status = 'checked_out'
            ORDER BY c.due_date
            """
        else:
            query = """
            SELECT c.checkout_id, c.book_id, c.patron_id, c.checkout_date, c.due_date, c.status,
                   b.title, b.author, b.genre, b.isbn
            FROM Checkouts c
            JOIN Books b ON c.book_id = b.book_id
            WHERE c.patron_id = ?
            ORDER BY c.checkout_date DESC
            """
        
        return self.execute_query(query, (patron_id,))