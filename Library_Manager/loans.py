import tkinter as tk
import design
from tkinter import ttk, messagebox
from datetime import date

class LoansTab(ttk.Frame):
    def __init__(self, parent, db, on_change=None):
        super().__init__(parent, style='App.TFrame')
        self.db = db
        self.on_change = on_change
        self._build_ui()

    def _build_ui(self):
        controls_frame = ttk.Frame(self, style='App.TFrame')
        controls_frame.grid(row=0, column=0, columnspan=5, sticky='ew', padx=5, pady=5)
        controls_frame.columnconfigure(1, weight=1)


        ttk.Label(controls_frame, text='Читатель:', style='App.TLabel').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.reader_combobox = design.SearchableCombobox(controls_frame, style='App.TCombobox')
        self.reader_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        ttk.Label(controls_frame, text='Экземпляр:', style='App.TLabel').grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.copy_combobox = design.SearchableCombobox(controls_frame, style='App.TCombobox')
        self.copy_combobox.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        issue_btn = design.create_button(controls_frame, text='Выдать книгу', command=self.issue_book)
        issue_btn.grid(row=2, column=0, columnspan=2, pady=5, sticky='ew')

        ttk.Label(controls_frame, text='ID выдачи:', style='App.TLabel').grid(row=3, column=0, padx=5, pady=5, sticky='w')
        self.loan_id_entry = ttk.Entry(controls_frame, style='App.TEntry')
        self.loan_id_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')

        return_btn = design.create_button(controls_frame, text='Вернуть книгу', command=self.return_book)
        return_btn.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        delete_loan_btn = design.create_button(controls_frame, text='Удалить выдачу', command=self.delete_loan)
        delete_loan_btn.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky='ew')

        self.loan_tree = ttk.Treeview(
            self,
            style='App.Treeview',
            columns=('ID', 'ID читателя', 'ID экземпляра', 'Дата выдачи', 'Выдано до', 'Дата возврата', 'Статус'),
            show='headings',
            selectmode='browse'
        )
        self.loan_tree.heading('ID', text='ID')
        self.loan_tree.heading('ID читателя', text='ID читателя')
        self.loan_tree.heading('ID экземпляра', text='ID экземпляра')
        self.loan_tree.heading('Дата выдачи', text='Дата выдачи')
        self.loan_tree.heading('Выдано до', text='Выдано до')
        self.loan_tree.heading('Дата возврата', text='Дата возврата')
        self.loan_tree.heading('Статус', text='Статус')

        # Fixed loan tree column widths. Изменять здесь.
        # ID столбцы не растягиваются, дата и статус распределяют оставшееся место
        self.loan_tree.column('ID', width=50, minwidth=45, anchor='center', stretch=False)
        self.loan_tree.column('ID читателя', width=90, minwidth=80, anchor='center', stretch=False)
        self.loan_tree.column('ID экземпляра', width=90, minwidth=80, anchor='center', stretch=False)
        self.loan_tree.column('Дата выдачи', width=110, minwidth=100, stretch=True)
        self.loan_tree.column('Выдано до', width=110, minwidth=100, stretch=True)
        self.loan_tree.column('Дата возврата', width=110, minwidth=100, stretch=True)
        self.loan_tree.column('Статус', width=110, minwidth=100, stretch=True)

        self.loan_tree.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky='nsew')

        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.loan_tree.yview, style='App.TScrollbar')
        scrollbar.grid(row=1, column=5, sticky='ns')
        self.loan_tree.configure(yscrollcommand=scrollbar.set)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        extend_frame = ttk.Frame(self, style='App.TFrame')
        extend_frame.grid(row=2, column=0, columnspan=5, sticky='ew', padx=5, pady=5)
        extend_frame.columnconfigure(1, weight=1)

        ttk.Label(extend_frame, text='Продлить на (дней):', style='App.TLabel').grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.extend_combobox = ttk.Combobox(extend_frame, state='readonly', values=[10,15,20], style='App.TCombobox')
        self.extend_combobox.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        extend_btn = design.create_button(extend_frame, text='Продлить выдачу', command=self.extend_selected_loan)
        extend_btn.grid(row=0, column=2, padx=5, pady=5, sticky='w')

    def update_copy_combobox(self):
        self.copy_combobox.set_completion_list(self.db.get_available_copies())
        self.copy_combobox.set('')

    def update_reader_combobox(self):
        self.reader_combobox.set_completion_list(self.db.get_readers_for_combobox())
        self.reader_combobox.set('')

    def issue_book(self):
        selected_reader = self.reader_combobox.get().strip()
        selected_copy = self.copy_combobox.get().strip()

        if not selected_reader or not selected_copy:
            messagebox.showerror('Ошибка', 'Выберите читателя и экземпляр')
            return

        try:
            reader_id = int(selected_reader.split(' - ')[0])
            copy_id = int(selected_copy.split(' - ')[0])
            
            # Проверка статуса экземпляра
            condition_name = self.db.get_copy_condition_name(copy_id)
            if condition_name == 'На списание':
                messagebox.showerror('Ошибка', 'Экземпляр находится на списании и не может быть выдан')
                return
            
            self.db.issue_loan(reader_id, copy_id, date.today())
            self.refresh()
            if self.on_change:
                self.on_change()
        except ValueError:
            messagebox.showerror('Ошибка', 'Неверный ID читателя или экземпляра')
        except Exception as exc:
            messagebox.showerror('Ошибка', str(exc))

    def return_book(self):
        selected = self.loan_tree.selection()
        loan_id_text = self.loan_id_entry.get().strip()

        if selected:
            try:
                loan_id = int(self.loan_tree.item(selected[0])['values'][0])
            except (TypeError, ValueError):
                messagebox.showerror('Ошибка', 'Неверный ID выдачи в выбранной строке')
                return
        elif loan_id_text:
            try:
                loan_id = int(loan_id_text)
            except ValueError:
                messagebox.showerror('Ошибка', 'ID выдачи должен быть целым числом')
                return
        else:
            messagebox.showerror('Ошибка', 'Выберите выдачу или введите ID')
            return

        try:
            self.db.return_loan(loan_id, date.today())
            self.refresh()
            self.loan_id_entry.delete(0, tk.END)
            if self.on_change:
                self.on_change()
        except Exception as exc:
            messagebox.showerror('Ошибка', str(exc))

    def delete_loan(self):
        selected = self.loan_tree.selection()
        if not selected:
            messagebox.showerror('Ошибка', 'Выберите выдачу для удаления')
            return

        try:
            loan_id = int(self.loan_tree.item(selected[0])['values'][0])
            self.db.delete_loan(loan_id)
            self.refresh()
            if self.on_change:
                self.on_change()
        except (TypeError, ValueError):
            messagebox.showerror('Ошибка', 'Неверный ID выдачи')
        except Exception as exc:
            messagebox.showerror('Ошибка', str(exc))

    def update_loan_tree(self):
        for row in self.loan_tree.get_children():
            self.loan_tree.delete(row)
        for row in self.db.get_loans():
            # expected loan tuple: (id, id_reader, id_copy, start_date, due_date, return_date, status)
            self.loan_tree.insert('', 'end', values=row)

    def extend_selected_loan(self):
        selected = self.loan_tree.selection()
        if not selected:
            messagebox.showerror('Ошибка', 'Выберите выдачу для продления')
            return
        days = self.extend_combobox.get()
        if not days:
            messagebox.showerror('Ошибка', 'Выберите количество дней для продления')
            return
        try:
            loan_id = int(self.loan_tree.item(selected[0])['values'][0])
            self.db.extend_loan(loan_id, int(days))
            self.refresh()
            if self.on_change:
                self.on_change()
        except Exception as exc:
            messagebox.showerror('Ошибка', str(exc))

    def refresh(self):
        self.update_copy_combobox()
        self.update_reader_combobox()
        self.update_loan_tree()
