import pyodbc
from datetime import date, datetime, timedelta

class DatabaseError(Exception):
    pass

class Database:
    def __init__(self, server_name: str, database_name: str):
        self.server_name = server_name
        self.database_name = database_name
        self.conn = None
        self.c = None
        self._connect()
        self.create_tables()

    def _connect(self):
        temp_conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={self.server_name};'
            'DATABASE=master;'
            'Trusted_Connection=yes;',
            autocommit=True
        )
        temp_cursor = temp_conn.cursor()
        temp_cursor.execute(f"IF DB_ID(N'{self.database_name}') IS NULL CREATE DATABASE [{self.database_name}]")
        temp_cursor.close()
        temp_conn.close()

        conn_str = (
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={self.server_name};'
            f'DATABASE={self.database_name};'
            'Trusted_Connection=yes;'
        )
        self.conn = pyodbc.connect(conn_str)
        self.c = self.conn.cursor()

    def create_tables(self):
        self.c.execute('''
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'book')
        BEGIN
            CREATE TABLE book (
                id_book INT IDENTITY(1,1) PRIMARY KEY,
                isbn NVARCHAR(50),
                title NVARCHAR(255),
                author NVARCHAR(255),
                year INT
            );
        END
        ''')

        self.c.execute('''
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'condition')
        BEGIN
            CREATE TABLE [condition] (
                id_condition INT IDENTITY(1,1) PRIMARY KEY,
                name NVARCHAR(100) NOT NULL
            );
        END
        ''')

        try:
            rows = self.fetchall('SELECT COUNT(*) FROM [condition]')
            if rows and rows[0][0] == 0:
                self.execute("INSERT INTO [condition] (name) VALUES (?), (?), (?), (?)", ('Отличное','Нормальное','Плохое','На списание'))
        except Exception:
            pass

        self.c.execute('''
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'copy')
        BEGIN
            CREATE TABLE copy (
                id_copy INT IDENTITY(1,1) PRIMARY KEY,
                id_book INT,
                id_condition INT,
                CONSTRAINT FK_copy_book FOREIGN KEY (id_book) REFERENCES book(id_book),
                CONSTRAINT FK_copy_condition FOREIGN KEY (id_condition) REFERENCES [condition](id_condition)
            );
        END
        ''')

        self.c.execute('''
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'class')
        BEGIN
            CREATE TABLE [class] (
                id_class INT IDENTITY(1,1) PRIMARY KEY,
                name NVARCHAR(50) NOT NULL
            );
        END
        ''')

        try:
            rows = self.fetchall('SELECT COUNT(*) FROM [class]')
            if rows and rows[0][0] == 0:
                class_values = ('Учитель','5А','5Б','6А','6Б','7А','7Б','8А','8Б','9А','9Б','10А','11А')
                for class_name in class_values:
                    self.execute('INSERT INTO [class] (name) VALUES (?)', (class_name,))
                self.conn.commit()
        except Exception:
            pass

        self.c.execute('''
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'reader')
        BEGIN
            CREATE TABLE reader (
                id_reader INT IDENTITY(1,1) PRIMARY KEY,
                reader_name NVARCHAR(100),
                patronymic NVARCHAR(100),
                surname NVARCHAR(100),
                id_class INT NULL,
                CONSTRAINT FK_reader_class FOREIGN KEY (id_class) REFERENCES [class](id_class)
            );
        END
        ''')

        self.c.execute('''
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'loan')
        BEGIN
            CREATE TABLE loan (
                id INT IDENTITY(1,1) PRIMARY KEY,
                id_reader INT,
                id_copy INT,
                start_date DATE,
                due_date DATE,
                return_date DATE,
                status NVARCHAR(50),
                CONSTRAINT FK_loan_reader FOREIGN KEY (id_reader) REFERENCES reader(id_reader),
                CONSTRAINT FK_loan_copy FOREIGN KEY (id_copy) REFERENCES copy(id_copy)
            );
        END
        ''')
        self.conn.commit()

    def execute(self, query: str, params=None):
        if params is None:
            params = ()
        return self.c.execute(query, params)

    def fetchall(self, query: str, params=None):
        cursor = self.execute(query, params)
        return cursor.fetchall()

    @staticmethod
    def format_value(value):
        if value is None:
            return ''
        if isinstance(value, (date, datetime)):
            return value.strftime('%Y-%m-%d')
        return value

    @classmethod
    def format_row(cls, row):
        return tuple(cls.format_value(item) for item in row)

    def get_books(self):
        return [self.format_row(row) for row in self.fetchall('SELECT * FROM book ORDER BY id_book DESC')]

    def search_books(self, query):
        if not query:
            return self.get_books()
        q = f'%{query}%'
        return [self.format_row(row) for row in self.fetchall(
            'SELECT * FROM book WHERE isbn LIKE ? OR title LIKE ? OR author LIKE ? ORDER BY id_book DESC',
            (q, q, q)
        )]

    def get_book_options(self):
        return [f"{row[1]} - {row[2]}" for row in self.fetchall('SELECT id_book, isbn, title FROM book')]

    def add_book(self, isbn: str, title: str, author: str, year):
        year = self._ensure_int(year, 'Год')
        self.execute(
            'INSERT INTO book (isbn, title, author, year) VALUES (?, ?, ?, ?)',
            (isbn, title, author, year)
        )
        self.conn.commit()

    def add_copy(self, book_isbn, condition: str):
        if not book_isbn:
            raise ValueError('ISBN книги должен быть заполнен')
        row = self.execute('SELECT id_book FROM book WHERE isbn = ?', (book_isbn,)).fetchone()
        if not row:
            raise ValueError('Книга с таким ISBN не найдена')
        book_id = row[0]
        row = self.execute('SELECT id_condition FROM [condition] WHERE name = ?', (condition,)).fetchone()
        if not row:
            raise ValueError('Состояние экземпляра не найдено')
        condition_id = row[0]
        self.execute('INSERT INTO copy (id_book, id_condition) VALUES (?, ?)', (book_id, condition_id))
        self.conn.commit()

    def delete_book(self, book_id):
        book_id = self._ensure_int(book_id, 'ID книги')
        self.execute('DELETE FROM loan WHERE id_copy IN (SELECT id_copy FROM copy WHERE id_book = ?)', (book_id,))
        self.execute('DELETE FROM copy WHERE id_book = ?', (book_id,))
        self.execute('DELETE FROM book WHERE id_book = ?', (book_id,))
        self.conn.commit()

    def get_readers(self):
        return [self.format_row(row) for row in self.fetchall(
            "SELECT r.id_reader, r.reader_name, r.surname, r.patronymic, ISNULL(c.name, '') FROM reader r LEFT JOIN [class] c ON r.id_class = c.id_class ORDER BY r.id_reader DESC"
        )]

    def search_readers(self, query):
        if not query:
            return self.get_readers()
        q = f'%{query}%'
        return [self.format_row(row) for row in self.fetchall(
            "SELECT r.id_reader, r.reader_name, r.surname, r.patronymic, ISNULL(c.name, '') FROM reader r LEFT JOIN [class] c ON r.id_class = c.id_class WHERE r.reader_name LIKE ? OR r.surname LIKE ? OR r.patronymic LIKE ? ORDER BY r.id_reader DESC",
            (q, q, q)
        )]

    def get_readers_for_combobox(self):
        return [f"{row[0]} - {row[1]} {row[2]} {row[3]}" for row in self.fetchall(
            "SELECT id_reader, reader_name, surname, ISNULL(patronymic, '') FROM reader"
        )]

    def get_classes(self):
        return [row[0] for row in self.fetchall('SELECT name FROM [class]')]

    def get_conditions(self):
        return [row[0] for row in self.fetchall('SELECT name FROM [condition]')]

    def add_reader(self, name: str, patronymic: str, surname: str, class_name: str = None):
        class_id = None
        if class_name:
            row = self.execute('SELECT id_class FROM [class] WHERE name = ?', (class_name,)).fetchone()
            if row:
                class_id = row[0]
            else:
                raise ValueError('Класс не найден')
        self.execute('INSERT INTO reader (reader_name, patronymic, surname, id_class) VALUES (?, ?, ?, ?)', (name, patronymic, surname, class_id))
        self.conn.commit()

    def delete_reader(self, reader_id):
        reader_id = self._ensure_int(reader_id, 'ID читателя')
        self.execute('DELETE FROM loan WHERE id_reader = ?', (reader_id,))
        self.execute('DELETE FROM reader WHERE id_reader = ?', (reader_id,))
        self.conn.commit()

    def get_available_copies(self):
        return [f"{row[0]} - {row[1]} - {row[2]}" for row in self.fetchall(
            "SELECT c.id_copy, b.isbn, b.title FROM copy c JOIN book b ON c.id_book = b.id_book WHERE c.id_copy NOT IN (SELECT id_copy FROM loan WHERE status = 'Активно') AND c.id_condition NOT IN (SELECT id_condition FROM [condition] WHERE name = 'На списание')"
        )]

    def get_loans(self):
        # update overdue statuses server-side where supported
        try:
            self.execute("UPDATE loan SET status = 'Просрочено' WHERE status = 'Активно' AND due_date < CONVERT(date, GETDATE())")
            self.conn.commit()
        except Exception:
            pass
        return [self.format_row(row) for row in self.fetchall('SELECT * FROM loan ORDER BY id DESC')]

    def issue_loan(self, reader_id, copy_id, start_date):
        reader_id = self._ensure_int(reader_id, 'ID читателя')
        copy_id = self._ensure_int(copy_id, 'ID экземпляра')
        if isinstance(start_date, (date, datetime)):
            start_date_dt = start_date
            start_date = start_date_dt.strftime('%Y-%m-%d')
            due_date_dt = start_date_dt + timedelta(days=15)
            due_date = due_date_dt.strftime('%Y-%m-%d')
        else:
            due_date = None
        self.execute(
            "INSERT INTO loan (id_reader, id_copy, start_date, due_date, status) VALUES (?, ?, ?, ?, 'Активно')",
            (reader_id, copy_id, start_date, due_date)
        )
        self.conn.commit()

    def get_copy_condition_name(self, copy_id):
        """Получить название состояния экземпляра"""
        copy_id = self._ensure_int(copy_id, 'ID экземпляра')
        row = self.execute(
            'SELECT co.name FROM copy c JOIN [condition] co ON c.id_condition = co.id_condition WHERE c.id_copy = ?',
            (copy_id,)
        ).fetchone()
        return row[0] if row else None

    def extend_loan(self, loan_id, days):
        loan_id = self._ensure_int(loan_id, 'ID выдачи')
        days = self._ensure_int(days, 'Дней для продления')
        self.execute('UPDATE loan SET due_date = DATEADD(day, ?, due_date), status = ? WHERE id = ?', (days, 'Активно', loan_id))
        self.conn.commit()

    def return_loan(self, loan_id, return_date):
        loan_id = self._ensure_int(loan_id, 'ID выдачи')
        if isinstance(return_date, (date, datetime)):
            return_date = return_date.strftime('%Y-%m-%d')
        self.execute('UPDATE loan SET return_date = ?, status = ? WHERE id = ?', (return_date, 'Закрыто', loan_id))
        self.conn.commit()

    def delete_loan(self, loan_id):
        loan_id = self._ensure_int(loan_id, 'ID выдачи')
        self.execute('DELETE FROM loan WHERE id = ?', (loan_id,))
        self.conn.commit()

    def _ensure_int(self, value, field_name: str):
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            value = value.strip()
        if value == '' or value is None:
            raise ValueError(f'{field_name} должен быть заполнен')
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError(f'{field_name} должен быть целым числом')
