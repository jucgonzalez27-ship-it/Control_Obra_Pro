import sqlite3

conexion = sqlite3.connect("obra.db")
cursor = conexion.cursor()

cursor.execute("SELECT * FROM problema_departamento")

relaciones = cursor.fetchall()

for relacion in relaciones:
    print(relacion)

conexion.close()