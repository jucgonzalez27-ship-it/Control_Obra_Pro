import sqlite3

conexion = sqlite3.connect("obra.db")
cursor = conexion.cursor()

cursor.execute("""
SELECT *
FROM departamentos
WHERE estado = 'Bloqueado'
""")

departamentos = cursor.fetchall()

for departamento in departamentos:
    print(departamento)

conexion.close()