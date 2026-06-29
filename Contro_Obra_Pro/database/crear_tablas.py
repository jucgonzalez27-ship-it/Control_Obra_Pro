import sqlite3
import os

print("Ruta actual:")
print(os.getcwd())

# Crear conexión
conexion = sqlite3.connect("obra.db")

# Crear cursor
cursor = conexion.cursor()

# Tabla departamentos
cursor.execute("""
CREATE TABLE IF NOT EXISTS departamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    torre TEXT NOT NULL,
    piso INTEGER NOT NULL,
    numero TEXT NOT NULL,
    estado TEXT NOT NULL
)
""")

# Tabla responsables
cursor.execute("""
CREATE TABLE IF NOT EXISTS responsables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    empresa TEXT,
    cargo TEXT
)
""")

# Tabla problemas_madre
cursor.execute("""
CREATE TABLE IF NOT EXISTS problemas_madre (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    partida TEXT NOT NULL,
    tipo_problema TEXT NOT NULL,
    descripcion TEXT,
    responsable_id INTEGER,
    estado TEXT NOT NULL,
    fecha_deteccion TEXT,
    fecha_compromiso TEXT,
    FOREIGN KEY (responsable_id) REFERENCES responsables(id)
)
""")

# Tabla problema_departamento
cursor.execute("""
CREATE TABLE IF NOT EXISTS problema_departamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problema_id INTEGER NOT NULL,
    departamento_id INTEGER NOT NULL,
    FOREIGN KEY (problema_id) REFERENCES problemas_madre(id),
    FOREIGN KEY (departamento_id) REFERENCES departamentos(id)
)
""")

# Tabla acciones
cursor.execute("""
CREATE TABLE IF NOT EXISTS acciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problema_id INTEGER NOT NULL,
    fecha TEXT NOT NULL,
    comentario TEXT NOT NULL,
    estado TEXT NOT NULL,
    FOREIGN KEY (problema_id) REFERENCES problemas_madre(id)
)
""")

conexion.commit()
conexion.close()

print("Base de datos creada correctamente.")