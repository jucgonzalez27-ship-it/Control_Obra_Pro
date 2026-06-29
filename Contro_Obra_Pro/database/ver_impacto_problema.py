import sqlite3

conexion = sqlite3.connect("obra.db")
cursor = conexion.cursor()

cursor.execute("""
SELECT 
    problemas_madre.id,
    problemas_madre.titulo,
    departamentos.id,
    departamentos.numero
FROM problema_departamento
JOIN problemas_madre
    ON problema_departamento.problema_id = problemas_madre.id
JOIN departamentos
    ON problema_departamento.departamento_id = departamentos.id
""")

resultados = cursor.fetchall()

for fila in resultados:
    print(fila)

conexion.close()