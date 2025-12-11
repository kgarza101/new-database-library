import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
from pathlib import Path
import os


class LoginSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Library System - Login")
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        
        self.db_file = "usercred.db"
        self.connection = None
        self.current_user = None
        self.is_admin = False
        
        if not self.connect_db():
            self.root.destroy()
            return
        
        self.create_login_ui()
    
    def connect_db(self):
        try:
            db_path = Path(self.db_file).resolve()
            
            if not db_path.exists():
                messagebox.showerror(
                    "Database Error", 
                    f"Database file '{self.db_file}' not found.\n\n"
                )
                return False
            
            self.connection = sqlite3.connect(str(db_path))
                        
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            table_exists = cursor.fetchone()
            
            if not table_exists:
                messagebox.showerror(
                    "Database Error", 
                )
                cursor.close()
                return False
            
            cursor.execute("PRAGMA table_info(users)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            required_columns = ['username', 'password', 'is_admin']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                messagebox.showerror(
                    "Database Error",
                    f"Users table is missing required columns: {', '.join(missing_columns)}"
                )
                cursor.close()
                return False
            
            cursor.close()
            return True
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error connecting to database:\n{e}")
            print(f"SQLite Error: {e}")
            return False
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error:\n{e}")
            print(f"Unexpected Error: {e}")
            return False
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_login_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="Library System",
            font=("Arial", 22, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=25)
        
        content_frame = tk.Frame(self.root, bg="#ecf0f1")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        tk.Label(
            content_frame,
            text="Login",
            font=("Arial", 18, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(pady=(0, 20))
        
        tk.Label(
            content_frame,
            text="Username:",
            font=("Arial", 11),
            bg="#ecf0f1"
        ).pack(anchor=tk.W, pady=(10, 5))
        
        self.login_username_entry = tk.Entry(
            content_frame,
            width=35,
            font=("Arial", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.login_username_entry.pack(pady=(0, 15))
        
        tk.Label(
            content_frame,
            text="Password:",
            font=("Arial", 11),
            bg="#ecf0f1"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.login_password_entry = tk.Entry(
            content_frame,
            width=35,
            font=("Arial", 11),
            show="*",
            relief=tk.SOLID,
            borderwidth=1
        )
        self.login_password_entry.pack(pady=(0, 25))
        
        tk.Button(
            content_frame,
            text="Login",
            command=self.login,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 12, "bold"),
            width=25,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT
        ).pack(pady=5)
        
        tk.Button(
            content_frame,
            text="Register New Account",
            command=self.create_register_ui,
            bg="#3498db",
            fg="white",
            font=("Arial", 12, "bold"),
            width=25,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT
        ).pack(pady=5)
        
        self.login_username_entry.bind('<Return>', lambda e: self.login())
        self.login_password_entry.bind('<Return>', lambda e: self.login())
        
        self.login_username_entry.focus_set()
    
    def create_register_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame,
            text="Library System",
            font=("Arial", 22, "bold"),
            bg="#2c3e50",
            fg="white"
        ).pack(pady=25)
        
        content_frame = tk.Frame(self.root, bg="#ecf0f1")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        tk.Label(
            content_frame,
            text="Register New Account",
            font=("Arial", 18, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(pady=(0, 20))
        
        tk.Label(
            content_frame,
            text="Username:",
            font=("Arial", 11),
            bg="#ecf0f1"
        ).pack(anchor=tk.W, pady=(10, 5))
        
        self.register_username_entry = tk.Entry(
            content_frame,
            width=35,
            font=("Arial", 11),
            relief=tk.SOLID,
            borderwidth=1
        )
        self.register_username_entry.pack(pady=(0, 15))
        
        tk.Label(
            content_frame,
            text="Password:",
            font=("Arial", 11),
            bg="#ecf0f1"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.register_password_entry = tk.Entry(
            content_frame,
            width=35,
            font=("Arial", 11),
            show="*",
            relief=tk.SOLID,
            borderwidth=1
        )
        self.register_password_entry.pack(pady=(0, 15))
        
        tk.Label(
            content_frame,
            text="Confirm Password:",
            font=("Arial", 11),
            bg="#ecf0f1"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.register_confirm_password_entry = tk.Entry(
            content_frame,
            width=35,
            font=("Arial", 11),
            show="*",
            relief=tk.SOLID,
            borderwidth=1
        )
        self.register_confirm_password_entry.pack(pady=(0, 20))
        
        self.is_admin_var = tk.IntVar(value=0)
        admin_checkbox = tk.Checkbutton(
            content_frame,
            text="Register as Administrator",
            variable=self.is_admin_var,
            font=("Arial", 11),
            bg="#ecf0f1",
            activebackground="#ecf0f1",
            cursor="hand2"
        )
        admin_checkbox.pack(pady=(0, 20))
        
        tk.Button(
            content_frame,
            text="Register",
            command=self.register,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 12, "bold"),
            width=25,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT
        ).pack(pady=5)
        
        tk.Button(
            content_frame,
            text="Back to Login",
            command=self.create_login_ui,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 12, "bold"),
            width=25,
            pady=8,
            cursor="hand2",
            relief=tk.FLAT
        ).pack(pady=5)
        
        self.register_username_entry.focus_set()
    
    def login(self):
        if not self.connection:
            messagebox.showerror("Error", "Database connection is not available.")
            return
        
        username = self.login_username_entry.get().strip()
        password = self.login_password_entry.get()
        
        if not username or not password:
            messagebox.showwarning("Missing Information", "Please enter both username and password.")
            return
        
        try:
            cursor = self.connection.cursor()
            hashed_password = self.hash_password(password)
            
            cursor.execute(
                "SELECT username, is_admin FROM users WHERE username=? AND password=?",
                (username, hashed_password)
            )
            
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                self.current_user = result[0]
                self.is_admin = bool(result[1])
                
                admin_status = "Administrator" if self.is_admin else "User"
                messagebox.showinfo(
                    "Login Successful",
                    f"Welcome, {self.current_user}!\nStatus: {admin_status}"
                )
                
                self.open_library_app()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")
                self.login_password_entry.delete(0, tk.END)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error during login: {e}")
    
    def register(self):
        if not self.connection:
            messagebox.showerror("Error", "Database connection is not available.")
            return
        
        username = self.register_username_entry.get().strip()
        password = self.register_password_entry.get()
        confirm_password = self.register_confirm_password_entry.get()
        is_admin = self.is_admin_var.get()
        
        if not username or not password:
            messagebox.showwarning("Missing Information", "Please enter both username and password.")
            return
        
        if len(username) < 3:
            messagebox.showwarning("Invalid Username", "Username must be at least 3 characters long.")
            return
        
        if len(password) < 6:
            messagebox.showwarning("Invalid Password", "Password must be at least 6 characters long.")
            return
        
        if password != confirm_password:
            messagebox.showerror("Password Mismatch", "Passwords do not match.")
            return
        
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT username FROM users WHERE username=?", (username,))
            if cursor.fetchone():
                messagebox.showerror("Registration Failed", "Username already exists.")
                cursor.close()
                return
            
            hashed_password = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                (username, hashed_password, is_admin)
            )
            
            self.connection.commit()
            cursor.close()
            
            admin_status = "Administrator" if is_admin else "Regular User"
            messagebox.showinfo(
                "Registration Successful",
                f"Account created successfully!\nUsername: {username}\nStatus: {admin_status}"
            )
            
            self.create_login_ui()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error during registration: {e}")
    
    def open_library_app(self):
        self.root.withdraw()
        
        try:
            from library_app import LibraryBookApp
            library_root = tk.Toplevel(self.root)
            
            app = LibraryBookApp(
                library_root,
                login_window = self.root,
                current_user = self.current_user,
                is_admin = self.is_admin
            )
            
            def on_library_close():
                library_root.destroy()
                self.root.deiconify()
                self.login_username_entry.delete(0, tk.END)
                self.login_password_entry.delete(0, tk.END)
                self.current_user = None 
                self.is_admin = False
            
            library_root.protocol("WM_DELETE_WINDOW", on_library_close)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open library application: {e}")
            self.root.deiconify()
    
    def __del__(self):
        if self.connection:
            self.connection.close()


if __name__ == "__main__":
    root = tk.Tk()
    login_app = LoginSystem(root)
    root.mainloop()