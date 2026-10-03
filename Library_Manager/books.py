import tkinter as tk
import design
from tkinter import ttk, messagebox

class BooksTab(ttk.Frame):
    def __init__(self, parent, db, on_change=None):
        super().__init__(parent, style='App.TFrame')
        self.db = db
        self.on_change = on_change
        self._build_ui()

    def _build_ui(self):
        controls_frame = ttk.Frame(self, style='App.TFrame')
        controls_frame.grid(row=0, column=0, columnspan=5, sticky='ew', padx=5, pady=5)
        controls_frame.columnconfigure(1, weight=1)

        ttk.Label(controls_frame, text='ISBN:', style='App.TLabel').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.isbn_entry = ttk.Entry(controls_frame, style='App.TEntry')
        self.isbn_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(controls_frame, text='Название:', style='App.TLabel').grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.title_entry = ttk.Entry(controls_frame, style='App.TEntry')
        self.title_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(controls_frame, text='Автор:', style='App.TLabel').grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.author_entry = ttk.Entry(controls_frame, style='App.TEntry')
        self.author_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(controls_frame, text='Год:', style='App.TLabel').grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.year_entry = ttk.Entry(controls_frame, style='App.TEntry')
        self.year_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        add_book_btn = design.create_button(controls_frame, text='Добавить книгу', command=self.add_book)
        add_book_btn.grid(row=4, column=0, columnspan=2, pady=10, sticky='ew')

        delete_book_btn = design.create_button(controls_frame, text='Удалить книгу', command=self.delete_book)
        delete_book_btn.grid(row=5, column=0, columnspan=2, pady=5, sticky='ew')

        ttk.Label(controls_frame, text='Поиск:', style='App.TLabel').grid(row=6, column=0, padx=5, pady=5, sticky='w')
        self.search_entry = ttk.Entry(controls_frame, style='App.TEntry')
        self.search_entry.grid(row=6, column=1, padx=5, pady=5, sticky='ew')

        search_btn = design.create_button(controls_frame, text='Найти', command=self.search_books)
        search_btn.grid(row=7, column=0, padx=5, pady=5, sticky='ew')
        clear_btn = design.create_button(controls_frame, text='Сбросить', command=self.clear_search)
        clear_btn.grid(row=7, column=1, padx=5, pady=5, sticky='ew')

        self.book_tree = ttk.Treeview(
            self,
            style='App.Treeview',
            columns=('ID', 'ISBN', 'Название', 'Автор', 'Год'),
            show='headings',
            selectmode='browse'
        )
        self.book_tree.heading('ID', text='ID')
        self.book_tree.heading('ISBN', text='ISBN')
        self.book_tree.heading('Название', text='Название')
        self.book_tree.heading('Автор', text='Автор')
        self.book_tree.heading('Год', text='Год')

        # Fixed book tree column widths. Изменять здесь.
        # ID не растягивается, остальные распределяют оставшееся место пропорционально
        self.book_tree.column('ID', width=60, minwidth=50, anchor='center', stretch=False)
        self.book_tree.column('ISBN', width=150, minwidth=120, stretch=True)
        self.book_tree.column('Название', width=320, minwidth=250, stretch=True)
        self.book_tree.column('Автор', width=180, minwidth=150, stretch=True)
        self.book_tree.column('Год', width=80, minwidth=70, anchor='center', stretch=True)

        self.book_tree.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky='nsew')

        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.book_tree.yview, style='App.TScrollbar')
        scrollbar.grid(row=1, column=5, sticky='ns')
        self.book_tree.configure(yscrollcommand=scrollbar.set)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def search_books(self):
        query = self.search_entry.get().strip()
        self.update_book_tree(query)

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.update_book_tree()

    def add_book(self):
        isbn = self.isbn_entry.get().strip()
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        year = self.year_entry.get().strip()
        if not (isbn and title and author and year):
            messagebox.showerror('Ошибка', 'Все поля должны быть заполнены')
            return

        try:
            self.db.add_book(isbn, title, author, year)
            self.update_book_tree()
            self.clear_book_entries()
            if self.on_change:
                self.on_change()
        except Exception as exc:
            messagebox.showerror('Ошибка', str(exc))

    def delete_book(self):
        selected = self.book_tree.selection()
        if not selected:
            messagebox.showerror('Ошибка', 'Выберите книгу для удаления')
            return

        try:
            book_id = int(self.book_tree.item(selected[0])['values'][0])
            self.db.delete_book(book_id)
            self.update_book_tree()
            if self.on_change:
                self.on_change()
        except (TypeError, ValueError):
            messagebox.showerror('Ошибка', 'Неверный ID книги')
        except Exception as exc:
            messagebox.showerror('Ошибка', str(exc))

    def update_book_tree(self, query=None):
        for row in self.book_tree.get_children():
            self.book_tree.delete(row)
        rows = self.db.search_books(query) if query else self.db.get_books()
        for row in rows:
            self.book_tree.insert('', 'end', values=row)

    def clear_book_entries(self):
        self.isbn_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        # section removed
    
