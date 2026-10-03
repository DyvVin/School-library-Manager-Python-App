import tkinter as tk
import design
from tkinter import ttk, messagebox

class ReadersTab(ttk.Frame):
    def __init__(self, parent, db, on_change=None):
        super().__init__(parent, style='App.TFrame')
        self.db = db
        self.on_change = on_change
        self._build_ui()

    def _build_ui(self):
        controls_frame = ttk.Frame(self, style='App.TFrame')
        controls_frame.grid(row=0, column=0, columnspan=4, sticky='ew', padx=5, pady=5)
        controls_frame.columnconfigure(1, weight=1)

        ttk.Label(controls_frame, text='Имя:', style='App.TLabel').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.name_entry = ttk.Entry(controls_frame, style='App.TEntry')
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(controls_frame, text='Фамилия:', style='App.TLabel').grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.surname_entry = ttk.Entry(controls_frame, style='App.TEntry')
        self.surname_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(controls_frame, text='Отчество:', style='App.TLabel').grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.patronymic_entry = ttk.Entry(controls_frame, style='App.TEntry')
        self.patronymic_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(controls_frame, text='Класс:', style='App.TLabel').grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.class_combobox = ttk.Combobox(controls_frame, state='readonly', style='App.TCombobox')
        self.class_combobox.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        add_reader_btn = design.create_button(controls_frame, text='Добавить читателя', command=self.add_reader)
        add_reader_btn.grid(row=4, column=0, columnspan=2, pady=10, sticky='ew')

        delete_reader_btn = design.create_button(controls_frame, text='Удалить читателя', command=self.delete_reader)
        delete_reader_btn.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky='ew')

        ttk.Label(controls_frame, text='Поиск:', style='App.TLabel').grid(row=6, column=0, padx=5, pady=5, sticky='w')
        self.search_entry = ttk.Entry(controls_frame, style='App.TEntry')
        self.search_entry.grid(row=6, column=1, padx=5, pady=5, sticky='ew')

        search_btn = design.create_button(controls_frame, text='Найти', command=self.search_readers)
        search_btn.grid(row=7, column=0, padx=5, pady=5, sticky='ew')
        clear_btn = design.create_button(controls_frame, text='Сбросить', command=self.clear_search)
        clear_btn.grid(row=7, column=1, padx=5, pady=5, sticky='ew')

        self.reader_tree = ttk.Treeview(
            self,
            style='App.Treeview',
            columns=('ID', 'Имя', 'Фамилия', 'Отчество', 'Класс'),
            show='headings',
            selectmode='browse'
        )
        self.reader_tree.heading('ID', text='ID')
        self.reader_tree.heading('Имя', text='Имя')
        self.reader_tree.heading('Фамилия', text='Фамилия')
        self.reader_tree.heading('Отчество', text='Отчество')
        self.reader_tree.heading('Класс', text='Класс')

        # Fixed reader tree column widths. Изменять здесь.
        # ID не растягивается, остальные распределяют оставшееся место равномерно
        self.reader_tree.column('ID', width=60, minwidth=50, anchor='center', stretch=False)
        self.reader_tree.column('Имя', width=150, minwidth=130, stretch=True)
        self.reader_tree.column('Фамилия', width=150, minwidth=130, stretch=True)
        self.reader_tree.column('Отчество', width=150, minwidth=130, stretch=True)
        self.reader_tree.column('Класс', width=120, minwidth=110, stretch=True)

        self.reader_tree.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky='nsew')

        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.reader_tree.yview, style='App.TScrollbar')
        scrollbar.grid(row=1, column=4, sticky='ns')
        self.reader_tree.configure(yscrollcommand=scrollbar.set)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

    def add_reader(self):
        name = self.name_entry.get().strip()
        patronymic = self.patronymic_entry.get().strip()
        surname = self.surname_entry.get().strip()
        class_name = self.class_combobox.get().strip()

        if not name or not surname:
            messagebox.showerror('Ошибка', 'Имя и фамилия обязательны')
            return

        try:
            self.db.add_reader(name, patronymic, surname, class_name if class_name else None)
            self.update_reader_tree()
            self.name_entry.delete(0, tk.END)
            self.patronymic_entry.delete(0, tk.END)
            self.surname_entry.delete(0, tk.END)
            self.class_combobox.set('')
            if self.on_change:
                self.on_change()
        except Exception as exc:
            messagebox.showerror('Ошибка', str(exc))

    def update_reader_tree(self, query=None):
        for row in self.reader_tree.get_children():
            self.reader_tree.delete(row)
        rows = self.db.search_readers(query) if query else self.db.get_readers()
        for row in rows:
            self.reader_tree.insert('', 'end', values=row)
        # refresh classes list
        try:
            self.class_combobox['values'] = self.db.get_classes()
        except Exception:
            self.class_combobox['values'] = []

    def search_readers(self):
        query = self.search_entry.get().strip()
        self.update_reader_tree(query)

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.update_reader_tree()

    def delete_reader(self):
        selected = self.reader_tree.selection()
        if not selected:
            messagebox.showerror('Ошибка', 'Выберите читателя для удаления')
            return

        try:
            reader_id = int(self.reader_tree.item(selected[0])['values'][0])
            self.db.delete_reader(reader_id)
            self.update_reader_tree()
            if self.on_change:
                self.on_change()
        except (TypeError, ValueError):
            messagebox.showerror('Ошибка', 'Неверный ID читателя')
        except Exception as exc:
            messagebox.showerror('Ошибка', str(exc))
