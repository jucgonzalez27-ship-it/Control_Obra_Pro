import sqlite3

conexion = sqlite3.connect("obra.db")
cursor = conexion.cursor()

cursor.execute("""
INSERT INTO responsables (
    nombre,
    empresa,
    cargo
)
VALUES (?, ?, ?)
""", (
    "Juan Perez",
    "Ventanas Chile",
    "Supervisor"
))

conexion.commit()
conexion.close()

print("Responsable insertado correctamente.")