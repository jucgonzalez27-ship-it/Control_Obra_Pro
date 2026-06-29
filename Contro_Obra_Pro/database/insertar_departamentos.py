import sqlite3

conexion = sqlite3.connect("obra.db")
cursor = conexion.cursor()

departamentos = [
    ("B", 2, "23", "Bloqueado"),
    ("B", 2, "24", "Bloqueado"),
    ("B", 2, "25", "Observado"),
    ("B", 2, "26", "Liberable"),
    ("B", 2, "27", "Bloqueado"),
    ("B", 2, "28", "Observado"),
    ("B", 2, "29", "Liberable"),
]

cursor.executemany("""
INSERT INTO departamentos (torre, piso, numero, estado)
VALUES (?, ?, ?, ?)
""", departamentos)

conexion.commit()
conexion.close()

print("Departamentos insertados correctamente.")