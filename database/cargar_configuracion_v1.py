"""Carga idempotente de la configuracion V1 de Proyecto Montevista."""

from pathlib import Path
import shutil
from datetime import datetime

from database.modelo_v01 import (
    RUTA_DB_PREDETERMINADA,
    aplicar_especialidades_partidas,
    inicializar_base,
    sesion,
)


TIPOLOGIAS_V1 = {
    "C1": {
        "departamentos": ["13", "23", "33", "43", "53"],
        "recintos": [
            "Living - Comedor",
            "Cocina",
            "Dormitorio Principal",
            "Dormitorio 1",
            "Dormitorio 2",
            "Baño 1",
            "Baño 2",
            "Terraza Principal",
            "Terraza Suite",
        ],
    },
    "C2": {
        "departamentos": ["6", "16", "26", "36", "46", "56"],
        "recintos": [
            "Living - Comedor",
            "Cocina",
            "Dormitorio Principal",
            "Dormitorio 1",
            "Baño 1",
            "Baño 2",
            "Walk-in Closet",
            "Terraza Principal",
            "Terraza Suite",
        ],
    },
    "D": {
        "departamentos": [
            "4",
            "7",
            "14",
            "17",
            "24",
            "27",
            "29",
            "34",
            "37",
            "39",
            "44",
            "47",
            "49",
            "54",
            "57",
            "59",
        ],
        "recintos": [
            "Living - Comedor",
            "Cocina",
            "Dormitorio Principal",
            "Dormitorio 1",
            "Baño 1",
            "Baño 2",
            "Walk-in Closet",
            "Terraza Principal",
            "Terraza Suite",
        ],
    },
    "E": {
        "departamentos": [
            "5",
            "15",
            "18",
            "25",
            "28",
            "35",
            "38",
            "45",
            "48",
            "55",
            "58",
        ],
        "recintos": [
            "Living - Comedor",
            "Cocina",
            "Dormitorio Principal",
            "Dormitorio 1",
            "Baño 1",
            "Baño 2",
            "Walk-in Closet",
            "Terraza Principal",
            "Terraza Suite",
        ],
    },
    "F": {
        "departamentos": ["3"],
        "recintos": [
            "Living",
            "Cocina",
            "Dormitorio Principal",
            "Dormitorio 1",
            "Baño 1",
            "Baño 2",
        ],
    },
}


CHECKLISTS_MAESTROS = {
    "Living - Comedor": [
        "Tabique",
        "Empaste",
        "Aparejo",
        "Primera mano de pintura",
        "Mano final de pintura",
        "Piso flotante",
        "Guardapolvo",
        "Cornisa",
        "Junquillo",
        "Puerta",
        "Cerradura",
        "Componentes eléctricos",
        "Radiador",
    ],
    "Cocina": [
        "Tabique",
        "Cerámica muro",
        "Fragüe muro",
        "Cerámica piso",
        "Empaste",
        "Aparejo",
        "Primera mano de pintura",
        "Mano final de pintura",
        "Mueble base",
        "Mueble aéreo",
        "Estante",
        "Cubierta",
        "Guardapolvo cerámico",
        "Cornisa",
        "Junquillo",
        "Puerta",
        "Cerradura",
        "Lavaplatos",
        "Grifería",
        "Encimera",
        "Horno",
        "Campana",
        "Componentes eléctricos",
        "Radiador",
        "Caldera",
    ],
    "Dormitorio": [
        "Tabique",
        "Empaste",
        "Aparejo",
        "Primera mano de pintura",
        "Mano final de pintura",
        "Piso flotante",
        "Guardapolvo",
        "Cornisa",
        "Junquillo",
        "Puerta",
        "Cerradura",
        "Closet",
        "Componentes eléctricos",
        "Radiador",
    ],
    "Walk-in Closet": [
        "Tabique",
        "Empaste",
        "Aparejo",
        "Primera mano de pintura",
        "Mano final de pintura",
        "Piso flotante",
        "Guardapolvo",
        "Cornisa",
        "Junquillo",
        "Closet",
        "Componentes eléctricos",
    ],
    "Baño Principal": [
        "Tabique",
        "Cerámica muro",
        "Fragüe muro",
        "Cerámica piso",
        "Empaste",
        "Aparejo",
        "Primera mano de pintura",
        "Mano final de pintura",
        "Guardapolvo cerámico",
        "Cornisa",
        "Puerta",
        "Cerradura",
        "Vanitorio",
        "Espejo",
        "Extractor de aire",
        "Grifería",
        "Receptáculo",
        "Mampara",
        "WC",
        "Accesorios",
        "Componentes eléctricos",
    ],
    "Baño 1": [
        "Tabique",
        "Cerámica muro",
        "Fragüe muro",
        "Cerámica piso",
        "Empaste",
        "Aparejo",
        "Primera mano de pintura",
        "Mano final de pintura",
        "Guardapolvo cerámico",
        "Cornisa",
        "Puerta",
        "Cerradura",
        "Vanitorio",
        "Espejo",
        "Extractor de aire",
        "Grifería",
        "Tina",
        "WC",
        "Accesorios",
        "Componentes eléctricos",
    ],
    "Terraza": [
        "Textura",
        "Piso cerámico",
        "Guardapolvo cerámico",
        "Cielo",
        "Baranda vidriada",
        "Componentes eléctricos",
    ],
}


CHECKLIST_MAESTRO_POR_RECINTO = {
    "Living": "Living - Comedor",
    "Living - Comedor": "Living - Comedor",
    "Cocina": "Cocina",
    "Dormitorio Principal": "Dormitorio",
    "Dormitorio 1": "Dormitorio",
    "Dormitorio 2": "Dormitorio",
    "Walk-in Closet": "Dormitorio",
    "Baño 1": "Baño 1",
    "Baño 2": "Baño Principal",
    "Baño Principal": "Baño Principal",
    "Terraza Principal": "Terraza",
    "Terraza Suite": "Terraza",
}


PESOS_AVANCE_PARTIDA_V1 = {
    "Empaste": 2,
    "Mano final de pintura": 2,
    "Porcelanato piso": 2,
    "Porcelanato muro": 2,
    "Cerámica piso": 2,
    "Cerámica muro": 2,
    "Piso cerámico": 2,
    "Piso flotante": 2,
    "Mueble base": 2,
    "Mueble aéreo": 2,
    "Cubierta": 2,
    "Closet": 2,
    "Textura": 2,
    "Textura terraza": 2,
}


def _peso_avance_v1(partida: str) -> int:
    """Peso operativo V1; las partidas no listadas quedan con peso 1."""
    return PESOS_AVANCE_PARTIDA_V1.get(partida, 1)


def _clave_departamento(numero: str) -> tuple[int, str]:
    texto = str(numero).strip()
    try:
        return 0, str(int(texto))
    except ValueError:
        return 1, texto.casefold()


def _crear_respaldo(ruta_db: Path) -> Path | None:
    if not ruta_db.exists():
        return None
    marca = datetime.now().strftime("%Y%m%d-%H%M%S")
    respaldo = ruta_db.with_name(f"{ruta_db.stem}.backup-{marca}{ruta_db.suffix}")
    shutil.copy2(ruta_db, respaldo)
    return respaldo


def cargar_configuracion_v1(
    ruta_db: str | Path = RUTA_DB_PREDETERMINADA,
    *,
    crear_respaldo: bool = False,
) -> dict:
    """Carga tipologias, recintos, asignaciones y checklists V1.

    La carga es idempotente: puede ejecutarse varias veces sin duplicar datos.
    No elimina recintos ni partidas existentes; solo agrega y actualiza ordenes.
    """
    ruta = Path(ruta_db)
    respaldo = _crear_respaldo(ruta) if crear_respaldo else None
    inicializar_base(ruta)

    resumen = {
        "respaldo": str(respaldo) if respaldo else None,
        "tipologias": 0,
        "recintos": 0,
        "partidas": 0,
        "checklist_partidas": 0,
        "departamentos_asignados": 0,
        "departamentos_no_encontrados": [],
    }

    with sesion(ruta) as conexion:
        for nombre_tipologia, definicion in TIPOLOGIAS_V1.items():
            conexion.execute(
                "INSERT OR IGNORE INTO tipologias (nombre) VALUES (?)",
                (nombre_tipologia,),
            )
            tipologia_id = conexion.execute(
                "SELECT id FROM tipologias WHERE nombre = ?",
                (nombre_tipologia,),
            ).fetchone()["id"]
            resumen["tipologias"] += 1

            for orden, recinto in enumerate(definicion["recintos"], start=1):
                conexion.execute(
                    """
                    INSERT INTO tipologia_recinto (
                        tipologia_id, nombre_recinto, orden
                    )
                    VALUES (?, ?, ?)
                    ON CONFLICT (tipologia_id, nombre_recinto)
                    DO UPDATE SET orden = excluded.orden
                    """,
                    (tipologia_id, recinto, orden),
                )
                resumen["recintos"] += 1

            departamentos = {
                _clave_departamento(fila["numero"]): fila["id"]
                for fila in conexion.execute(
                    "SELECT id, numero FROM departamentos"
                ).fetchall()
            }
            for numero in definicion["departamentos"]:
                departamento_id = departamentos.get(_clave_departamento(numero))
                if departamento_id is None:
                    resumen["departamentos_no_encontrados"].append(
                        f"{nombre_tipologia}: {numero}"
                    )
                    continue
                conexion.execute(
                    """
                    UPDATE departamentos
                    SET tipologia_id = ?
                    WHERE id = ?
                    """,
                    (tipologia_id, departamento_id),
                )
                resumen["departamentos_asignados"] += 1

        for partidas in CHECKLISTS_MAESTROS.values():
            for partida in partidas:
                conexion.execute(
                    "INSERT OR IGNORE INTO partidas (nombre) VALUES (?)",
                    (partida,),
                )
                resumen["partidas"] += 1

        for nombre_recinto, nombre_checklist in CHECKLIST_MAESTRO_POR_RECINTO.items():
            partidas = CHECKLISTS_MAESTROS[nombre_checklist]
            recintos = conexion.execute(
                """
                SELECT id
                FROM tipologia_recinto
                WHERE nombre_recinto = ?
                """,
                (nombre_recinto,),
            ).fetchall()
            for recinto in recintos:
                for orden, partida in enumerate(partidas, start=1):
                    partida_id = conexion.execute(
                        "SELECT id FROM partidas WHERE nombre = ?",
                        (partida,),
                    ).fetchone()["id"]
                    peso_avance = _peso_avance_v1(partida)
                    conexion.execute(
                        """
                        INSERT INTO recinto_partida (
                            tipologia_recinto_id,
                            partida_id,
                            orden,
                            peso_avance,
                            obligatoria
                        )
                        VALUES (?, ?, ?, ?, 1)
                        ON CONFLICT (tipologia_recinto_id, partida_id)
                        DO UPDATE SET
                            orden = excluded.orden,
                            peso_avance = excluded.peso_avance,
                            obligatoria = 1
                        """,
                        (recinto["id"], partida_id, orden, peso_avance),
                    )
                    resumen["checklist_partidas"] += 1

        aplicar_especialidades_partidas(conexion)

    return resumen


if __name__ == "__main__":
    resultado = cargar_configuracion_v1(crear_respaldo=True)
    print("Configuracion V1 cargada.")
    for clave, valor in resultado.items():
        print(f"{clave}: {valor}")
