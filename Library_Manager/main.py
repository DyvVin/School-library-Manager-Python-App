import tkinter as tk
from tkinter import ttk, messagebox

import design
from db import Database
from books import BooksTab
from copies import CopiesTab
from readers import ReadersTab
from loans import LoansTab

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Учет книжного фонда')
        self.root.geometry('1100x800')
        #icon = tk.PhotoImage(file='resources/icon.png')
        #self.root.iconphoto(True, icon)
        design.apply_design(root)

        server_name = r'DESKTOP-B6V1SLP\SQLEXPRESS01'
        database_name = 'library_db'

        try:
            self.db = Database(server_name, database_name)
        except Exception as exc:
            messagebox.showerror('Ошибка подключения', str(exc))
            root.destroy()
            return

        self.notebook = ttk.Notebook(root, style='App.TNotebook')
        self.notebook.pack(fill='both', expand=True)

        

        self.books_frame = ttk.Frame(self.notebook, style='App.TFrame')
        self.readers_frame = ttk.Frame(self.notebook, style='App.TFrame')
        self.loans_frame = ttk.Frame(self.notebook, style='App.TFrame')

        self.notebook.add(self.books_frame, text='Книги')
        self.copies_frame = ttk.Frame(self.notebook, style='App.TFrame')
        self.notebook.add(self.copies_frame, text='Экземпляры')
        self.notebook.add(self.readers_frame, text='Читатели')
        self.notebook.add(self.loans_frame, text='Выдачи')

        self.books_tab = BooksTab(self.books_frame, self.db, on_change=self.refresh_all)
        self.books_tab.pack(fill='both', expand=True)

        self.copies_tab = CopiesTab(self.copies_frame, self.db, on_change=self.refresh_all)
        self.copies_tab.pack(fill='both', expand=True)

        self.readers_tab = ReadersTab(self.readers_frame, self.db, on_change=self.refresh_all)
        self.readers_tab.pack(fill='both', expand=True)

        self.loans_tab = LoansTab(self.loans_frame, self.db, on_change=self.refresh_all)
        self.loans_tab.pack(fill='both', expand=True)

        self.refresh_all()

    def refresh_all(self):
        self.books_tab.update_book_tree()
        self.readers_tab.update_reader_tree()
        self.loans_tab.refresh()

if __name__ == '__main__':
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()
