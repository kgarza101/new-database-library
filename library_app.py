import tkinter as tk
from tkinter import ttk, messagebox
from database import DatabaseConnection

class LibraryBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Book Records")
        self.root.geometry("900x600")
        
        # Database connection
        self.db = DatabaseConnection("library.db")
        if not self.db.connect():
            messagebox.showerror("Database Error", 
                               "Failed to connect to database.\n\n")
            self.root.destroy()
            return
        
        self.widgets()
        
        self.load_books()
        
        self.tree.bind('<Double-Button-1>', self.on_book_double_click)
        
    def widgets(self):
        # Title label
        title_label = tk.Label(
            self.root,
            text="Library Book Records",
            font=("Arial", 20, "bold"),
            pady=20,
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(fill=tk.X)
        
        search_frame = tk.Frame(self.root, pady=15, bg="#ecf0f1")
        search_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(
            search_frame,
            text="Search:",
            font=("Arial", 11),
            bg="#ecf0f1"
        ).pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.search_books())
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=35,
            font=("Arial", 10)
        )
        search_entry.pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        button_frame = tk.Frame(search_frame, bg="#ecf0f1")
        button_frame.pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="Add Book",
            command=self.add_book_dialog,
            bg="#2ecc71",
            fg="white",
            padx=15,
            pady=5,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Edit Book",
            command=self.edit_book_dialog,
            bg="#f39c12",
            fg="white",
            padx=15,
            pady=5,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Delete Book",
            command=self.delete_book,
            bg="#e74c3c",
            fg="white",
            padx=15,
            pady=5,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Refresh",
            command=self.load_books,
            bg="#3498db",
            fg="white",
            padx=15,
            pady=5,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            search_frame, 
            text="Clear Search", 
            command=self.clear_search,
            bg="#95a5a6",
            fg="white",
            padx=15,
            pady=5,
            font=("Arial", 10, "bold"),
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        # Treeview frame
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
       
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                       background="#ffffff",
                       foreground="black",
                       rowheight=25,
                       fieldbackground="#ffffff",
                       font=("Arial", 10))
        style.map("Treeview", background=[("selected", "#3498db")])
        style.configure("Treeview.Heading",
                        font=("Arial", 11, "bold"),
                        background="#34495e",
                        foreground="white")
        
        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("BookID", "Title", "Author", "Genre", "ISBN"),
            show="headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Column headings
        self.tree.heading("BookID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Genre", text="Genre")
        self.tree.heading("ISBN", text="ISBN")
        
        # Column widths
        self.tree.column("BookID", width=50, anchor=tk.CENTER)
        self.tree.column("Title", width=350, anchor=tk.W)
        self.tree.column("Author", width=250, anchor=tk.W)
        self.tree.column("Genre", width=150, anchor=tk.W)
        self.tree.column("ISBN", width=150, anchor=tk.W)
        
        # Colors
        self.tree.tag_configure("oddrow", background="#f8f9fa")
        self.tree.tag_configure("evenrow", background="#ffffff")
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        # Status
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg="#ecf0f1",
            font=("Arial", 9)
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_books(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            books = self.db.get_all_books()
            
            if books:
                for index, book in enumerate(books):
                    tag = "evenrow" if index % 2 == 0 else "oddrow"
                    self.tree.insert("", tk.END, values=book, tags=(tag,))
                
                self.status_label.config(text=f"Loaded {len(books)} books")
            else:
                self.status_label.config(text="No books found in database")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading books: {e}")
            self.status_label.config(text="Error loading books")
    
    def search_books(self):
        
        search_term = self.search_var.get().strip()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_term:
            self.load_books()
            return
        
        try:
            books = self.db.search_books(search_term)
            
            if books:
                for index, book in enumerate(books):
                    tag = "evenrow" if index % 2 == 0 else "oddrow"
                    self.tree.insert("", tk.END, values=book, tags=(tag,))
            
            self.status_label.config(text=f"Found {len(books)} books matching '{search_term}'")
            
        except Exception as e:
            messagebox.showerror("Database Error", f"Error searching for books: {e}")
            self.status_label.config(text="Error searching for books")
    
    def clear_search(self):
        self.search_var.set("")
        self.load_books()
    
    def add_book_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Book")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(dialog, text="Title:", font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        title_entry = tk.Entry(dialog, width=40, font=("Arial", 10))
        title_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Author:", font=("Arial", 11)).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        author_entry = tk.Entry(dialog, width=40, font=("Arial", 10))
        author_entry.grid(row=1, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Genre:", font=("Arial", 11)).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        genre_entry = tk.Entry(dialog, width=40, font=("Arial", 10))
        genre_entry.grid(row=2, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="ISBN:", font=("Arial", 11)).grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        isbn_entry = tk.Entry(dialog, width=40, font=("Arial", 10))
        isbn_entry.grid(row=3, column=1, padx=10, pady=10)
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        def save_book():
            title = title_entry.get().strip()
            author = author_entry.get().strip()
            genre = genre_entry.get().strip()
            isbn = isbn_entry.get().strip()
            
            if not title or not author:
                messagebox.showwarning("Missing Information", "Title and Author are required.")
                return
            
            book_id = self.db.add_book(title, author, genre, isbn if isbn else None)
            if book_id:
                messagebox.showinfo("Success", f"Book added successfully!")
                dialog.destroy()
                self.load_books()
            else:
                messagebox.showerror("Error", "Failed to add book. Please try again.")
        
        tk.Button(button_frame, text="Save", command=save_book, 
                 bg="#2ecc71", fg="white", padx=20, pady=5).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                 bg="#95a5a6", fg="white", padx=20, pady=5).pack(side=tk.LEFT, padx=10)
        
        title_entry.focus_set()
    
    def edit_book_dialog(self):
        """Edit selected book"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a book to edit")
            return
        
        item = self.tree.item(selected_item[0])
        book_id, old_title, old_author, old_genre, old_isbn = item['values']
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Book: {old_title}")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        tk.Label(dialog, text="Title:", font=("Arial", 11)).grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        title_entry = tk.Entry(dialog, width=40, font=("Arial", 10))
        title_entry.grid(row=0, column=1, padx=10, pady=10)
        title_entry.insert(0, old_title)
        
        tk.Label(dialog, text="Author:", font=("Arial", 11)).grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        author_entry = tk.Entry(dialog, width=40, font=("Arial", 10))
        author_entry.grid(row=1, column=1, padx=10, pady=10)
        author_entry.insert(0, old_author)
        
        tk.Label(dialog, text="Genre:", font=("Arial", 11)).grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
        genre_entry = tk.Entry(dialog, width=40, font=("Arial", 10))
        genre_entry.grid(row=2, column=1, padx=10, pady=10)
        genre_entry.insert(0, old_genre)
        
        tk.Label(dialog, text="ISBN:", font=("Arial", 11)).grid(row=3, column=0, padx=10, pady=10, sticky=tk.W)
        isbn_entry = tk.Entry(dialog, width=40, font=("Arial", 10))
        isbn_entry.grid(row=3, column=1, padx=10, pady=10)
        isbn_entry.insert(0, old_isbn)
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        def update_book():
            title = title_entry.get().strip()
            author = author_entry.get().strip()
            genre = genre_entry.get().strip()
            isbn = isbn_entry.get().strip()
            
            if not title or not author:
                messagebox.showwarning("Missing Information", "Title and Author are required!")
                return
            
            if self.db.update_book(book_id, title, author, genre, isbn if isbn else None):
                messagebox.showinfo("Success", "Book updated successfully!")
                dialog.destroy()
                self.load_books()
            else:
                messagebox.showerror("Error", "Failed to update book. Please try again.")
        
        tk.Button(button_frame, text="Update", command=update_book,
                 bg="#f39c12", fg="white", padx=20, pady=5).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                 bg="#95a5a6", fg="white", padx=20, pady=5).pack(side=tk.LEFT, padx=10)
        
        title_entry.focus_set()
    
    def delete_book(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a book to delete")
            return
        
        item = self.tree.item(selected_item[0])
        book_id, title, author = item['values'][0], item['values'][1], item['values'][2]
        
        # Confirm deletion
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete '{title}' by {author}?"):
            if self.db.delete_book(book_id):
                messagebox.showinfo("Success", f"Book '{title}' deleted successfully")
                self.load_books()
            else:
                messagebox.showerror("Error", "Failed to delete book")
    
    def on_book_double_click(self, event):
        item = self.tree.selection()
        if item:
            self.edit_book_dialog()

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryBookApp(root)
    root.mainloop()