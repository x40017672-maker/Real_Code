import sqlite3

connection = sqlite3.connect("practice.db")
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users ( id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT
)
""")

username = input("Enter username: ")
password = input("Enter password: ")

cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

connection.commit()
print("User saved!")
connection.close()