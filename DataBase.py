import sqlite3
def init_db(): #to create the database
    conn=sqlite3.connect("flights.db") # create database file
    cursor=conn.cursor() # to run SQL commmands
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            flight_number TEXT,
            departure TEXT,
            destination TEXT,
            date TEXT,
            seat_number TEXT
        )
    """) # create the table by  SQL, the columns inside, and id is primary key for each row
    conn.commit() # to save the changes
    conn.close() # to close the connection