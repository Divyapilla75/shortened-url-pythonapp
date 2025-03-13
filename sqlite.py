import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM urls")
rows = cursor.fetchall()

for row in rows:
    print(row)  # Print each row to check if the short URL exists

conn.close()
