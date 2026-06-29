# Control Obra Pro

Control Obra Pro es una aplicacion Streamlit para controlar avance operativo de departamentos en obra: partidas, recintos, bloqueos, restricciones, reportes e historial.

La aplicacion esta preparada para ejecutarse localmente o en Streamlit Cloud. Si no existe una base local, el sistema crea el esquema inicial automaticamente al iniciar.

## Requisitos

- Python 3.11 o superior.
- Git.
- Acceso local al repositorio.

## Instalacion

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

## Ejecucion local

Iniciar la aplicacion:

```powershell
python -m streamlit run app.py
```

Abrir en el navegador:

```text
http://localhost:8501
```

## Ejecucion en red local para celular

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

Ejemplo:

```text
http://192.168.1.50:8501
```

Si no carga desde el celular, revisar firewall de Windows y permitir Python/Streamlit en redes privadas.

## Tests

Ejecutar todas las pruebas:

```powershell
python -m unittest discover -v
```

Validar sintaxis de la app:

```powershell
python -m py_compile app.py
```

## Base de datos local

No subir bases reales al repositorio.

Archivos como los siguientes deben permanecer solo en el equipo local:

```text
*.db
*.sqlite
*.sqlite3
```

La base operativa local se crea automaticamente si no existe. Para una prueba piloto limpia, iniciar la app sin copiar una base real al repositorio.

## Streamlit Cloud

Para desplegar en Streamlit Cloud:

1. Subir el repositorio a GitHub sin archivos `.db`.
2. Crear una nueva app en Streamlit Cloud.
3. Seleccionar el repositorio.
4. Usar `app.py` como archivo principal.
5. Verificar que `requirements.txt` este en la raiz del repositorio.
6. Desplegar.

No subir `.streamlit/secrets.toml`. Si se requieren secretos en el futuro, configurarlos desde el panel de Streamlit Cloud.

## Subir a GitHub

Revisar estado local:

```powershell
git status
```

Confirmar que no aparezcan bases reales:

```powershell
git status --short
```

Agregar archivos del proyecto:

```powershell
git add .
```

Crear commit:

```powershell
git commit -m "Preparar Control Obra Pro para piloto"
```

Crear repositorio en GitHub y asociar remoto:

```powershell
git remote add origin https://github.com/USUARIO/REPOSITORIO.git
```

Subir:

```powershell
git push -u origin main
```

Si la rama principal se llama `master`, usar:

```powershell
git push -u origin master
```
