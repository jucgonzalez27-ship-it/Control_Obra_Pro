import sqlite3

conexion = sqlite3.connect("obra.db")
cursor = conexion.cursor()

relaciones = [
    (1, 1),  # problema 1 afecta depto id 1 = 23
    (1, 2),  # problema 1 afecta depto id 2 = 24
    (1, 5),  # problema 1 afecta depto id 5 = 27
]

cursor.executemany("""
INSERT INTO problema_departamento (problema_id, departamento_id)
VALUES (?, ?)
""", relaciones)

conexion.commit()
conexion.close()

print("Problema relacionado con departamentos correctamente.")