School library Manager

Desktop application for automating operations of a school library. Application runs entirely on a local SQLite database and provides management of books, students, and loans, included search and controlled data entry. Program is intended for use by a single librarian or library administrator on one computer. It stores all data in a local file.

Data integrity is prioritized. When a loan is created, the book and the student are selected from existing records rather than typed manually. This prevents data duplication and conflicts.

Features:
1. Add, edit, and delete books, copies and students.
2. Track the list of available copies automatically.
3. View the current loan history of a student.
4. Create a loan by selecting a book and a student from drop-down lists.
5. Register the return of a loan.
6. Automatically flag overdue loans.
7. Search books and students.
8. All fields in the loan form are read-only data selection lists from the database.
9. ISBN and student ID are validated for format and uniqueness.
    

Requirements:

Python 3.9 or later

SQLite

Tkinter 
