import sqlite3

conexion = sqlite3.connect("obra.db")
cursor = conexion.cursor()

print("PROBLEMAS")
cursor.execute("SELECT * FROM problemas_madre")
for fila in cursor.fetchall():
    print(fila)

print("\nDEPARTAMENTOS")
cursor.execute("SELECT * FROM departamentos")
for fila in cursor.fetchall():
    print(fila)

print("\nRELACIONES")
cursor.execute("SELECT * FROM problema_departamento")
for fila in cursor.fetchall():
    print(fila)

conexion.close()