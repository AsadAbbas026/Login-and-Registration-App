import sqlite3

database = sqlite3.connect("registered_users.db")

cursor = database.cursor()

information = cursor.execute("SELECT * FROM users;")

for info in information:
    print(info)