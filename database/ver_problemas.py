import sqlite3

conexion = sqlite3.connect("obra.db")
cursor = conexion.cursor()

cursor.execute("""
SELECT *
FROM problemas_madre
""")

problemas = cursor.fetchall()

for problema in problemas:
    print(problema)

conexion.close()

import os

print(os.getcwd())