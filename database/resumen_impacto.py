import sqlite3

conexion = sqlite3.connect("obra.db")
cursor = conexion.cursor()

cursor.execute("""
SELECT
    problemas_madre.titulo,
    COUNT(problema_departamento.departamento_id) as cantidad_afectados
FROM problemas_madre
JOIN problema_departamento
    ON problemas_madre.id = problema_departamento.problema_id
GROUP BY problemas_madre.id, problemas_madre.titulo
""")

resultados = cursor.fetchall()

print("\nRESUMEN DE IMPACTO\n")

for titulo, cantidad in resultados:
    print(f"Problema: {titulo}")
    print(f"Departamentos afectados: {cantidad}")
    print("-" * 40)

conexion.close()