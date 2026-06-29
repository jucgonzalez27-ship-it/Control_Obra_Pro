"""Reset seguro de datos operativos de Control Obra Pro V1.

Este script conserva configuracion base y borra solamente registros operativos.
No se ejecuta automaticamente: debe correrse manualmente y confirmar con RESET.
"""

from __future__ import annotations

from contextlib import closing
from datetime import datetime
from pathlib import Path
import shutil
import sqlite3
import sys


RUTA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_DB = RUTA_PROYECTO / "obra_v01.db"


TABLAS_OPERATIVAS_A_BORRAR = (
    "acciones",
    "restricciones",
    "problemas_madre",
    "restricciones_avance",
    "historial_partida_departamento",
    "liberaciones_departamento",
)


def tabla_existe(conexion: sqlite3.Connection, nombre: str) -> bool:
    fila = conexion.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (nombre,),
    ).fetchone()
    return fila is not None


def contar_registros(conexion: sqlite3.Connection, tabla: str) -> int:
    if not tabla_existe(conexion, tabla):
        return 0
    return conexion.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]


def crear_respaldo(ruta_db: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    ruta_respaldo = ruta_db.with_name(f"{ruta_db.stem}.backup-reset-{timestamp}.db")
    shutil.copy2(ruta_db, ruta_respaldo)
    return ruta_respaldo


def reset_operativo(ruta_db: Path = RUTA_DB) -> dict[str, int | str]:
    if not ruta_db.exists():
        raise FileNotFoundError(f"No existe la base de datos: {ruta_db}")

    ruta_respaldo = crear_respaldo(ruta_db)

    with closing(sqlite3.connect(ruta_db)) as conexion:
        conexion.row_factory = sqlite3.Row
        conexion.execute("PRAGMA foreign_keys = ON")

        conteos_antes = {
            tabla: contar_registros(conexion, tabla)
            for tabla in TABLAS_OPERATIVAS_A_BORRAR
        }
        partidas_antes = contar_registros(conexion, "estado_partida_departamento")

        with conexion:
            for tabla in TABLAS_OPERATIVAS_A_BORRAR:
                if tabla_existe(conexion, tabla):
                    conexion.execute(f"DELETE FROM {tabla}")

            if tabla_existe(conexion, "estado_partida_departamento"):
                conexion.execute(
                    """
                    UPDATE estado_partida_departamento
                    SET estado = 'no_iniciada',
                        actualizado_por_usuario_id = NULL,
                        fecha_ultima_actualizacion = NULL
                    """
                )

            if tabla_existe(conexion, "departamentos"):
                conexion.execute(
                    """
                    UPDATE departamentos
                    SET estado_operativo = 'sin_revisar',
                        fecha_ultima_revision = NULL
                    """
                )

        conteos_despues = {
            tabla: contar_registros(conexion, tabla)
            for tabla in TABLAS_OPERATIVAS_A_BORRAR
        }
        partidas_reiniciadas = conexion.execute(
            """
            SELECT COUNT(*)
            FROM estado_partida_departamento
            WHERE estado = 'no_iniciada'
              AND actualizado_por_usuario_id IS NULL
              AND fecha_ultima_actualizacion IS NULL
            """
        ).fetchone()[0] if tabla_existe(conexion, "estado_partida_departamento") else 0

    resumen: dict[str, int | str] = {
        "respaldo": str(ruta_respaldo),
        "partidas_estado_antes": partidas_antes,
        "partidas_reiniciadas": partidas_reiniciadas,
    }
    for tabla in TABLAS_OPERATIVAS_A_BORRAR:
        resumen[f"{tabla}_antes"] = conteos_antes[tabla]
        resumen[f"{tabla}_despues"] = conteos_despues[tabla]
    return resumen


def main() -> int:
    print("Reset operativo Control Obra Pro V1")
    print(f"Base objetivo: {RUTA_DB}")
    print()
    print("Se conservara configuracion base:")
    print("- obra, torre, departamentos, tipologias, recintos")
    print("- partidas, checklists, pesos, dependencias, especialidades, usuarios")
    print()
    print("Se borraran o reiniciaran datos operativos:")
    print("- estados cargados en terreno, historial, restricciones, observaciones")
    print("- problemas, bloqueos, liberaciones, comentarios y fechas operativas")
    print()

    confirmacion = input("ESCRIBIR RESET PARA CONTINUAR: ").strip()
    if confirmacion != "RESET":
        print("Operacion cancelada. No se modifico la base de datos.")
        return 1

    try:
        resumen = reset_operativo()
    except Exception as error:
        print(f"ERROR: {error}")
        return 2

    print()
    print("Reset operativo completado.")
    print(f"Respaldo creado: {resumen['respaldo']}")
    print(
        "Partidas reiniciadas: "
        f"{resumen['partidas_reiniciadas']} de "
        f"{resumen['partidas_estado_antes']}"
    )
    print()
    print("Conteo de tablas operativas despues del reset:")
    for tabla in TABLAS_OPERATIVAS_A_BORRAR:
        print(f"- {tabla}: {resumen[f'{tabla}_despues']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
