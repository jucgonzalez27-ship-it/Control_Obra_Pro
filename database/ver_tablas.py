import sqlite3
import os

print("Ruta actual:")
print(os.getcwd())

conexion = sqlite3.connect("obra.db")
cursor = conexion.cursor()

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table';
""")

tablas = cursor.fetchall()

for tabla in tablas:
    print(tabla)

conexion.close()