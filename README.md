# CopBuilder

CopBuilder es una aplicacion Streamlit para controlar avance operativo de departamentos en obra: recintos, partidas, bloqueos, restricciones, reportes, historial y trabajo en terreno.

El punto de entrada de la aplicacion es:

```text
app.py
```

La app esta preparada para ejecutarse localmente o en Streamlit Cloud. Si no existe una base SQLite local, el sistema inicializa automaticamente el esquema vacio al arrancar.

## Requisitos

- Python 3.11 o superior.
- Git.
- Dependencias definidas en `requirements.txt`.

## Instalacion Local

Crear y activar un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Ejecucion Local

Iniciar la aplicacion:

```powershell
python -m streamlit run app.py
```

Abrir en el navegador:

```text
http://localhost:8501
```

## Ejecucion En Red Local Para Celular

Iniciar Streamlit escuchando en la red local:

```powershell
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

Obtener la IP local del computador:

```powershell
ipconfig
```

Desde el celular, conectado a la misma red Wi-Fi, abrir:

```text
http://IP_DEL_COMPUTADOR:8501
```

Si no carga desde el celular, revisar el firewall de Windows y permitir Python/Streamlit en redes privadas.

## Streamlit Cloud

Para desplegar en Streamlit Cloud:

1. Subir el repositorio a GitHub sin archivos `.db`, `.sqlite` ni respaldos de bases reales.
2. Crear una nueva app en Streamlit Cloud.
3. Seleccionar el repositorio de GitHub.
4. Configurar `app.py` como archivo principal.
5. Confirmar que `requirements.txt` esta en la raiz del repositorio.
6. Desplegar.

No subir `.streamlit/secrets.toml`. Si se requieren secretos en el futuro, configurarlos desde el panel de Streamlit Cloud.

## Base De Datos

No subir bases SQLite reales al repositorio.

Archivos como los siguientes deben permanecer solo en el equipo local:

```text
*.db
*.sqlite
*.sqlite3
*.db-wal
*.db-shm
```

Si `obra_v01.db` no existe, CopBuilder crea automaticamente una base vacia con el esquema inicial. Luego se puede cargar configuracion y datos desde la propia app.

## Limitacion Actual De Persistencia

SQLite local sirve para beta, demo y pruebas controladas.

Para uso real multiusuario desde internet se recomienda migrar la persistencia a PostgreSQL o Supabase. Streamlit Cloud puede reiniciar el entorno y no debe considerarse almacenamiento definitivo para operacion productiva con multiples usuarios.

## Tests

Ejecutar todas las pruebas:

```powershell
python -m unittest discover -v
```

Validar sintaxis:

```powershell
python -m py_compile app.py database\servicios.py
```

## Checklist Antes De Subir A GitHub

Revisar estado local:

```powershell
git status --short --ignored
```

Confirmar que las bases reales aparecen como ignoradas y no como archivos a subir.

Agregar archivos versionables:

```powershell
git add .gitignore README.md requirements.txt app.py database tests docs
```

Crear commit:

```powershell
git commit -m "Preparar CopBuilder para Streamlit Cloud"
```

Subir a GitHub:

```powershell
git push -u origin main
```

Si la rama principal se llama `master`, usar:

```powershell
git push -u origin master
```
