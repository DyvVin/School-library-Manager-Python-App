import tkinter as tk
import design
from tkinter import ttk, messagebox

class CopiesTab(ttk.Frame):
    def __init__(self, parent, db, on_change=None):
        super().__init__(parent, style='App.TFrame')
        self.db = db
        self.on_change = on_change
        self._build_ui()

    def _build_ui(self):
        controls_frame = ttk.Frame(self, style='App.TFrame')
        controls_frame.grid(row=0, column=0, columnspan=5, sticky='ew', padx=5, pady=5)
        controls_frame.columnconfigure(1, weight=1)

        ttk.Label(controls_frame, text='ISBN книги:', style='App.TLabel').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.book_isbn_combobox = design.SearchableCombobox(controls_frame, style='App.TCombobox')
        self.book_isbn_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(controls_frame, text='Состояние:', style='App.TLabel').grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.condition_combobox = ttk.Combobox(controls_frame, state='readonly', style='App.TCombobox')
        self.condition_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        add_copy_btn = design.create_button(controls_frame, text='Добавить экземпляр', command=self.add_copy)
        add_copy_btn.grid(row=2, column=0, columnspan=2, pady=5, sticky='ew')

        delete_copy_btn = design.create_button(controls_frame, text='Удалить экземпляр', command=self.delete_copy)
        delete_copy_btn.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        self.copy_tree = ttk.Treeview(
            self,
            style='App.Treeview',
            columns=('ID', 'ISBN', 'Название', 'Состояние'),
            show='headings',
            selectmode='browse'
        )
        self.copy_tree.heading('ID', text='ID')
        self.copy_tree.heading('ISBN', text='ISBN')
        self.copy_tree.heading('Название', text='Название')
        self.copy_tree.heading('Состояние', text='Состояние')

        # Fixed copy tree column widths. Изменять здесь.
        # ID не растягивается, остальные распределяют оставшееся место
        self.copy_tree.column('ID', width=60, minwidth=50, anchor='center', stretch=False)
        self.copy_tree.column('ISBN', width=160, minwidth=120, stretch=True)
        self.copy_tree.column('Название', width=340, minwidth=250, stretch=True)
        self.copy_tree.column('Состояние', width=120, minwidth=100, stretch=True)

        self.copy_tree.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky='nsew')

        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.copy_tree.yview, style='App.TScrollbar')
        scrollbar.grid(row=1, column=5, sticky='ns')
        self.copy_tree.configure(yscrollcommand=scrollbar.set)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.refresh()

    def refresh(self):
        # load book ISBN options
        try:
            self.book_isbn_combobox.set_completion_list(self.db.get_book_options())
        except Exception:
            self.book_isbn_combobox.set_completion_list([])
        self.book_isbn_combobox.set('')

        # load conditions
        try:
            self.condition_combobox['values'] = self.db.get_conditions()
        except Exception:
            self.condition_combobox['values'] = []
        self.condition_combobox.set('')

        # load copies
        for row in self.copy_tree.get_children():
            self.copy_tree.delete(row)
        try:
            rows = self.db.fetchall(
                'SELECT c.id_copy, b.isbn, b.title, co.name FROM copy c '
                'JOIN book b ON c.id_book = b.id_book '
                'JOIN [condition] co ON c.id_condition = co.id_condition '
                'ORDER BY c.id_copy DESC'
            )
            for r in rows:
                self.copy_tree.insert('', 'end', values=(r[0], r[1], r[2], r[3]))
        except Exception:
            pass

    def add_copy(self):
        book_selection = self.book_isbn_combobox.get().strip()
        condition = self.condition_combobox.get().strip()
        if not book_selection or not condition:
            messagebox.showerror('Ошибка', 'ISBN книги и состояние обязательны')
            return
        # Извлечение только ISBN из выбранного значения "ISBN - Название"
        book_isbn = book_selection.split(' - ')[0].strip() if ' - ' in book_selection else book_selection
        try:
            self.db.add_copy(book_isbn, condition)
            self.book_isbn_combobox.set('')
            if self.on_change:
                self.on_change()
            self.refresh()
        except Exception as exc:
            messagebox.showerror('Ошибка', str(exc))

    def delete_copy(self):
        selected = self.copy_tree.selection()
        if not selected:
            messagebox.showerror('Ошибка', 'Выберите экземпляр для удаления')
            return
        try:
            copy_id = int(self.copy_tree.item(selected[0])['values'][0])
            self.db.execute('DELETE FROM loan WHERE id_copy = ?', (copy_id,))
            self.db.execute('DELETE FROM copy WHERE id_copy = ?', (copy_id,))
            self.db.conn.commit()
            if self.on_change:
                self.on_change()
            self.refresh()
        except Exception as exc:
            messagebox.showerror('Ошибка', str(exc))
