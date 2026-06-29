import sqlite3

conexion = sqlite3.connect("obra.db")
cursor = conexion.cursor()

cursor.execute("""
SELECT
    problemas_madre.titulo,
    problemas_madre.partida,
    problemas_madre.tipo_problema,
    responsables.nombre,
    COUNT(problema_departamento.departamento_id) AS departamentos_afectados
FROM problemas_madre
JOIN problema_departamento
    ON problemas_madre.id = problema_departamento.problema_id
JOIN responsables
    ON problemas_madre.responsable_id = responsables.id
GROUP BY problemas_madre.id
ORDER BY departamentos_afectados DESC
""")

resultados = cursor.fetchall()

print("\nRANKING DE PROBLEMAS\n")

for i, fila in enumerate(resultados, start=1):
    titulo, partida, tipo_problema, responsable, afectados = fila

    print(f"{i}. {titulo}")
    print(f"   Partida: {partida}")
    print(f"   Tipo: {tipo_problema}")
    print(f"   Responsable: {responsable}")
    print(f"   Departamentos afectados: {afectados}")
    print("-" * 50)

conexion.close()