"""Operaciones de lectura y escritura usadas por la interfaz."""

from datetime import date
from pathlib import Path

from database.modelo_v01 import (
    DEPENDENCIA_TODAS_PRINCIPALES,
    ESPECIALIDAD_PREDETERMINADA,
    ESPECIALIDADES_V1,
    RUTA_DB_PREDETERMINADA,
    inicializar_base,
    sesion,
)
from database.reglas import calcular_bloqueo


def preparar_base(ruta_db: str | Path = RUTA_DB_PREDETERMINADA) -> Path:
    return inicializar_base(ruta_db)


def obtener_resumen_configuracion(ruta_db=RUTA_DB_PREDETERMINADA) -> dict:
    with sesion(ruta_db) as conexion:
        return {
            "obras": conexion.execute("SELECT COUNT(*) FROM obras").fetchone()[0],
            "torres": conexion.execute("SELECT COUNT(*) FROM torres").fetchone()[0],
            "departamentos": conexion.execute(
                "SELECT COUNT(*) FROM departamentos"
            ).fetchone()[0],
            "usuarios": conexion.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0],
            "responsables": conexion.execute(
                "SELECT COUNT(*) FROM responsables"
            ).fetchone()[0],
        }


def listar_obras(ruta_db=RUTA_DB_PREDETERMINADA) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            "SELECT id, nombre FROM obras WHERE activa = 1 ORDER BY nombre"
        ).fetchall()
        return [dict(fila) for fila in filas]


def listar_torres(obra_id: int, ruta_db=RUTA_DB_PREDETERMINADA) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT id, nombre
            FROM torres
            WHERE obra_id = ?
            ORDER BY nombre
            """,
            (obra_id,),
        ).fetchall()
        return [dict(fila) for fila in filas]


def crear_obra(nombre: str, ruta_db=RUTA_DB_PREDETERMINADA) -> int:
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre de la obra es obligatorio.")

    with sesion(ruta_db) as conexion:
        cursor = conexion.execute(
            "INSERT INTO obras (nombre) VALUES (?)",
            (nombre,),
        )
        return cursor.lastrowid


def crear_torre(obra_id: int, nombre: str, ruta_db=RUTA_DB_PREDETERMINADA) -> int:
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre de la torre es obligatorio.")

    with sesion(ruta_db) as conexion:
        cursor = conexion.execute(
            "INSERT INTO torres (obra_id, nombre) VALUES (?, ?)",
            (obra_id, nombre),
        )
        return cursor.lastrowid


def crear_departamentos(
    torre_id: int,
    departamentos: list[tuple[int, str]],
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> int:
    registros = []
    vistos = set()

    for piso, numero in departamentos:
        numero_limpio = str(numero).strip()
        if not numero_limpio:
            raise ValueError("Todos los departamentos deben tener número.")
        clave = numero_limpio.casefold()
        if clave in vistos:
            raise ValueError(f"El departamento {numero_limpio} está repetido.")
        vistos.add(clave)
        registros.append((torre_id, int(piso), numero_limpio))

    if not registros:
        raise ValueError("Debes ingresar al menos un departamento.")

    with sesion(ruta_db) as conexion:
        conexion.executemany(
            """
            INSERT INTO departamentos (torre_id, piso, numero)
            VALUES (?, ?, ?)
            """,
            registros,
        )
    return len(registros)


def crear_usuario(
    nombre: str,
    rol: str,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> int:
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre del usuario es obligatorio.")
    if rol not in {"Administrador", "Supervisor", "Solo lectura"}:
        raise ValueError("El rol seleccionado no es válido.")

    with sesion(ruta_db) as conexion:
        cursor = conexion.execute(
            "INSERT INTO usuarios (nombre, rol) VALUES (?, ?)",
            (nombre, rol),
        )
        return cursor.lastrowid


def crear_responsable(
    nombre: str,
    empresa: str = "",
    cargo: str = "",
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> int:
    nombre = nombre.strip()
    if not nombre:
        raise ValueError("El nombre del responsable es obligatorio.")

    with sesion(ruta_db) as conexion:
        cursor = conexion.execute(
            """
            INSERT INTO responsables (nombre, empresa, cargo)
            VALUES (?, ?, ?)
            """,
            (nombre, empresa.strip() or None, cargo.strip() or None),
        )
        return cursor.lastrowid


def listar_departamentos(ruta_db=RUTA_DB_PREDETERMINADA) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT
                o.nombre AS obra,
                t.nombre AS torre,
                d.piso,
                d.numero AS departamento,
                CASE
                    WHEN EXISTS (
                        SELECT 1
                        FROM restricciones r
                        WHERE r.departamento_id = d.id
                          AND r.estado <> 'Verificado'
                          AND r.bloquea_entrega = 1
                    ) OR d.estado_operativo = 'bloqueado'
                        THEN 'Bloqueado'
                    WHEN d.estado_operativo = 'observado'
                        THEN 'Observado no bloqueante'
                    WHEN d.estado_operativo IN ('liberable', 'verificado')
                        THEN 'Liberable'
                    WHEN d.estado_operativo = 'en_proceso'
                        THEN 'En proceso'
                    ELSE 'Sin revisar'
                END AS estado,
                (
                    SELECT COUNT(*)
                    FROM estado_partida_departamento epd
                    WHERE epd.departamento_id = d.id
                      AND epd.estado NOT IN ('verificada', 'no_aplica')
                ) + (
                    SELECT COUNT(*)
                    FROM restricciones r
                    WHERE r.departamento_id = d.id
                      AND r.estado <> 'Verificado'
                ) AS pendientes_activos
            FROM departamentos d
            JOIN torres t ON t.id = d.torre_id
            JOIN obras o ON o.id = t.obra_id
            ORDER BY o.nombre, t.nombre, d.piso, d.numero
            """
        ).fetchall()
        return [dict(fila) for fila in filas]


def obtener_dashboard_departamentos(ruta_db=RUTA_DB_PREDETERMINADA) -> list[dict]:
    """Resume avance, bloqueos y responsables para la matriz principal."""
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            WITH avance AS (
                SELECT
                    epd.departamento_id,
                    COALESCE(SUM(CASE
                        WHEN epd.estado <> 'no_aplica' THEN rp.peso_avance
                        ELSE 0
                    END), 0) AS aplicables,
                    COALESCE(SUM(CASE
                        WHEN epd.estado = 'verificada' THEN rp.peso_avance
                        ELSE 0
                    END), 0) AS verificadas,
                    COALESCE(SUM(CASE
                        WHEN epd.estado IN ('terminada', 'verificada')
                        THEN rp.peso_avance ELSE 0
                    END), 0) AS declaradas,
                    COUNT(CASE WHEN epd.estado = 'bloqueada' THEN 1 END)
                        AS bloqueos_partida,
                    COUNT(CASE WHEN epd.estado = 'observada' THEN 1 END)
                        AS observaciones_partida,
                    COUNT(CASE
                        WHEN epd.estado NOT IN ('verificada', 'no_aplica') THEN 1
                    END) AS pendientes_partida
                FROM estado_partida_departamento epd
                JOIN recinto_partida rp ON rp.id = epd.recinto_partida_id
                GROUP BY epd.departamento_id
            ),
            restricciones_resumen AS (
                SELECT
                    r.departamento_id,
                    COUNT(CASE
                        WHEN r.estado <> 'Verificado'
                         AND r.bloquea_entrega = 1 THEN 1
                    END) AS bloqueos_restriccion,
                    COUNT(CASE
                        WHEN r.estado <> 'Verificado'
                         AND r.bloquea_entrega = 0 THEN 1
                    END) AS observaciones_restriccion,
                    COUNT(CASE
                        WHEN r.estado <> 'Verificado'
                         AND r.fecha_compromiso < date('now') THEN 1
                    END) AS vencidas,
                    MIN(CASE
                        WHEN r.estado <> 'Verificado'
                        THEN r.fecha_compromiso
                    END) AS proxima_fecha,
                    (
                        SELECT resp.nombre
                        FROM restricciones r2
                        JOIN problemas_madre pm2
                            ON pm2.id = r2.problema_madre_id
                        JOIN responsables resp
                            ON resp.id = pm2.responsable_id
                        WHERE r2.departamento_id = r.departamento_id
                          AND r2.estado <> 'Verificado'
                        ORDER BY r2.bloquea_entrega DESC, r2.fecha_compromiso
                        LIMIT 1
                    ) AS responsable_restriccion
                FROM restricciones r
                GROUP BY r.departamento_id
            ),
            responsables_partida AS (
                SELECT
                    epd.departamento_id,
                    (
                        SELECT resp.nombre
                        FROM estado_partida_departamento epd2
                        JOIN restricciones_avance ra
                            ON ra.estado_partida_id = epd2.id
                           AND ra.estado = 'activa'
                        JOIN responsables resp ON resp.id = ra.responsable_id
                        WHERE epd2.departamento_id = epd.departamento_id
                        ORDER BY ra.fecha_compromiso
                        LIMIT 1
                    ) AS responsable_partida
                FROM estado_partida_departamento epd
                GROUP BY epd.departamento_id
            )
            SELECT
                d.id,
                o.nombre AS obra,
                t.nombre AS torre,
                d.piso,
                d.numero AS departamento,
                d.estado_operativo,
                COALESCE(a.aplicables, 0) AS aplicables,
                COALESCE(a.verificadas, 0) AS verificadas,
                COALESCE(a.declaradas, 0) AS declaradas,
                COALESCE(a.pendientes_partida, 0) AS pendientes_partida,
                COALESCE(a.bloqueos_partida, 0)
                    + COALESCE(rr.bloqueos_restriccion, 0) AS bloqueos_activos,
                COALESCE(a.observaciones_partida, 0)
                    + COALESCE(rr.observaciones_restriccion, 0)
                    AS observaciones_activas,
                COALESCE(rr.vencidas, 0) AS vencidas,
                rr.proxima_fecha,
                COALESCE(
                    rr.responsable_restriccion,
                    rp.responsable_partida,
                    'Sin asignar'
                ) AS responsable_principal
            FROM departamentos d
            JOIN torres t ON t.id = d.torre_id
            JOIN obras o ON o.id = t.obra_id
            LEFT JOIN avance a ON a.departamento_id = d.id
            LEFT JOIN restricciones_resumen rr ON rr.departamento_id = d.id
            LEFT JOIN responsables_partida rp ON rp.departamento_id = d.id
            ORDER BY o.nombre, t.nombre, d.piso, d.numero
            """
        ).fetchall()

    resultado = []
    for fila in filas:
        registro = dict(fila)
        aplicables = registro["aplicables"]
        registro["avance_oficial"] = (
            round(registro["verificadas"] * 100 / aplicables)
            if aplicables
            else 0
        )
        registro["avance_declarado"] = (
            round(registro["declaradas"] * 100 / aplicables)
            if aplicables
            else 0
        )
        registro["estado"] = _estado_dashboard(registro)
        resultado.append(registro)
    return resultado


def _estado_dashboard(departamento: dict) -> str:
    if departamento["bloqueos_activos"]:
        return "Bloqueado"
    if departamento["observaciones_activas"] or departamento["estado_operativo"] == "observado":
        return "Observado"
    if departamento["estado_operativo"] in {"liberable", "verificado"}:
        return "Liberable"
    if departamento["estado_operativo"] == "en_proceso":
        return "En proceso"
    return "Sin revisar"


def obtener_resumen_dashboard(ruta_db=RUTA_DB_PREDETERMINADA) -> dict:
    departamentos = obtener_dashboard_departamentos(ruta_db)
    total = len(departamentos)
    avance_oficial = (
        round(sum(depto["avance_oficial"] for depto in departamentos) / total)
        if total
        else 0
    )
    avance_declarado = (
        round(sum(depto["avance_declarado"] for depto in departamentos) / total)
        if total
        else 0
    )
    return {
        "total": total,
        "avance_oficial": avance_oficial,
        "avance_declarado": avance_declarado,
        "bloqueados": sum(1 for depto in departamentos if depto["estado"] == "Bloqueado"),
        "observados": sum(1 for depto in departamentos if depto["estado"] == "Observado"),
        "liberables": sum(1 for depto in departamentos if depto["estado"] == "Liberable"),
        "vencidas": sum(depto["vencidas"] for depto in departamentos),
    }


def obtener_resumen_pisos(ruta_db=RUTA_DB_PREDETERMINADA) -> list[dict]:
    departamentos = obtener_dashboard_departamentos(ruta_db)
    por_piso = {}
    for departamento in departamentos:
        por_piso.setdefault(departamento["piso"], []).append(departamento)

    resumen = []
    for piso, registros in sorted(por_piso.items()):
        total = len(registros)
        resumen.append(
            {
                "piso": piso,
                "nivel": f"Piso {piso}" if piso >= 0 else "Subterráneo",
                "departamentos": total,
                "avance_oficial": round(
                    sum(item["avance_oficial"] for item in registros) / total
                ),
                "avance_declarado": round(
                    sum(item["avance_declarado"] for item in registros) / total
                ),
                "bloqueados": sum(1 for item in registros if item["estado"] == "Bloqueado"),
                "observados": sum(1 for item in registros if item["estado"] == "Observado"),
                "liberables": sum(1 for item in registros if item["estado"] == "Liberable"),
            }
        )
    return resumen


def obtener_restricciones_dashboard(
    departamento_id: int,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    hoy = date.today().isoformat()
    with sesion(ruta_db) as conexion:
        restricciones = conexion.execute(
            """
            SELECT
                'Problema' AS origen,
                rd.titulo,
                rd.recinto,
                rd.partida,
                rd.tipo_problema AS tipo,
                rd.responsable,
                rd.estado,
                rd.fecha_compromiso,
                rd.comentario_corto AS comentario,
                rd.bloquea_entrega,
                CASE WHEN rd.fecha_compromiso < ? THEN 1 ELSE 0 END AS vencida
            FROM v_restricciones_detalle rd
            JOIN departamentos d ON d.numero = rd.departamento
            JOIN torres t ON t.nombre = rd.torre AND t.id = d.torre_id
            WHERE d.id = ?
              AND rd.estado <> 'Verificado'
            UNION ALL
            SELECT
                'Partida' AS origen,
                ra.causa AS titulo,
                tr.nombre_recinto AS recinto,
                p.nombre AS partida,
                'Bloqueo de avance' AS tipo,
                resp.nombre AS responsable,
                ra.estado AS estado,
                ra.fecha_compromiso,
                COALESCE(ra.comentario, '') AS comentario,
                1 AS bloquea_entrega,
                CASE WHEN ra.fecha_compromiso < ? THEN 1 ELSE 0 END AS vencida
            FROM restricciones_avance ra
            JOIN estado_partida_departamento epd
                ON epd.id = ra.estado_partida_id
            JOIN recinto_partida rp ON rp.id = epd.recinto_partida_id
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN partidas p ON p.id = rp.partida_id
            JOIN responsables resp ON resp.id = ra.responsable_id
            WHERE epd.departamento_id = ?
              AND ra.estado = 'activa'
            ORDER BY vencida DESC, bloquea_entrega DESC, fecha_compromiso
            """,
            (hoy, departamento_id, hoy, departamento_id),
        ).fetchall()
        return [dict(fila) for fila in restricciones]


def obtener_partidas_pendientes_dashboard(
    departamento_id: int,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT
                tr.nombre_recinto AS recinto,
                p.nombre AS partida,
                p.especialidad,
                epd.estado,
                1 AS obligatoria,
                ra.fecha_compromiso,
                resp.nombre AS responsable
            FROM estado_partida_departamento epd
            JOIN recinto_partida rp ON rp.id = epd.recinto_partida_id
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN partidas p ON p.id = rp.partida_id
            LEFT JOIN restricciones_avance ra
                ON ra.estado_partida_id = epd.id
               AND ra.estado = 'activa'
            LEFT JOIN responsables resp ON resp.id = ra.responsable_id
            WHERE epd.departamento_id = ?
              AND epd.estado NOT IN ('verificada', 'no_aplica')
            ORDER BY tr.orden, rp.orden, p.nombre
            """,
            (departamento_id,),
        ).fetchall()
        return [dict(fila) for fila in filas]


def obtener_ficha_dashboard_departamento(
    departamento_id: int,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> dict:
    departamentos = obtener_dashboard_departamentos(ruta_db)
    ficha = next(
        (departamento for departamento in departamentos if departamento["id"] == departamento_id),
        None,
    )
    if ficha is None:
        raise ValueError("El departamento seleccionado no existe.")

    restricciones = obtener_restricciones_dashboard(departamento_id, ruta_db)
    pendientes = obtener_partidas_pendientes_dashboard(departamento_id, ruta_db)
    historial = obtener_historial_partidas_departamento(
        departamento_id,
        limite=8,
        ruta_db=ruta_db,
    )
    ficha = dict(ficha)
    ficha["restricciones"] = restricciones
    ficha["bloqueos"] = [item for item in restricciones if item["bloquea_entrega"]]
    ficha["observaciones"] = [
        item for item in restricciones if not item["bloquea_entrega"]
    ]
    ficha["vencidas_detalle"] = [item for item in restricciones if item["vencida"]]
    ficha["pendientes"] = pendientes
    ficha["historial"] = historial
    return ficha


def listar_usuarios(ruta_db=RUTA_DB_PREDETERMINADA) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT id, nombre, rol
            FROM usuarios
            WHERE activo = 1
            ORDER BY nombre
            """
        ).fetchall()
        return [dict(fila) for fila in filas]


def listar_responsables(ruta_db=RUTA_DB_PREDETERMINADA) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT id, nombre, empresa, cargo
            FROM responsables
            WHERE activo = 1
            ORDER BY nombre
            """
        ).fetchall()
        return [dict(fila) for fila in filas]


def listar_catalogo(tabla: str, ruta_db=RUTA_DB_PREDETERMINADA) -> list[dict]:
    tablas_permitidas = {"partidas", "tipos_problema", "recintos"}
    if tabla not in tablas_permitidas:
        raise ValueError("El catálogo solicitado no existe.")

    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            f"SELECT id, nombre FROM {tabla} ORDER BY nombre"
        ).fetchall()
        return [dict(fila) for fila in filas]


def listar_especialidades() -> list[str]:
    return list(ESPECIALIDADES_V1)


def obtener_partidas_por_especialidad(
    especialidad: str,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    if especialidad not in ESPECIALIDADES_V1:
        raise ValueError("La especialidad seleccionada no existe.")

    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT id, nombre, especialidad
            FROM partidas
            WHERE especialidad = ?
            ORDER BY nombre
            """,
            (especialidad,),
        ).fetchall()
        return [dict(fila) for fila in filas]


def actualizar_especialidad_partida(
    partida_id: int,
    especialidad: str,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> None:
    if especialidad not in ESPECIALIDADES_V1:
        raise ValueError("La especialidad seleccionada no existe.")

    with sesion(ruta_db) as conexion:
        cursor = conexion.execute(
            """
            UPDATE partidas
            SET especialidad = ?
            WHERE id = ?
            """,
            (especialidad, partida_id),
        )
        if cursor.rowcount == 0:
            raise ValueError("La partida seleccionada no existe.")


def obtener_partidas_sin_especialidad_especifica(
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT id, nombre, especialidad
            FROM partidas
            WHERE especialidad = ?
            ORDER BY nombre
            """,
            (ESPECIALIDAD_PREDETERMINADA,),
        ).fetchall()
        return [dict(fila) for fila in filas]


def listar_departamentos_seleccionables(
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT
                d.id,
                o.nombre AS obra,
                t.nombre AS torre,
                d.piso,
                d.numero
            FROM departamentos d
            JOIN torres t ON t.id = d.torre_id
            JOIN obras o ON o.id = t.obra_id
            ORDER BY o.nombre, t.nombre, d.piso, d.numero
            """
        ).fetchall()
        return [dict(fila) for fila in filas]


def crear_tipologia(
    nombre: str,
    recintos: list[str],
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> int:
    """Crea una tipología y su lista ordenada de recintos."""
    nombre = nombre.strip()
    recintos_limpios = []
    vistos = set()
    for recinto in recintos:
        recinto_limpio = recinto.strip()
        if not recinto_limpio:
            continue
        clave = recinto_limpio.casefold()
        if clave not in vistos:
            vistos.add(clave)
            recintos_limpios.append(recinto_limpio)

    if not nombre:
        raise ValueError("El nombre de la tipología es obligatorio.")
    if not recintos_limpios:
        raise ValueError("La tipología debe tener al menos un recinto.")

    with sesion(ruta_db) as conexion:
        cursor = conexion.execute(
            "INSERT INTO tipologias (nombre) VALUES (?)",
            (nombre,),
        )
        tipologia_id = cursor.lastrowid
        conexion.executemany(
            """
            INSERT INTO tipologia_recinto (
                tipologia_id, nombre_recinto, orden
            )
            VALUES (?, ?, ?)
            """,
            [
                (tipologia_id, recinto, orden)
                for orden, recinto in enumerate(recintos_limpios, start=1)
            ],
        )
        return tipologia_id


def listar_tipologias(ruta_db=RUTA_DB_PREDETERMINADA) -> list[dict]:
    """Lista tipologías junto con sus recintos y cantidad de departamentos."""
    with sesion(ruta_db) as conexion:
        tipologias = conexion.execute(
            """
            SELECT
                tip.id,
                tip.nombre,
                COUNT(DISTINCT d.id) AS departamentos_asignados
            FROM tipologias tip
            LEFT JOIN departamentos d ON d.tipologia_id = tip.id
            GROUP BY tip.id, tip.nombre
            ORDER BY tip.nombre
            """
        ).fetchall()

        resultado = []
        for tipologia in tipologias:
            recintos = conexion.execute(
                """
                SELECT nombre_recinto
                FROM tipologia_recinto
                WHERE tipologia_id = ?
                ORDER BY orden, nombre_recinto
                """,
                (tipologia["id"],),
            ).fetchall()
            registro = dict(tipologia)
            registro["recintos"] = [
                recinto["nombre_recinto"] for recinto in recintos
            ]
            resultado.append(registro)
        return resultado


def listar_recintos_tipologia(
    tipologia_id: int,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    """Lista los recintos configurables de una tipología."""
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT id, nombre_recinto AS nombre, orden
            FROM tipologia_recinto
            WHERE tipologia_id = ?
            ORDER BY orden, nombre_recinto
            """,
            (tipologia_id,),
        ).fetchall()
        return [dict(fila) for fila in filas]


def configurar_partidas_tipologia(
    tipologia_recinto_id: int,
    partida_ids: list[int],
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> int:
    """Reemplaza el checklist esperado de un recinto por la selección recibida."""
    ids = list(dict.fromkeys(partida_ids))
    if not ids:
        raise ValueError("Selecciona al menos una partida para el recinto.")

    with sesion(ruta_db) as conexion:
        recinto = conexion.execute(
            "SELECT id FROM tipologia_recinto WHERE id = ?",
            (tipologia_recinto_id,),
        ).fetchone()
        if recinto is None:
            raise ValueError("El recinto seleccionado no existe.")

        marcadores = ",".join("?" for _ in ids)
        partidas_existentes = conexion.execute(
            f"SELECT id FROM partidas WHERE id IN ({marcadores})",
            ids,
        ).fetchall()
        if len(partidas_existentes) != len(ids):
            raise ValueError("Una o más partidas seleccionadas no existen.")

        marcadores_ids = ",".join("?" for _ in ids)
        conexion.execute(
            f"""
            DELETE FROM recinto_partida
            WHERE tipologia_recinto_id = ?
              AND partida_id NOT IN ({marcadores_ids})
            """,
            (tipologia_recinto_id, *ids),
        )
        for orden, partida_id in enumerate(ids, start=1):
            conexion.execute(
                """
                INSERT INTO recinto_partida (
                    tipologia_recinto_id,
                    partida_id,
                    orden,
                    obligatoria
                )
                VALUES (?, ?, ?, 1)
                ON CONFLICT (tipologia_recinto_id, partida_id)
                DO UPDATE SET
                    orden = excluded.orden,
                    obligatoria = 1
                """,
                (tipologia_recinto_id, partida_id, orden),
            )
        return len(ids)


def obtener_checklist_tipologia(
    tipologia_id: int,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    """Devuelve los recintos y partidas esperadas de una tipología."""
    with sesion(ruta_db) as conexion:
        recintos = conexion.execute(
            """
            SELECT id, nombre_recinto AS nombre, orden
            FROM tipologia_recinto
            WHERE tipologia_id = ?
            ORDER BY orden, nombre_recinto
            """,
            (tipologia_id,),
        ).fetchall()

        resultado = []
        for recinto in recintos:
            partidas = conexion.execute(
                """
                SELECT
                    p.id,
                    p.nombre,
                    1 AS obligatoria,
                    rp.peso_avance,
                    rp.id AS recinto_partida_id,
                    rp.orden
                FROM recinto_partida rp
                JOIN partidas p ON p.id = rp.partida_id
                WHERE rp.tipologia_recinto_id = ?
                ORDER BY rp.orden, p.nombre
                """,
                (recinto["id"],),
            ).fetchall()
            registro = dict(recinto)
            registro["partidas"] = [dict(fila) for fila in partidas]
            resultado.append(registro)
        return resultado


def actualizar_configuracion_partida_recinto(
    *,
    recinto_partida_id: int,
    peso_avance: int,
    obligatoria: bool | None = None,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> None:
    """Actualiza peso; la obligatoriedad se deriva de la aplicabilidad."""
    if peso_avance not in {1, 2}:
        raise ValueError("El peso debe ser 1 montaje/terminacion o 2 principal.")

    with sesion(ruta_db) as conexion:
        cursor = conexion.execute(
            """
            UPDATE recinto_partida
            SET peso_avance = ?,
                obligatoria = 1
            WHERE id = ?
            """,
            (peso_avance, recinto_partida_id),
        )
        if cursor.rowcount == 0:
            raise ValueError("La partida del recinto no existe.")


def asegurar_checklist_departamento(
    departamento_id: int,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> int:
    """Materializa en el departamento el checklist definido por su tipología."""
    with sesion(ruta_db) as conexion:
        departamento = conexion.execute(
            "SELECT tipologia_id FROM departamentos WHERE id = ?",
            (departamento_id,),
        ).fetchone()
        if departamento is None:
            raise ValueError("El departamento seleccionado no existe.")
        if departamento["tipologia_id"] is None:
            raise ValueError("El departamento todavía no tiene tipología asignada.")

        conexion.execute(
            """
            INSERT OR IGNORE INTO estado_partida_departamento (
                departamento_id, recinto_partida_id
            )
            SELECT ?, rp.id
            FROM recinto_partida rp
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            WHERE tr.tipologia_id = ?
            """,
            (departamento_id, departamento["tipologia_id"]),
        )
        cantidad = conexion.execute(
            """
            SELECT COUNT(*)
            FROM estado_partida_departamento
            WHERE departamento_id = ?
            """,
            (departamento_id,),
        ).fetchone()[0]
        if cantidad == 0:
            raise ValueError(
                "La tipología no tiene partidas configuradas en sus recintos."
            )
        return cantidad


def obtener_avance_departamento(
    departamento_id: int,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> dict:
    """Devuelve checklist, porcentaje y estado calculado de un departamento."""
    asegurar_checklist_departamento(departamento_id, ruta_db)
    with sesion(ruta_db) as conexion:
        ficha = conexion.execute(
            """
            SELECT
                d.id,
                o.nombre AS obra,
                t.nombre AS torre,
                d.piso,
                d.numero,
                tip.nombre AS tipologia,
                d.etapa_actual,
                d.estado_operativo,
                d.fecha_ultima_revision
            FROM departamentos d
            JOIN torres t ON t.id = d.torre_id
            JOIN obras o ON o.id = t.obra_id
            JOIN tipologias tip ON tip.id = d.tipologia_id
            WHERE d.id = ?
            """,
            (departamento_id,),
        ).fetchone()
        partidas = conexion.execute(
            """
            SELECT
                epd.id AS estado_partida_id,
                tr.nombre_recinto AS recinto,
                p.nombre AS partida,
                p.especialidad AS especialidad,
                epd.estado,
                epd.fecha_ultima_actualizacion,
                1 AS obligatoria,
                rp.peso_avance,
                rp.orden,
                ra.causa,
                resp.nombre AS responsable,
                ra.responsable_id,
                ra.fecha_compromiso,
                ra.comentario
            FROM estado_partida_departamento epd
            JOIN recinto_partida rp ON rp.id = epd.recinto_partida_id
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN partidas p ON p.id = rp.partida_id
            LEFT JOIN restricciones_avance ra
                ON ra.estado_partida_id = epd.id
               AND ra.estado = 'activa'
            LEFT JOIN responsables resp ON resp.id = ra.responsable_id
            WHERE epd.departamento_id = ?
            ORDER BY tr.orden, rp.orden, p.nombre
            """,
            (departamento_id,),
        ).fetchall()

        aplicables = [fila for fila in partidas if fila["estado"] != "no_aplica"]
        peso_total = sum(fila["peso_avance"] for fila in aplicables)
        peso_verificado = sum(
            fila["peso_avance"]
            for fila in aplicables
            if fila["estado"] == "verificada"
        )
        peso_declarado = sum(
            fila["peso_avance"]
            for fila in aplicables
            if fila["estado"] in {"terminada", "verificada"}
        )
        avance_oficial = (
            round(peso_verificado * 100 / peso_total)
            if peso_total
            else 100
        )
        avance_declarado = (
            round(peso_declarado * 100 / peso_total)
            if peso_total
            else 100
        )
        resultado = dict(ficha)
        resultado["avance_porcentaje"] = avance_oficial
        resultado["avance_oficial_porcentaje"] = avance_oficial
        resultado["avance_declarado_porcentaje"] = avance_declarado
        resultado["partidas"] = [dict(fila) for fila in partidas]
        return resultado


def listar_dependencias_criticas(
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT
                id,
                recinto,
                partida,
                dependencia,
                grupo,
                tipo_condicion,
                descripcion,
                activa
            FROM dependencias_criticas_partida
            ORDER BY recinto, partida, grupo, dependencia
            """
        ).fetchall()
        return [dict(fila) for fila in filas]


def crear_dependencia_critica(
    *,
    recinto: str,
    partida: str,
    dependencia: str,
    descripcion: str,
    grupo: int = 1,
    tipo_condicion: str = "AND",
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> int:
    recinto = recinto.strip()
    partida = partida.strip()
    dependencia = dependencia.strip()
    descripcion = descripcion.strip()
    tipo_condicion = tipo_condicion.strip().upper()
    if not recinto:
        raise ValueError("El recinto es obligatorio.")
    if not partida:
        raise ValueError("La partida es obligatoria.")
    if not dependencia:
        raise ValueError("La dependencia es obligatoria.")
    if not descripcion:
        raise ValueError("La descripcion es obligatoria.")
    if grupo < 1:
        raise ValueError("El grupo debe ser mayor o igual a 1.")
    if tipo_condicion not in {"AND", "OR"}:
        raise ValueError("La condicion debe ser AND u OR.")

    with sesion(ruta_db) as conexion:
        conexion.execute(
            """
            INSERT INTO dependencias_criticas_partida (
                recinto,
                partida,
                dependencia,
                grupo,
                tipo_condicion,
                descripcion,
                activa
            )
            VALUES (?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT (recinto, partida, dependencia, grupo)
            DO UPDATE SET
                tipo_condicion = excluded.tipo_condicion,
                descripcion = excluded.descripcion,
                activa = 1
            """,
            (recinto, partida, dependencia, grupo, tipo_condicion, descripcion),
        )
        fila = conexion.execute(
            """
            SELECT id
            FROM dependencias_criticas_partida
            WHERE recinto = ?
              AND partida = ?
              AND dependencia = ?
              AND grupo = ?
            """,
            (recinto, partida, dependencia, grupo),
        ).fetchone()
        return fila["id"]


def desactivar_dependencia_critica(
    dependencia_id: int,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> None:
    with sesion(ruta_db) as conexion:
        cursor = conexion.execute(
            """
            UPDATE dependencias_criticas_partida
            SET activa = 0
            WHERE id = ?
            """,
            (dependencia_id,),
        )
        if cursor.rowcount == 0:
            raise ValueError("La dependencia seleccionada no existe.")


def obtener_dependencias_criticas_partida(
    recinto: str,
    partida: str,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    with sesion(ruta_db) as conexion:
        for recinto_fuente in _recintos_fuente_dependencias(recinto):
            filas = conexion.execute(
                """
                SELECT
                    recinto,
                    partida,
                    dependencia,
                    grupo,
                    tipo_condicion,
                    descripcion
                FROM dependencias_criticas_partida
                WHERE activa = 1
                  AND lower(recinto) = lower(?)
                  AND lower(partida) = lower(?)
                ORDER BY grupo, dependencia
                """,
                (recinto_fuente, partida),
            ).fetchall()
            if filas:
                resultado = [dict(fila) for fila in filas]
                for dependencia in resultado:
                    dependencia["recinto_evaluado"] = recinto
                return resultado
        return []


def obtener_advertencias_dependencias_departamento(
    departamento_id: int,
    estado_partida_ids: list[int] | None = None,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    """Advierte dependencias criticas no cumplidas sin bloquear acciones."""
    asegurar_checklist_departamento(departamento_id, ruta_db)
    ids_filtrados = set(estado_partida_ids or [])
    estados_cumplidos = {"terminada", "verificada"}

    with sesion(ruta_db) as conexion:
        partidas = [
            dict(fila)
            for fila in conexion.execute(
                """
                SELECT
                    epd.id AS estado_partida_id,
                    tr.nombre_recinto AS recinto,
                    p.nombre AS partida,
                    epd.estado,
                    rp.peso_avance
                FROM estado_partida_departamento epd
                JOIN recinto_partida rp ON rp.id = epd.recinto_partida_id
                JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
                JOIN partidas p ON p.id = rp.partida_id
                WHERE epd.departamento_id = ?
                """,
                (departamento_id,),
            ).fetchall()
        ]
        dependencias = [
            dict(fila)
            for fila in conexion.execute(
                """
                SELECT
                    recinto,
                    partida,
                    dependencia,
                    grupo,
                    tipo_condicion,
                    descripcion
                FROM dependencias_criticas_partida
                WHERE activa = 1
                """
            ).fetchall()
        ]

    partidas_por_clave = {
        (_normalizar_texto(partida["recinto"]), _normalizar_texto(partida["partida"])): partida
        for partida in partidas
    }
    advertencias = []
    for partida in partidas:
        if ids_filtrados and partida["estado_partida_id"] not in ids_filtrados:
            continue
        if partida["estado"] in {"terminada", "verificada", "no_aplica"}:
            continue

        reglas_partida = _resolver_reglas_dependencia(
            dependencias,
            partida["recinto"],
            partida["partida"],
        )
        for reglas_grupo in _agrupar_reglas_dependencia(reglas_partida):
            tipo_condicion = reglas_grupo[0].get("tipo_condicion", "AND")
            if tipo_condicion == "OR":
                advertencia = _evaluar_grupo_dependencias_or(
                    partida,
                    reglas_grupo,
                    partidas_por_clave,
                    estados_cumplidos,
                )
                if advertencia:
                    advertencias.append(advertencia)
                continue

            advertencias.extend(
                _evaluar_grupo_dependencias_and(
                    partida,
                    reglas_grupo,
                    partidas,
                    partidas_por_clave,
                    estados_cumplidos,
                )
            )
    return advertencias


def _agrupar_reglas_dependencia(reglas: list[dict]) -> list[list[dict]]:
    grupos: dict[tuple[int, str], list[dict]] = {}
    for regla in reglas:
        tipo_condicion = str(regla.get("tipo_condicion") or "AND").upper()
        clave = (regla["grupo"], tipo_condicion)
        grupos.setdefault(clave, []).append(regla)
    return list(grupos.values())


def _evaluar_grupo_dependencias_and(
    partida: dict,
    reglas: list[dict],
    partidas: list[dict],
    partidas_por_clave: dict,
    estados_cumplidos: set[str],
) -> list[dict]:
    advertencias = []
    for dependencia in reglas:
        if dependencia["dependencia"] == DEPENDENCIA_TODAS_PRINCIPALES:
            principales_pendientes = [
                item
                for item in partidas
                if item["recinto"] == partida["recinto"]
                and item["estado_partida_id"] != partida["estado_partida_id"]
                and item["peso_avance"] == 2
                and item["estado"] not in estados_cumplidos
                and item["estado"] != "no_aplica"
            ]
            if principales_pendientes:
                advertencias.append(
                    {
                        "recinto": partida["recinto"],
                        "partida": partida["partida"],
                        "dependencia": dependencia["descripcion"],
                        "estado_dependencia": "pendiente",
                        "detalle": (
                            "Partidas principales pendientes: "
                            + ", ".join(
                                item["partida"] for item in principales_pendientes
                            )
                        ),
                    }
                )
            continue

        dependencia_partida = partidas_por_clave.get(
            (
                _normalizar_texto(partida["recinto"]),
                _normalizar_texto(dependencia["dependencia"]),
            )
        )
        if dependencia_partida is None:
            continue
        if dependencia_partida["estado"] not in estados_cumplidos:
            advertencias.append(
                {
                    "recinto": partida["recinto"],
                    "partida": partida["partida"],
                    "dependencia": dependencia["dependencia"],
                    "estado_dependencia": dependencia_partida["estado"],
                    "detalle": dependencia["descripcion"],
                }
            )
    return advertencias


def _evaluar_grupo_dependencias_or(
    partida: dict,
    reglas: list[dict],
    partidas_por_clave: dict,
    estados_cumplidos: set[str],
) -> dict | None:
    alternativas = []
    for dependencia in reglas:
        dependencia_partida = partidas_por_clave.get(
            (
                _normalizar_texto(partida["recinto"]),
                _normalizar_texto(dependencia["dependencia"]),
            )
        )
        if dependencia_partida is None:
            continue
        alternativas.append((dependencia, dependencia_partida))

    if not alternativas:
        return None
    if any(
        dependencia_partida["estado"] in estados_cumplidos
        for _, dependencia_partida in alternativas
    ):
        return None

    dependencias = " OR ".join(
        dependencia["dependencia"] for dependencia, _ in alternativas
    )
    descripcion = reglas[0]["descripcion"]
    return {
        "recinto": partida["recinto"],
        "partida": partida["partida"],
        "dependencia": dependencias,
        "estado_dependencia": "pendiente",
        "detalle": descripcion,
    }


def _normalizar_texto(texto: str) -> str:
    return str(texto).strip().casefold()


def _resolver_reglas_dependencia(
    dependencias: list[dict],
    recinto: str,
    partida: str,
) -> list[dict]:
    for recinto_fuente in _recintos_fuente_dependencias(recinto):
        reglas = [
            dependencia
            for dependencia in dependencias
            if _normalizar_texto(dependencia["recinto"]) == _normalizar_texto(recinto_fuente)
            and _normalizar_texto(dependencia["partida"]) == _normalizar_texto(partida)
        ]
        if reglas:
            return reglas
    return []


def _recintos_fuente_dependencias(recinto: str) -> list[str]:
    herencias = {
        "walk-in closet": "Dormitorio",
        "baño 2": "Baño Principal",
    }
    recinto_limpio = str(recinto).strip()
    base = herencias.get(recinto_limpio.casefold())
    if base is None:
        return [recinto_limpio]
    return [recinto_limpio, base]


def _recalcular_estado_operativo(
    conexion,
    departamento_id: int,
) -> str:
    partidas = [
        dict(fila)
        for fila in conexion.execute(
            """
            SELECT epd.estado
            FROM estado_partida_departamento epd
            WHERE epd.departamento_id = ?
            """,
            (departamento_id,),
        ).fetchall()
    ]
    estados = [partida["estado"] for partida in partidas]
    bloqueos_restriccion = conexion.execute(
        """
        SELECT COUNT(*)
        FROM restricciones
        WHERE departamento_id = ?
          AND estado <> 'Verificado'
          AND bloquea_entrega = 1
        """,
        (departamento_id,),
    ).fetchone()[0]
    bloqueos_partida = conexion.execute(
        """
        SELECT COUNT(*)
        FROM restricciones_avance ra
        JOIN estado_partida_departamento epd
            ON epd.id = ra.estado_partida_id
        WHERE epd.departamento_id = ?
          AND ra.estado = 'activa'
        """,
        (departamento_id,),
    ).fetchone()[0]

    if not estados or all(estado == "no_iniciada" for estado in estados):
        estado_operativo = "sin_revisar"
    elif "bloqueada" in estados or bloqueos_restriccion or bloqueos_partida:
        estado_operativo = "bloqueado"
    elif "observada" in estados:
        estado_operativo = "observado"
    else:
        aplicables = [
            partida for partida in partidas if partida["estado"] != "no_aplica"
        ]
        if aplicables and all(partida["estado"] == "verificada" for partida in aplicables):
            estado_operativo = "liberable"
        else:
            estado_operativo = "en_proceso"

    conexion.execute(
        """
        UPDATE departamentos
        SET estado_operativo = ?,
            fecha_ultima_revision = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (estado_operativo, departamento_id),
    )
    return estado_operativo


def actualizar_estado_partida(
    *,
    estado_partida_id: int,
    nuevo_estado: str,
    usuario_id: int,
    causa: str = "",
    responsable_id: int | None = None,
    fecha_compromiso: date | None = None,
    comentario: str = "",
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> str:
    """Actualiza una partida y crea/cierra su restricción cuando corresponde."""
    estados_validos = {
        "no_iniciada",
        "en_proceso",
        "terminada",
        "observada",
        "bloqueada",
        "verificada",
        "no_aplica",
    }
    if nuevo_estado not in estados_validos:
        raise ValueError("El estado de partida seleccionado no es válido.")

    with sesion(ruta_db) as conexion:
        usuario = conexion.execute(
            "SELECT id, rol FROM usuarios WHERE id = ? AND activo = 1",
            (usuario_id,),
        ).fetchone()
        if usuario is None:
            raise ValueError("El usuario seleccionado no existe o está inactivo.")
        if usuario["rol"] == "Solo lectura":
            raise ValueError("El usuario solo lectura no puede modificar informacion.")
        estados_supervisor = {
            "no_iniciada",
            "en_proceso",
            "terminada",
            "observada",
            "bloqueada",
        }
        if usuario["rol"] != "Administrador" and nuevo_estado not in estados_supervisor:
            raise ValueError("Solo un administrador puede verificar o marcar no aplica.")

        partida = conexion.execute(
            """
            SELECT id, departamento_id, recinto_partida_id, estado
            FROM estado_partida_departamento
            WHERE id = ?
            """,
            (estado_partida_id,),
        ).fetchone()
        if partida is None:
            raise ValueError("La partida seleccionada no existe.")

        orden_estados = {
            "no_iniciada": 0,
            "en_proceso": 1,
            "observada": 2,
            "bloqueada": 2,
            "terminada": 3,
            "verificada": 4,
            "no_aplica": 4,
        }
        estado_anterior = partida["estado"]
        es_retroceso = orden_estados[nuevo_estado] < orden_estados[estado_anterior]
        if es_retroceso and usuario["rol"] != "Administrador":
            raise ValueError("Solo un administrador puede retroceder estados.")

        if nuevo_estado == "bloqueada":
            if not causa.strip():
                raise ValueError("La causa es obligatoria al bloquear una partida.")
            if responsable_id is None:
                raise ValueError(
                    "El responsable es obligatorio al bloquear una partida."
                )
            if fecha_compromiso is None:
                raise ValueError(
                    "La fecha compromiso es obligatoria al bloquear una partida."
                )
            if not comentario.strip():
                raise ValueError(
                    "El comentario es obligatorio al bloquear una partida."
                )
        if nuevo_estado == "observada" and not comentario.strip():
            raise ValueError("El comentario es obligatorio al observar una partida.")

        conexion.execute(
            """
            UPDATE estado_partida_departamento
            SET estado = ?,
                actualizado_por_usuario_id = ?,
                fecha_ultima_actualizacion = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (nuevo_estado, usuario_id, estado_partida_id),
        )

        conexion.execute(
            """
            INSERT INTO historial_partida_departamento (
                estado_partida_id,
                departamento_id,
                recinto_partida_id,
                usuario_id,
                estado_anterior,
                estado_nuevo,
                comentario
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                estado_partida_id,
                partida["departamento_id"],
                partida["recinto_partida_id"],
                usuario_id,
                estado_anterior,
                nuevo_estado,
                comentario.strip() or None,
            ),
        )

        if nuevo_estado == "bloqueada":
            conexion.execute(
                """
                INSERT INTO restricciones_avance (
                    estado_partida_id,
                    causa,
                    responsable_id,
                    fecha_compromiso,
                    comentario,
                    estado,
                    fecha_cierre
                )
                VALUES (?, ?, ?, ?, ?, 'activa', NULL)
                ON CONFLICT (estado_partida_id)
                DO UPDATE SET
                    causa = excluded.causa,
                    responsable_id = excluded.responsable_id,
                    fecha_compromiso = excluded.fecha_compromiso,
                    comentario = excluded.comentario,
                    estado = 'activa',
                    fecha_cierre = NULL
                """,
                (
                    estado_partida_id,
                    causa.strip(),
                    responsable_id,
                    fecha_compromiso.isoformat(),
                    comentario.strip() or None,
                ),
            )
        else:
            conexion.execute(
                """
                UPDATE restricciones_avance
                SET estado = 'cerrada',
                    fecha_cierre = CURRENT_TIMESTAMP
                WHERE estado_partida_id = ?
                  AND estado = 'activa'
                """,
                (estado_partida_id,),
            )

        return _recalcular_estado_operativo(
            conexion,
            partida["departamento_id"],
        )


def actualizar_estados_partidas(
    *,
    estado_partida_ids: list[int],
    nuevo_estado: str,
    usuario_id: int,
    causa: str = "",
    responsable_id: int | None = None,
    fecha_compromiso: date | None = None,
    comentario: str = "",
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> dict:
    """Aplica el mismo cambio de estado a varias partidas."""
    ids = list(dict.fromkeys(estado_partida_ids))
    if not ids:
        raise ValueError("Selecciona al menos una partida.")

    estados_departamento = []
    for estado_partida_id in ids:
        estado_operativo = actualizar_estado_partida(
            estado_partida_id=estado_partida_id,
            nuevo_estado=nuevo_estado,
            usuario_id=usuario_id,
            causa=causa,
            responsable_id=responsable_id,
            fecha_compromiso=fecha_compromiso,
            comentario=comentario,
            ruta_db=ruta_db,
        )
        estados_departamento.append(estado_operativo)

    return {
        "actualizadas": len(ids),
        "estado_operativo": estados_departamento[-1],
    }


def obtener_historial_partidas_departamento(
    departamento_id: int,
    limite: int = 30,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT
                h.fecha,
                u.nombre AS usuario,
                u.rol,
                h.estado_anterior,
                h.estado_nuevo,
                h.comentario,
                tr.nombre_recinto AS recinto,
                p.nombre AS partida
            FROM historial_partida_departamento h
            JOIN usuarios u ON u.id = h.usuario_id
            JOIN recinto_partida rp ON rp.id = h.recinto_partida_id
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN partidas p ON p.id = rp.partida_id
            WHERE h.departamento_id = ?
            ORDER BY h.fecha DESC, h.id DESC
            LIMIT ?
            """,
            (departamento_id, limite),
        ).fetchall()
        return [dict(fila) for fila in filas]


def asignar_tipologia_departamento(
    departamento_id: int,
    tipologia_id: int,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> None:
    """Asocia un departamento existente con una tipología."""
    with sesion(ruta_db) as conexion:
        cursor = conexion.execute(
            """
            UPDATE departamentos
            SET tipologia_id = ?
            WHERE id = ?
            """,
            (tipologia_id, departamento_id),
        )
        if cursor.rowcount == 0:
            raise ValueError("El departamento seleccionado no existe.")


def asignar_tipologia_departamentos(
    departamento_ids: list[int],
    tipologia_id: int,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> int:
    """Asigna una tipología a varios departamentos en una sola operación."""
    ids = list(dict.fromkeys(departamento_ids))
    if not ids:
        raise ValueError("Selecciona al menos un departamento.")

    with sesion(ruta_db) as conexion:
        tipologia = conexion.execute(
            "SELECT id FROM tipologias WHERE id = ?",
            (tipologia_id,),
        ).fetchone()
        if tipologia is None:
            raise ValueError("La tipología seleccionada no existe.")

        marcadores = ",".join("?" for _ in ids)
        existentes = conexion.execute(
            f"SELECT id FROM departamentos WHERE id IN ({marcadores})",
            ids,
        ).fetchall()
        if len(existentes) != len(ids):
            raise ValueError("Uno o más departamentos no existen.")

        conexion.executemany(
            """
            UPDATE departamentos
            SET tipologia_id = ?
            WHERE id = ?
            """,
            ((tipologia_id, departamento_id) for departamento_id in ids),
        )
        return len(ids)


def obtener_ficha_departamento(
    departamento_id: int,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> dict:
    """Devuelve identidad, situación operativa, recintos y casos activos."""
    with sesion(ruta_db) as conexion:
        departamento = conexion.execute(
            """
            SELECT
                d.id,
                o.nombre AS obra,
                t.nombre AS torre,
                d.piso,
                d.numero,
                d.tipologia_id,
                tip.nombre AS tipologia,
                d.etapa_actual,
                d.estado_operativo,
                d.fecha_objetivo_preentrega,
                d.fecha_objetivo_entrega,
                d.fecha_ultima_revision
            FROM departamentos d
            JOIN torres t ON t.id = d.torre_id
            JOIN obras o ON o.id = t.obra_id
            LEFT JOIN tipologias tip ON tip.id = d.tipologia_id
            WHERE d.id = ?
            """,
            (departamento_id,),
        ).fetchone()
        if departamento is None:
            raise ValueError("El departamento seleccionado no existe.")

        recintos = conexion.execute(
            """
            SELECT id, nombre_recinto AS nombre, orden
            FROM tipologia_recinto
            WHERE tipologia_id = ?
            ORDER BY orden, nombre_recinto
            """,
            (departamento["tipologia_id"],),
        ).fetchall()
        observaciones_activas = conexion.execute(
            """
            SELECT
                r.id,
                pm.titulo,
                rec.nombre AS recinto,
                p.nombre AS partida,
                tp.nombre AS tipo,
                resp.nombre AS responsable,
                r.estado,
                r.fecha_compromiso,
                r.comentario_corto AS descripcion,
                r.bloquea_entrega
            FROM restricciones r
            JOIN problemas_madre pm ON pm.id = r.problema_madre_id
            JOIN recintos rec ON rec.id = r.recinto_id
            JOIN partidas p ON p.id = pm.partida_id
            JOIN tipos_problema tp ON tp.id = pm.tipo_problema_id
            JOIN responsables resp ON resp.id = pm.responsable_id
            WHERE r.departamento_id = ?
              AND r.estado <> 'Verificado'
            ORDER BY r.bloquea_entrega DESC, r.fecha_compromiso
            """,
            (departamento_id,),
        ).fetchall()

        ficha = dict(departamento)
        ficha["recintos"] = [dict(fila) for fila in recintos]
        ficha["observaciones_activas"] = [
            dict(fila) for fila in observaciones_activas
        ]
        return ficha


def crear_problema(
    *,
    titulo: str,
    partida_id: int,
    tipo_problema_id: int,
    responsable_id: int,
    creado_por_usuario_id: int,
    departamento_ids: list[int],
    recinto_id: int,
    fecha_deteccion: date,
    fecha_compromiso: date,
    comentario_corto: str,
    requiere_retrabajo: bool,
    afecta_funcionalidad: bool,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> int:
    titulo = titulo.strip()
    comentario_corto = comentario_corto.strip()
    departamento_ids = list(dict.fromkeys(departamento_ids))

    if not titulo:
        raise ValueError("El título del problema es obligatorio.")
    if not comentario_corto:
        raise ValueError("El comentario corto es obligatorio.")
    if not departamento_ids:
        raise ValueError("Selecciona al menos un departamento.")
    if fecha_compromiso < fecha_deteccion:
        raise ValueError(
            "La fecha compromiso no puede ser anterior a la fecha de detección."
        )

    with sesion(ruta_db) as conexion:
        tipo = conexion.execute(
            """
            SELECT nombre
            FROM tipos_problema
            WHERE id = ?
            """,
            (tipo_problema_id,),
        ).fetchone()
        if tipo is None:
            raise ValueError("El tipo de problema seleccionado no existe.")

        bloquea_entrega = int(
            calcular_bloqueo(
                tipo["nombre"],
                requiere_retrabajo,
                afecta_funcionalidad,
            )
        )
        cursor = conexion.execute(
            """
            INSERT INTO problemas_madre (
                titulo,
                partida_id,
                tipo_problema_id,
                responsable_id,
                creado_por_usuario_id
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                titulo,
                partida_id,
                tipo_problema_id,
                responsable_id,
                creado_por_usuario_id,
            ),
        )
        problema_id = cursor.lastrowid
        conexion.executemany(
            """
            INSERT INTO restricciones (
                problema_madre_id,
                departamento_id,
                recinto_id,
                fecha_deteccion,
                fecha_compromiso,
                comentario_corto,
                requiere_retrabajo,
                afecta_funcionalidad,
                bloquea_entrega
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    problema_id,
                    departamento_id,
                    recinto_id,
                    fecha_deteccion.isoformat(),
                    fecha_compromiso.isoformat(),
                    comentario_corto,
                    int(requiere_retrabajo),
                    int(afecta_funcionalidad),
                    bloquea_entrega,
                )
                for departamento_id in departamento_ids
            ],
        )
        return problema_id


def listar_problemas(ruta_db=RUTA_DB_PREDETERMINADA) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT
                ep.problema_madre_id AS id,
                ep.titulo,
                p.nombre AS partida,
                tp.nombre AS tipo,
                resp.nombre AS responsable,
                ep.estado,
                ep.departamentos_afectados,
                ep.pendientes_activos,
                MIN(r.fecha_compromiso) AS fecha_compromiso,
                MAX(r.bloquea_entrega) AS bloquea_entrega
            FROM v_estado_problemas_madre ep
            JOIN problemas_madre pm ON pm.id = ep.problema_madre_id
            JOIN partidas p ON p.id = pm.partida_id
            JOIN tipos_problema tp ON tp.id = pm.tipo_problema_id
            JOIN responsables resp ON resp.id = pm.responsable_id
            LEFT JOIN restricciones r ON r.problema_madre_id = pm.id
            GROUP BY
                ep.problema_madre_id,
                ep.titulo,
                p.nombre,
                tp.nombre,
                resp.nombre,
                ep.estado,
                ep.departamentos_afectados,
                ep.pendientes_activos
            ORDER BY
                bloquea_entrega DESC,
                fecha_compromiso,
                ep.problema_madre_id DESC
            """
        ).fetchall()
        return [dict(fila) for fila in filas]


def listar_restricciones(ruta_db=RUTA_DB_PREDETERMINADA) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT
                rd.restriccion_id AS id,
                rd.problema_madre_id AS problema_id,
                rd.titulo,
                rd.torre,
                rd.piso,
                rd.departamento,
                rd.recinto,
                rd.partida,
                rd.tipo_problema AS tipo,
                rd.responsable,
                rd.estado,
                rd.fecha_deteccion,
                rd.fecha_compromiso,
                rd.comentario_corto,
                rd.requiere_retrabajo,
                rd.afecta_funcionalidad,
                rd.bloquea_entrega
            FROM v_restricciones_detalle rd
            ORDER BY
                CASE rd.estado
                    WHEN 'Abierto' THEN 1
                    WHEN 'En gestión' THEN 2
                    WHEN 'Resuelto' THEN 3
                    ELSE 4
                END,
                rd.fecha_compromiso,
                rd.torre,
                rd.piso,
                rd.departamento
            """
        ).fetchall()
        return [dict(fila) for fila in filas]


def obtener_historial_restriccion(
    restriccion_id: int,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT
                a.fecha,
                u.nombre AS usuario,
                u.rol,
                a.estado_resultante AS estado,
                a.comentario
            FROM acciones a
            JOIN usuarios u ON u.id = a.usuario_id
            WHERE a.restriccion_id = ?
            ORDER BY a.fecha DESC, a.id DESC
            """,
            (restriccion_id,),
        ).fetchall()
        return [dict(fila) for fila in filas]


def actualizar_restriccion(
    *,
    restriccion_id: int,
    usuario_id: int,
    nuevo_estado: str,
    fecha_compromiso: date,
    comentario_corto: str,
    nota_seguimiento: str = "",
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> None:
    comentario_corto = comentario_corto.strip()
    nota_seguimiento = nota_seguimiento.strip()
    if not comentario_corto:
        raise ValueError("El comentario del caso no puede quedar vacío.")

    transiciones = {
        "Abierto": {"En gestión"},
        "En gestión": {"Resuelto"},
        "Resuelto": {"Verificado"},
        "Verificado": set(),
    }

    with sesion(ruta_db) as conexion:
        usuario = conexion.execute(
            "SELECT nombre, rol FROM usuarios WHERE id = ? AND activo = 1",
            (usuario_id,),
        ).fetchone()
        if usuario is None:
            raise ValueError("El usuario seleccionado no existe o está inactivo.")

        if usuario["rol"] == "Solo lectura":
            raise ValueError("El usuario solo lectura no puede modificar informacion.")

        restriccion = conexion.execute(
            """
            SELECT estado, fecha_deteccion
            FROM restricciones
            WHERE id = ?
            """,
            (restriccion_id,),
        ).fetchone()
        if restriccion is None:
            raise ValueError("La restricción seleccionada no existe.")

        estado_actual = restriccion["estado"]
        if nuevo_estado not in transiciones[estado_actual]:
            raise ValueError(
                f"No se puede pasar de {estado_actual} a {nuevo_estado}."
            )
        if nuevo_estado == "Verificado" and usuario["rol"] != "Administrador":
            raise ValueError("Solo un administrador puede verificar el cierre.")
        if fecha_compromiso.isoformat() < restriccion["fecha_deteccion"]:
            raise ValueError(
                "La fecha compromiso no puede ser anterior a la detección."
            )

        es_verificacion = nuevo_estado == "Verificado"
        conexion.execute(
            """
            UPDATE restricciones
            SET estado = ?,
                fecha_compromiso = ?,
                comentario_corto = ?,
                verificado_por_usuario_id = ?,
                fecha_verificacion = CASE
                    WHEN ? = 1 THEN CURRENT_TIMESTAMP
                    ELSE NULL
                END
            WHERE id = ?
            """,
            (
                nuevo_estado,
                fecha_compromiso.isoformat(),
                comentario_corto,
                usuario_id if es_verificacion else None,
                int(es_verificacion),
                restriccion_id,
            ),
        )

        comentario_historial = nota_seguimiento or (
            f"Cambio de estado: {estado_actual} → {nuevo_estado}"
        )
        conexion.execute(
            """
            INSERT INTO acciones (
                restriccion_id,
                usuario_id,
                comentario,
                estado_resultante
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                restriccion_id,
                usuario_id,
                comentario_historial,
                nuevo_estado,
            ),
        )


def obtener_indicadores(ruta_db=RUTA_DB_PREDETERMINADA) -> dict:
    hoy = date.today().isoformat()
    departamentos = listar_departamentos(ruta_db)
    estados = {}
    for departamento in departamentos:
        estado = departamento["estado"]
        estados[estado] = estados.get(estado, 0) + 1

    with sesion(ruta_db) as conexion:
        vencidas_anteriores = conexion.execute(
            """
            SELECT COUNT(*)
            FROM restricciones
            WHERE estado <> 'Verificado'
              AND fecha_compromiso < ?
            """,
            (hoy,),
        ).fetchone()[0]
        vencidas_avance = conexion.execute(
            """
            SELECT COUNT(*)
            FROM restricciones_avance
            WHERE estado = 'activa'
              AND fecha_compromiso < ?
            """,
            (hoy,),
        ).fetchone()[0]

    return {
        "bloqueados": estados.get("Bloqueado", 0),
        "observados": estados.get("Observado no bloqueante", 0),
        "liberables": estados.get("Liberable", 0),
        "vencidas": vencidas_anteriores + vencidas_avance,
    }


def obtener_reporte_pendientes_departamento(
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT
                d.piso AS piso,
                d.numero AS departamento,
                COALESCE(tip.nombre, '') AS tipologia,
                tr.nombre_recinto AS recinto,
                p.nombre AS partida,
                epd.estado,
                p.especialidad AS especialidad,
                COALESCE(resp.nombre, '') AS responsable,
                COALESCE(epd.fecha_ultima_actualizacion, '') AS ultima_actualizacion,
                CASE
                    WHEN epd.fecha_ultima_actualizacion IS NULL THEN ''
                    ELSE CAST(
                        julianday(date('now')) -
                        julianday(date(epd.fecha_ultima_actualizacion))
                        AS INTEGER
                    )
                END AS dias_sin_movimiento,
                COALESCE(ra.comentario, (
                    SELECT h.comentario
                    FROM historial_partida_departamento h
                    WHERE h.estado_partida_id = epd.id
                    ORDER BY h.fecha DESC, h.id DESC
                    LIMIT 1
                ), '') AS comentario
            FROM estado_partida_departamento epd
            JOIN departamentos d ON d.id = epd.departamento_id
            LEFT JOIN tipologias tip ON tip.id = d.tipologia_id
            JOIN recinto_partida rp ON rp.id = epd.recinto_partida_id
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN partidas p ON p.id = rp.partida_id
            LEFT JOIN restricciones_avance ra
                ON ra.estado_partida_id = epd.id
               AND ra.estado = 'activa'
            LEFT JOIN responsables resp ON resp.id = ra.responsable_id
            WHERE epd.estado NOT IN ('verificada', 'no_aplica')
            ORDER BY d.piso, d.numero, tr.orden, rp.orden
            """
        ).fetchall()
        return [dict(fila) for fila in filas]


def obtener_pendientes_por_especialidad(
    especialidad: str | None = None,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    if especialidad is not None and especialidad not in ESPECIALIDADES_V1:
        raise ValueError("La especialidad seleccionada no existe.")

    registros = obtener_reporte_pendientes_departamento(ruta_db)
    if especialidad is None:
        return registros
    return [
        registro
        for registro in registros
        if registro["especialidad"] == especialidad
    ]


def obtener_resumen_pendientes_especialidad(
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    pendientes = obtener_pendientes_por_especialidad(ruta_db=ruta_db)
    resumen = {}
    for pendiente in pendientes:
        especialidad = pendiente["especialidad"]
        registro = resumen.setdefault(
            especialidad,
            {"especialidad": especialidad, "pendientes": 0},
        )
        registro["pendientes"] += 1
    return sorted(
        resumen.values(),
        key=lambda item: (-item["pendientes"], item["especialidad"]),
    )


def obtener_reporte_pendientes_responsable(
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT
                resp.nombre AS responsable,
                COALESCE(resp.empresa, '') AS empresa,
                p.especialidad AS especialidad,
                d.piso,
                d.numero AS departamento,
                tr.nombre_recinto AS recinto,
                p.nombre AS partida,
                epd.estado,
                ra.fecha_compromiso,
                CASE
                    WHEN ra.fecha_compromiso < date('now')
                    THEN CAST(julianday(date('now')) - julianday(ra.fecha_compromiso) AS INTEGER)
                    ELSE 0
                END AS dias_vencido,
                COALESCE(ra.comentario, ra.causa) AS comentario
            FROM restricciones_avance ra
            JOIN estado_partida_departamento epd
                ON epd.id = ra.estado_partida_id
            JOIN departamentos d ON d.id = epd.departamento_id
            JOIN recinto_partida rp ON rp.id = epd.recinto_partida_id
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN partidas p ON p.id = rp.partida_id
            JOIN responsables resp ON resp.id = ra.responsable_id
            WHERE ra.estado = 'activa'
            UNION ALL
            SELECT
                resp.nombre AS responsable,
                COALESCE(resp.empresa, '') AS empresa,
                p.especialidad AS especialidad,
                d.piso,
                d.numero AS departamento,
                rec.nombre AS recinto,
                p.nombre AS partida,
                r.estado,
                r.fecha_compromiso,
                CASE
                    WHEN r.fecha_compromiso < date('now')
                    THEN CAST(julianday(date('now')) - julianday(r.fecha_compromiso) AS INTEGER)
                    ELSE 0
                END AS dias_vencido,
                r.comentario_corto AS comentario
            FROM restricciones r
            JOIN problemas_madre pm ON pm.id = r.problema_madre_id
            JOIN departamentos d ON d.id = r.departamento_id
            JOIN recintos rec ON rec.id = r.recinto_id
            JOIN partidas p ON p.id = pm.partida_id
            JOIN responsables resp ON resp.id = pm.responsable_id
            WHERE r.estado <> 'Verificado'
            ORDER BY responsable, dias_vencido DESC, piso, departamento
            """
        ).fetchall()
        return [dict(fila) for fila in filas]


def obtener_reporte_bloqueos_vencidos(
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT
                d.piso,
                d.numero AS departamento,
                tr.nombre_recinto AS recinto,
                p.nombre AS partida,
                p.especialidad AS especialidad,
                ra.causa,
                resp.nombre AS responsable,
                date(ra.fecha_creacion) AS fecha_deteccion,
                ra.fecha_compromiso,
                CAST(julianday(date('now')) - julianday(ra.fecha_compromiso) AS INTEGER)
                    AS dias_vencido,
                ra.estado
            FROM restricciones_avance ra
            JOIN estado_partida_departamento epd
                ON epd.id = ra.estado_partida_id
            JOIN departamentos d ON d.id = epd.departamento_id
            JOIN recinto_partida rp ON rp.id = epd.recinto_partida_id
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN partidas p ON p.id = rp.partida_id
            JOIN responsables resp ON resp.id = ra.responsable_id
            WHERE ra.estado = 'activa'
              AND ra.fecha_compromiso < date('now')
            UNION ALL
            SELECT
                d.piso,
                d.numero AS departamento,
                rec.nombre AS recinto,
                p.nombre AS partida,
                p.especialidad AS especialidad,
                pm.titulo AS causa,
                resp.nombre AS responsable,
                r.fecha_deteccion,
                r.fecha_compromiso,
                CAST(julianday(date('now')) - julianday(r.fecha_compromiso) AS INTEGER)
                    AS dias_vencido,
                r.estado
            FROM restricciones r
            JOIN problemas_madre pm ON pm.id = r.problema_madre_id
            JOIN departamentos d ON d.id = r.departamento_id
            JOIN recintos rec ON rec.id = r.recinto_id
            JOIN partidas p ON p.id = pm.partida_id
            JOIN responsables resp ON resp.id = pm.responsable_id
            WHERE r.estado <> 'Verificado'
              AND r.bloquea_entrega = 1
              AND r.fecha_compromiso < date('now')
            ORDER BY dias_vencido DESC, piso, departamento
            """
        ).fetchall()
        return [dict(fila) for fila in filas]


def obtener_reporte_avance_piso(ruta_db=RUTA_DB_PREDETERMINADA) -> list[dict]:
    departamentos = obtener_dashboard_departamentos(ruta_db)
    por_piso = {}
    for departamento in departamentos:
        por_piso.setdefault(departamento["piso"], []).append(departamento)

    resultado = []
    for piso, registros in sorted(por_piso.items()):
        total = len(registros)
        resultado.append(
            {
                "piso": piso,
                "total_departamentos": total,
                "avance_oficial": round(
                    sum(item["avance_oficial"] for item in registros) / total
                ),
                "avance_declarado": round(
                    sum(item["avance_declarado"] for item in registros) / total
                ),
                "en_proceso": sum(
                    1 for item in registros if item["estado"] == "En proceso"
                ),
                "bloqueados": sum(
                    1 for item in registros if item["estado"] == "Bloqueado"
                ),
                "liberables": sum(
                    1 for item in registros if item["estado"] == "Liberable"
                ),
                "verificados": sum(
                    1 for item in registros if item["avance_oficial"] == 100
                ),
            }
        )
    return resultado


def obtener_reporte_avance_tipologia(
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    departamentos = obtener_dashboard_departamentos(ruta_db)
    with sesion(ruta_db) as conexion:
        tipologias = {
            fila["id"]: fila["tipologia"]
            for fila in conexion.execute(
                """
                SELECT d.id, COALESCE(tip.nombre, 'Sin tipologia') AS tipologia
                FROM departamentos d
                LEFT JOIN tipologias tip ON tip.id = d.tipologia_id
                """
            ).fetchall()
        }

    por_tipologia = {}
    for departamento in departamentos:
        tipologia = tipologias.get(departamento["id"], "Sin tipologia")
        por_tipologia.setdefault(tipologia, []).append(departamento)

    resultado = []
    for tipologia, registros in sorted(por_tipologia.items()):
        total = len(registros)
        resultado.append(
            {
                "tipologia": tipologia,
                "cantidad_departamentos": total,
                "avance_oficial": round(
                    sum(item["avance_oficial"] for item in registros) / total
                ),
                "avance_declarado": round(
                    sum(item["avance_declarado"] for item in registros) / total
                ),
                "bloqueados": sum(
                    1 for item in registros if item["estado"] == "Bloqueado"
                ),
                "liberables": sum(
                    1 for item in registros if item["estado"] == "Liberable"
                ),
            }
        )
    return resultado


def obtener_reporte_departamentos_liberables(
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    departamentos = [
        departamento
        for departamento in obtener_dashboard_departamentos(ruta_db)
        if departamento["estado"] == "Liberable"
    ]
    if not departamentos:
        return []

    with sesion(ruta_db) as conexion:
        resultado = []
        for departamento in departamentos:
            detalle = conexion.execute(
                """
                SELECT
                    COALESCE(tip.nombre, '') AS tipologia,
                    d.fecha_ultima_revision,
                    SUM(CASE
                        WHEN epd.estado NOT IN ('verificada', 'no_aplica')
                        THEN 1 ELSE 0
                    END) AS pendientes_aplicables
                FROM departamentos d
                LEFT JOIN tipologias tip ON tip.id = d.tipologia_id
                LEFT JOIN estado_partida_departamento epd
                    ON epd.departamento_id = d.id
                WHERE d.id = ?
                GROUP BY d.id, tip.nombre, d.fecha_ultima_revision
                """,
                (departamento["id"],),
            ).fetchone()
            resultado.append(
                {
                    "departamento": departamento["departamento"],
                    "piso": departamento["piso"],
                    "tipologia": detalle["tipologia"],
                    "avance_oficial": departamento["avance_oficial"],
                    "avance_declarado": departamento["avance_declarado"],
                    "pendientes_aplicables": detalle["pendientes_aplicables"] or 0,
                    "ultima_actualizacion": detalle["fecha_ultima_revision"] or "",
                }
            )
    return resultado


def obtener_reporte_historial(
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT
                date(h.fecha) AS fecha,
                time(h.fecha) AS hora,
                u.nombre AS usuario,
                d.numero AS departamento,
                tr.nombre_recinto AS recinto,
                p.nombre AS partida,
                COALESCE(h.estado_anterior, '') AS estado_anterior,
                h.estado_nuevo,
                COALESCE(h.comentario, '') AS comentario
            FROM historial_partida_departamento h
            JOIN usuarios u ON u.id = h.usuario_id
            JOIN departamentos d ON d.id = h.departamento_id
            JOIN recinto_partida rp ON rp.id = h.recinto_partida_id
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN partidas p ON p.id = rp.partida_id
            ORDER BY h.fecha DESC, h.id DESC
            """
        ).fetchall()
        return [dict(fila) for fila in filas]


def obtener_partidas_sin_movimiento(
    dias: int = 7,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    with sesion(ruta_db) as conexion:
        filas = conexion.execute(
            """
            SELECT
                d.piso,
                d.numero AS departamento,
                tr.nombre_recinto AS recinto,
                p.nombre AS partida,
                epd.estado,
                epd.fecha_ultima_actualizacion,
                CAST(
                    julianday(date('now')) -
                    julianday(date(epd.fecha_ultima_actualizacion))
                    AS INTEGER
                ) AS dias_sin_movimiento
            FROM estado_partida_departamento epd
            JOIN departamentos d ON d.id = epd.departamento_id
            JOIN recinto_partida rp ON rp.id = epd.recinto_partida_id
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN partidas p ON p.id = rp.partida_id
            WHERE epd.estado NOT IN ('verificada', 'no_aplica')
              AND epd.fecha_ultima_actualizacion IS NOT NULL
              AND date(epd.fecha_ultima_actualizacion) <= date('now', ?)
            ORDER BY dias_sin_movimiento DESC, d.piso, d.numero
            LIMIT 20
            """,
            (f"-{int(dias)} day",),
        ).fetchall()
        return [dict(fila) for fila in filas]


def obtener_actividad_reciente(
    limite: int = 10,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[dict]:
    return obtener_reporte_historial(ruta_db)[:limite]


def obtener_recomendaciones_operativas(
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> list[str]:
    resumen = obtener_resumen_dashboard(ruta_db)
    bloqueos_vencidos = obtener_reporte_bloqueos_vencidos(ruta_db)
    liberables = obtener_reporte_departamentos_liberables(ruta_db)
    sin_movimiento = obtener_partidas_sin_movimiento(ruta_db=ruta_db)
    pendientes_especialidad = obtener_resumen_pendientes_especialidad(ruta_db)

    recomendaciones = []
    if bloqueos_vencidos:
        recomendaciones.append(
            f"Resolver {len(bloqueos_vencidos)} bloqueos vencidos antes de liberar departamentos."
        )
    if liberables:
        recomendaciones.append(
            f"Revisar {len(liberables)} departamentos liberables para cierre administrativo."
        )
    if sin_movimiento:
        recomendaciones.append(
            f"Revisar {len(sin_movimiento)} partidas sin movimiento en el umbral operativo."
        )
    if resumen["bloqueados"] > resumen["liberables"]:
        recomendaciones.append(
            "Priorizar responsables de departamentos bloqueados sobre nuevas verificaciones."
        )
    if pendientes_especialidad:
        principal = pendientes_especialidad[0]
        recomendaciones.append(
            f"Priorizar especialidad {principal['especialidad']} con {principal['pendientes']} pendientes."
        )
    return recomendaciones


def liberar_departamento(
    *,
    departamento_id: int,
    usuario_id: int,
    comentario: str,
    ruta_db=RUTA_DB_PREDETERMINADA,
) -> None:
    comentario = comentario.strip()
    if not comentario:
        raise ValueError("El comentario de liberacion es obligatorio.")

    with sesion(ruta_db) as conexion:
        usuario = conexion.execute(
            "SELECT rol FROM usuarios WHERE id = ? AND activo = 1",
            (usuario_id,),
        ).fetchone()
        if usuario is None:
            raise ValueError("El usuario seleccionado no existe o esta inactivo.")
        if usuario["rol"] != "Administrador":
            raise ValueError("Solo un administrador puede liberar departamentos.")

        bloqueos_restriccion = conexion.execute(
            """
            SELECT COUNT(*)
            FROM restricciones
            WHERE departamento_id = ?
              AND estado <> 'Verificado'
              AND bloquea_entrega = 1
            """,
            (departamento_id,),
        ).fetchone()[0]
        bloqueos_partida = conexion.execute(
            """
            SELECT COUNT(*)
            FROM restricciones_avance ra
            JOIN estado_partida_departamento epd
                ON epd.id = ra.estado_partida_id
            WHERE epd.departamento_id = ?
              AND ra.estado = 'activa'
            """,
            (departamento_id,),
        ).fetchone()[0]
        observaciones = conexion.execute(
            """
            SELECT COUNT(*)
            FROM estado_partida_departamento epd
            WHERE epd.departamento_id = ?
              AND epd.estado = 'observada'
            """,
            (departamento_id,),
        ).fetchone()[0]
        aplicables_pendientes = conexion.execute(
            """
            SELECT COUNT(*)
            FROM estado_partida_departamento epd
            WHERE epd.departamento_id = ?
              AND epd.estado NOT IN ('verificada', 'no_aplica')
            """,
            (departamento_id,),
        ).fetchone()[0]

        if bloqueos_restriccion or bloqueos_partida:
            raise ValueError("No se puede liberar con bloqueos activos.")
        if observaciones:
            raise ValueError("No se puede liberar con observaciones bloqueantes.")
        if aplicables_pendientes:
            raise ValueError(
                "No se puede liberar con partidas aplicables sin verificar."
            )

        conexion.execute(
            """
            INSERT INTO liberaciones_departamento (
                departamento_id,
                usuario_id,
                comentario
            )
            VALUES (?, ?, ?)
            """,
            (departamento_id, usuario_id, comentario),
        )
