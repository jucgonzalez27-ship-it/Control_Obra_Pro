import sqlite3
from datetime import datetime

conexion = sqlite3.connect("obra.db")
cursor = conexion.cursor()

cursor.execute("""
SELECT
    problemas_madre.titulo,
    problemas_madre.fecha_deteccion,
    COUNT(problema_departamento.departamento_id) as afectados
FROM problemas_madre
JOIN problema_departamento
    ON problemas_madre.id = problema_departamento.problema_id
GROUP BY problemas_madre.id
""")

resultados = cursor.fetchall()

print("\nRANKING DE PRIORIDAD\n")

for titulo, fecha_deteccion, afectados in resultados:

    fecha = datetime.strptime(fecha_deteccion, "%Y-%m-%d")
    dias_abierto = (datetime.now() - fecha).days

    prioridad = afectados + dias_abierto

    print(f"Problema: {titulo}")
    print(f"Departamentos afectados: {afectados}")
    print(f"Días abierto: {dias_abierto}")
    print(f"Prioridad: {prioridad}")
    print("-" * 50)

conexion.close()