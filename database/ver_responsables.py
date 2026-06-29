import sqlite3

conexion = sqlite3.connect("obra.db")
cursor = conexion.cursor()

cursor.execute("""
SELECT *
FROM responsables
""")

responsables = cursor.fetchall()

for responsable in responsables:
    print(responsable)

conexion.close()