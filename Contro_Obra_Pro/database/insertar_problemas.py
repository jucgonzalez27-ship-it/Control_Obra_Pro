import sqlite3

conexion = sqlite3.connect("obra.db")
cursor = conexion.cursor()

problemas = [
    (
        "Falta perfiles ventana piso 2",
        "Ventanas",
        "Falta material",
        "No han llegado perfiles de ventana",
        1,
        "Abierto",
        "2025-08-18",
        "2025-08-25"
    )
]

cursor.executemany("""
INSERT INTO problemas_madre (
    titulo,
    partida,
    tipo_problema,
    descripcion,
    responsable_id,
    estado,
    fecha_deteccion,
    fecha_compromiso
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", problemas)

conexion.commit()
conexion.close()

print("Problema creado correctamente.")