"""Interfaz web de Control Obra Pro."""

import sqlite3
from datetime import date, timedelta
from html import escape
from io import BytesIO

import pandas as pd
import streamlit as st

from database.cargar_configuracion_v1 import cargar_configuracion_v1
from database.servicios import (
    actualizar_estado_partida,
    actualizar_configuracion_partida_recinto,
    actualizar_estados_partidas,
    asignar_tipologia_departamentos,
    configurar_partidas_tipologia,
    crear_dependencia_critica,
    crear_departamentos,
    crear_obra,
    crear_responsable,
    crear_torre,
    crear_tipologia,
    crear_usuario,
    crear_problema,
    desactivar_dependencia_critica,
    actualizar_restriccion,
    listar_catalogo,
    listar_departamentos,
    listar_departamentos_seleccionables,
    listar_dependencias_criticas,
    listar_especialidades,
    listar_obras,
    listar_problemas,
    listar_recintos_tipologia,
    listar_restricciones,
    listar_responsables,
    listar_torres,
    listar_tipologias,
    listar_usuarios,
    liberar_departamento,
    obtener_actividad_reciente,
    obtener_advertencias_dependencias_departamento,
    obtener_dashboard_departamentos,
    obtener_ficha_dashboard_departamento,
    obtener_historial_partidas_departamento,
    obtener_historial_restriccion,
    obtener_plantilla_importacion_avance,
    obtener_checklist_tipologia,
    obtener_avance_departamento,
    obtener_indicadores,
    obtener_partidas_sin_movimiento,
    obtener_pendientes_por_especialidad,
    obtener_dependencias_criticas_partida,
    obtener_recomendaciones_operativas,
    obtener_reporte_avance_piso,
    obtener_reporte_avance_tipologia,
    obtener_reporte_bloqueos_vencidos,
    obtener_reporte_departamentos_liberables,
    obtener_reporte_historial,
    obtener_reporte_pendientes_departamento,
    obtener_reporte_pendientes_responsable,
    obtener_resumen_dashboard,
    obtener_resumen_pisos,
    obtener_resumen_pendientes_especialidad,
    obtener_resumen_configuracion,
    importar_avance_desde_filas,
    preparar_base,
)
from presentacion import clave_numero_departamento, estado_corto, nombre_del_nivel


st.set_page_config(
    page_title="CopBuilder",
    page_icon="COP",
    layout="wide",
)

preparar_base()


ETIQUETAS_ESTADO_PARTIDA = {
    "No iniciada": "no_iniciada",
    "En proceso": "en_proceso",
    "Terminada": "terminada",
    "Observada": "observada",
    "Bloqueada": "bloqueada",
    "Verificada": "verificada",
    "No aplica": "no_aplica",
}
ETIQUETA_POR_ESTADO_PARTIDA = {
    valor: etiqueta for etiqueta, valor in ETIQUETAS_ESTADO_PARTIDA.items()
}

ORDEN_OPERATIVO_RECINTOS = [
    "Living - Comedor",
    "Living",
    "Cocina",
    "Dormitorio Principal",
    "Walk-in Closet",
    "Baño Principal",
    "Baño Principal",
    "Baño 2",
    "Baño 2",
    "Dormitorio 1",
    "Dormitorio 2",
    "Baño Común",
    "Baño Común",
    "Baño 1",
    "Baño 1",
    "Terraza Principal",
    "Terraza Suite",
]
ORDEN_RECINTO = {
    nombre.casefold(): indice
    for indice, nombre in enumerate(ORDEN_OPERATIVO_RECINTOS)
}


def obtener_usuario_activo() -> dict | None:
    usuarios = listar_usuarios()
    if not usuarios:
        return None

    usuario_por_id = {usuario["id"]: usuario for usuario in usuarios}
    ids = list(usuario_por_id)
    usuario_id_actual = st.session_state.get("usuario_activo_id")
    indice = ids.index(usuario_id_actual) if usuario_id_actual in ids else 0
    usuario_id = st.sidebar.selectbox(
        "Usuario activo",
        ids,
        index=indice,
        format_func=lambda identificador: (
            f'{usuario_por_id[identificador]["nombre"]} · '
            f'{usuario_por_id[identificador]["rol"]}'
        ),
    )
    st.session_state["usuario_activo_id"] = usuario_id
    return usuario_por_id[usuario_id]


def es_solo_lectura(usuario: dict | None) -> bool:
    return usuario is not None and usuario["rol"] == "Solo lectura"


def descargar_csv(registros: list[dict], nombre_archivo: str):
    if not registros:
        return
    csv = pd.DataFrame(registros).to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Descargar CSV",
        data=csv,
        file_name=nombre_archivo,
        mime="text/csv",
        width="stretch",
    )


def crear_excel_descarga(registros: list[dict]) -> bytes:
    salida = BytesIO()
    with pd.ExcelWriter(salida, engine="openpyxl") as escritor:
        pd.DataFrame(registros).to_excel(
            escritor,
            index=False,
            sheet_name="avance",
        )
    return salida.getvalue()


def mostrar_marca_sidebar():
    st.sidebar.markdown(
        """
        <div class="cop-sidebar-brand">
            <div class="cop-sidebar-logo">CopBuilder</div>
            <div class="cop-sidebar-subtitle">Construction Operations Platform</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mostrar_inicio():
    usuario = st.session_state.get("usuario_activo")
    departamentos = obtener_dashboard_departamentos()
    resumen_dashboard = obtener_resumen_dashboard()
    pendientes_verificar = [
        departamento
        for departamento in departamentos
        if departamento["avance_declarado"] > departamento["avance_oficial"]
    ]
    avance_alto = [
        departamento
        for departamento in departamentos
        if departamento["estado"] != "Liberable"
        and departamento["avance_declarado"] >= 80
    ]

    obra_activa = departamentos[0]["obra"] if departamentos else "Sin obra activa"
    torre_activa = departamentos[0]["torre"] if departamentos else "Sin torre activa"
    usuario_activo = usuario["nombre"] if usuario else "Sin usuario activo"

    st.markdown(
        f"""
        <section class="cop-hero">
            <div>
                <span class="cop-kicker">Centro de Operaciones</span>
                <h1>CopBuilder</h1>
                <p>Prioridad diaria para avance, verificación y bloqueos.</p>
            </div>
            <div class="cop-context-grid">
                <div><span>Obra activa</span><strong>{escape(obra_activa)}</strong></div>
                <div><span>Torre activa</span><strong>{escape(torre_activa)}</strong></div>
                <div><span>Usuario activo</span><strong>{escape(usuario_activo)}</strong></div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    resumen = obtener_resumen_configuracion()
    if not resumen["departamentos"]:
        st.info(
            "La base está limpia. Comienza en Configuración cargando la obra, "
            "la torre piloto y sus departamentos."
        )

    if not departamentos:
        st.write("Todavía no hay departamentos registrados.")
        return

    st.subheader("Acciones prioritarias")
    acciones = [
        {
            "titulo": "Pendientes de verificar",
            "valor": len(pendientes_verificar),
            "detalle": "Departamentos con avance declarado mayor al oficial.",
            "accion": "Revisar y verificar partidas terminadas.",
        },
        {
            "titulo": "Departamentos bloqueados",
            "valor": resumen_dashboard["bloqueados"],
            "detalle": "Departamentos con bloqueo activo o restricción bloqueante.",
            "accion": "Resolver responsable, causa y compromiso.",
        },
        {
            "titulo": "Avance alto",
            "valor": len(avance_alto),
            "detalle": "Departamentos con avance declarado sobre 80%.",
            "accion": "Priorizar revisión para cierre operativo.",
        },
    ]
    columnas_acciones = st.columns(3)
    for columna, accion in zip(columnas_acciones, acciones):
        with columna:
            st.markdown(
                f"""
                <div class="cop-action-card">
                    <span>{escape(accion["titulo"])}</span>
                    <strong>{accion["valor"]}</strong>
                    <p>{escape(accion["detalle"])}</p>
                    <em>{escape(accion["accion"])}</em>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.subheader("KPIs")
    columnas = st.columns(4)
    columnas[0].metric("Avance promedio", f'{resumen_dashboard["avance_oficial"]}%')
    columnas[1].metric("Liberables", resumen_dashboard["liberables"])
    columnas[2].metric("Bloqueados", resumen_dashboard["bloqueados"])
    columnas[3].metric("Pendientes de verificar", len(pendientes_verificar))

    st.subheader("Filtros")
    filtros = st.columns([1, 1, 1, 1])
    pisos_disponibles = sorted({departamento["piso"] for departamento in departamentos})
    estados_disponibles = [
        "Bloqueado",
        "Observado",
        "En proceso",
        "Liberable",
        "Sin revisar",
    ]
    responsables_disponibles = sorted(
        {
            departamento["responsable_principal"]
            for departamento in departamentos
            if departamento["responsable_principal"]
        }
    )
    piso_filtro = filtros[0].selectbox(
        "Piso",
        ["Todos", *[nombre_del_nivel(piso) for piso in pisos_disponibles]],
    )
    estado_filtro = filtros[1].selectbox("Estado", ["Todos", *estados_disponibles])
    responsable_filtro = filtros[2].selectbox(
        "Responsable",
        ["Todos", *responsables_disponibles],
    )

    recintos_filtro = filtros[3].text_input(
        "Recinto",
        placeholder="Ej.: Cocina",
    )
    partida_filtro = ""
    especialidad_filtro = "Todas"
    with st.expander("Filtros avanzados"):
        especialidad_filtro = st.selectbox(
            "Especialidad",
            ["Todas", *listar_especialidades()],
        )
        partida_filtro = st.text_input(
            "Partida",
            placeholder="Ej.: Puerta, Pintura, Cerámica",
        )

    departamentos_filtrados = departamentos
    if piso_filtro != "Todos":
        piso_por_nombre = {nombre_del_nivel(piso): piso for piso in pisos_disponibles}
        departamentos_filtrados = [
            departamento
            for departamento in departamentos_filtrados
            if departamento["piso"] == piso_por_nombre[piso_filtro]
        ]
    if estado_filtro != "Todos":
        departamentos_filtrados = [
            departamento
            for departamento in departamentos_filtrados
            if departamento["estado"] == estado_filtro
        ]
    if responsable_filtro != "Todos":
        departamentos_filtrados = [
            departamento
            for departamento in departamentos_filtrados
            if departamento["responsable_principal"] == responsable_filtro
        ]
    if recintos_filtro.strip() or partida_filtro.strip():
        departamentos_filtrados = filtrar_por_recinto_partida(
            departamentos_filtrados,
            recintos_filtro,
            partida_filtro,
        )
    if especialidad_filtro != "Todas":
        departamentos_con_especialidad = {
            str(registro["departamento"])
            for registro in obtener_pendientes_por_especialidad(especialidad_filtro)
        }
        departamentos_filtrados = [
            departamento
            for departamento in departamentos_filtrados
            if str(departamento["departamento"]) in departamentos_con_especialidad
        ]

    st.subheader("Tarjetas de departamentos")
    mostrar_tarjetas_departamentos_operativas(departamentos_filtrados[:24])

    izquierda, derecha = st.columns([1.45, 1])
    with izquierda:
        st.subheader("Matriz de departamentos")
        mostrar_matriz_dashboard(departamentos_filtrados)
        st.subheader("Resumen por piso")
        mostrar_tabla(
            obtener_resumen_pisos(),
            "No hay datos por piso.",
        )

    with derecha:
        st.subheader("Ficha de departamento")
        opciones_departamento = {
            (
                f'{departamento["torre"]} · {nombre_del_nivel(departamento["piso"])} '
                f'· Depto {departamento["departamento"]}'
            ): departamento["id"]
            for departamento in departamentos_filtrados
        }
        if not opciones_departamento:
            st.info("No hay departamentos con los filtros seleccionados.")
            return
        etiqueta_previa = next(iter(opciones_departamento))
        if "dashboard_departamento_id" in st.session_state:
            for etiqueta, identificador in opciones_departamento.items():
                if identificador == st.session_state["dashboard_departamento_id"]:
                    etiqueta_previa = etiqueta
                    break
        departamento_elegido = st.selectbox(
            "Departamento",
            opciones_departamento,
            index=list(opciones_departamento).index(etiqueta_previa),
        )
        departamento_id = opciones_departamento[departamento_elegido]
        st.session_state["dashboard_departamento_id"] = departamento_id
        mostrar_ficha_dashboard(departamento_id)

    st.subheader("Alertas operativas")
    alertas = st.columns(3)
    with alertas[0]:
        st.markdown("##### Bloqueos vencidos")
        mostrar_tabla(
            obtener_reporte_bloqueos_vencidos()[:8],
            "Sin bloqueos vencidos.",
        )
    with alertas[1]:
        st.markdown("##### Partidas sin movimiento")
        mostrar_tabla(
            obtener_partidas_sin_movimiento()[:8],
            "Sin partidas detenidas en el umbral operativo.",
        )
    with alertas[2]:
        st.markdown("##### Actividad reciente")
        mostrar_tabla(
            obtener_actividad_reciente(8),
            "Sin actividad reciente.",
        )

    st.subheader("Pendientes por especialidad")
    mostrar_tabla(
        obtener_resumen_pendientes_especialidad(),
        "Sin pendientes agrupados por especialidad.",
    )

    recomendaciones = obtener_recomendaciones_operativas()
    st.subheader("Recomendaciones operativas")
    if recomendaciones:
        for recomendacion in recomendaciones:
            st.info(recomendacion)
    else:
        st.success("Sin recomendaciones operativas pendientes segun las reglas actuales.")


def filtrar_por_recinto_partida(
    departamentos: list[dict],
    recinto: str,
    partida: str,
) -> list[dict]:
    recinto = recinto.strip().casefold()
    partida = partida.strip().casefold()
    filtrados = []
    for departamento in departamentos:
        try:
            avance = obtener_avance_departamento(departamento["id"])
        except ValueError:
            continue
        coincide_recinto = True
        coincide_partida = True
        if recinto:
            coincide_recinto = any(
                recinto in item["recinto"].casefold()
                for item in avance["partidas"]
            )
        if partida:
            coincide_partida = any(
                partida in item["partida"].casefold()
                for item in avance["partidas"]
            )
        if coincide_recinto and coincide_partida:
            filtrados.append(departamento)
    return filtrados


def proxima_accion_dashboard(departamento: dict) -> str:
    if departamento["estado"] == "Bloqueado":
        return "Resolver bloqueo"
    if departamento["estado"] == "Liberable":
        return "Liberar departamento"
    if departamento["avance_declarado"] > departamento["avance_oficial"]:
        return "Verificar avance"
    if departamento["avance_declarado"] >= 80:
        return "Revisar cierre"
    if departamento["estado"] == "Sin revisar":
        return "Iniciar revisión"
    return "Continuar avance"


def mostrar_tarjetas_departamentos_operativas(departamentos: list[dict]):
    if not departamentos:
        st.info("No hay departamentos para mostrar con esos filtros.")
        return

    colores = {
        "Bloqueado": "is-blocked",
        "Observado": "is-risk",
        "Liberable": "is-ready",
        "En proceso": "is-progress",
        "Sin revisar": "is-pending",
    }
    tarjetas = []
    for departamento in departamentos:
        estado = departamento["estado"]
        tarjetas.append(
            f"""
            <article class="cop-dept-card {colores.get(estado, "is-pending")}">
                <div class="cop-dept-card__top">
                    <strong>Depto {escape(str(departamento["departamento"]))}</strong>
                    <span>{escape(estado)}</span>
                </div>
                <div class="cop-dept-card__progress">
                    <b>{departamento["avance_oficial"]}%</b>
                    <small>avance oficial</small>
                </div>
                <div class="cop-dept-card__meta">
                    <span>{escape(nombre_del_nivel(departamento["piso"]))}</span>
                    <span>Declarado {departamento["avance_declarado"]}%</span>
                </div>
                <em>{escape(proxima_accion_dashboard(departamento))}</em>
            </article>
            """
        )

    st.markdown(
        '<div class="cop-dept-grid">' + "".join(tarjetas) + "</div>",
        unsafe_allow_html=True,
    )


def mostrar_matriz_dashboard(departamentos: list[dict]):
    colores = {
        "Bloqueado": ("#fee2e2", "#991b1b", "#ef4444"),
        "Observado": ("#fef3c7", "#92400e", "#f59e0b"),
        "Liberable": ("#dcfce7", "#166534", "#22c55e"),
        "En proceso": ("#dbeafe", "#1e40af", "#3b82f6"),
        "Sin revisar": ("#f1f5f9", "#475569", "#94a3b8"),
    }

    st.markdown(
        """
        <div class="leyenda-semaforo">
            <span><i class="punto rojo"></i> Bloqueado</span>
            <span><i class="punto amarillo"></i> Observado</span>
            <span><i class="punto verde"></i> Liberable</span>
            <span><i class="punto azul"></i> En proceso</span>
            <span><i class="punto gris"></i> Sin revisar</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not departamentos:
        st.info("No hay departamentos para mostrar con esos filtros.")
        return

    departamentos_por_torre = {}
    for departamento in departamentos:
        clave_torre = (departamento["obra"], departamento["torre"])
        departamentos_por_torre.setdefault(clave_torre, []).append(departamento)

    for (obra, torre), registros_torre in departamentos_por_torre.items():
        st.markdown(f"#### {escape(torre)}")
        st.caption(obra)

        niveles = {}
        for departamento in registros_torre:
            niveles.setdefault(departamento["piso"], []).append(departamento)

        filas_html = []
        for piso in sorted(niveles):
            nombre_nivel = nombre_del_nivel(piso)
            tarjetas = []
            for departamento in sorted(
                niveles[piso],
                key=lambda registro: clave_numero_departamento(
                    registro["departamento"]
                ),
            ):
                estado = departamento["estado"]
                fondo, texto, borde = colores.get(
                    estado,
                    ("#f3f4f6", "#374151", "#9ca3af"),
                )
                detalle = (
                    f'Oficial {departamento["avance_oficial"]}% · '
                    f'Declarado {departamento["avance_declarado"]}% · '
                    f'Bloqueos {departamento["bloqueos_activos"]} · '
                    f'Obs {departamento["observaciones_activas"]} · '
                    f'{departamento["responsable_principal"]}'
                )
                tarjetas.append(
                    '<div class="tarjeta-departamento" '
                    f'title="{escape(estado)} - {escape(detalle)}" '
                    f'style="background:{fondo};color:{texto};'
                    f'border-color:{borde};">'
                    f'<strong>{escape(str(departamento["departamento"]))}</strong>'
                    f'<small>{escape(str(departamento["avance_oficial"]))}% of.</small>'
                    f'<small>{escape(str(departamento["avance_declarado"]))}% dec.</small>'
                    '<small>'
                    f'B:{departamento["bloqueos_activos"]} '
                    f'O:{departamento["observaciones_activas"]}'
                    '</small>'
                    "</div>"
                )

            filas_html.append(
                '<div class="fila-nivel">'
                f'<div class="nombre-nivel">{escape(nombre_nivel)}</div>'
                f'<div class="departamentos-nivel">{"".join(tarjetas)}</div>'
                "</div>"
            )

        st.markdown(
            '<div class="matriz-torre">'
            + "".join(filas_html)
            + "</div>",
            unsafe_allow_html=True,
        )


def mostrar_ficha_dashboard(departamento_id: int):
    ficha = obtener_ficha_dashboard_departamento(departamento_id)
    columnas = st.columns(3)
    columnas[0].metric("Estado", ficha["estado"])
    columnas[1].metric("Oficial", f'{ficha["avance_oficial"]}%')
    columnas[2].metric("Declarado", f'{ficha["avance_declarado"]}%')
    st.progress(ficha["avance_oficial"] / 100)

    detalle = st.columns(3)
    detalle[0].metric("Bloqueos", len(ficha["bloqueos"]))
    detalle[1].metric("Observaciones", len(ficha["observaciones"]))
    detalle[2].metric("Vencidas", len(ficha["vencidas_detalle"]))
    st.write(f'**Responsable principal:** {ficha["responsable_principal"]}')
    if ficha["proxima_fecha"]:
        st.write(f'**Próxima fecha compromiso:** {ficha["proxima_fecha"]}')

    if st.button("Actualizar partidas", type="primary", width="stretch"):
        st.session_state["departamento_avance_id"] = departamento_id
        st.session_state["departamentos_vista"] = "ficha"
        st.session_state["pagina"] = "Departamentos"
        st.rerun()

    usuario_activo = st.session_state.get("usuario_activo")
    if usuario_activo and usuario_activo["rol"] == "Administrador":
        with st.expander("Liberar departamento"):
            comentario_liberacion = st.text_area(
                "Comentario de liberacion",
                key=f"comentario_liberacion_{departamento_id}",
            )
            if st.button(
                "Liberar departamento",
                key=f"liberar_{departamento_id}",
                width="stretch",
            ):
                try:
                    liberar_departamento(
                        departamento_id=departamento_id,
                        usuario_id=usuario_activo["id"],
                        comentario=comentario_liberacion,
                    )
                    st.success("Liberacion registrada.")
                    st.rerun()
                except (ValueError, sqlite3.IntegrityError) as error:
                    st.error(mensaje_amigable(error))
    elif usuario_activo and usuario_activo["rol"] == "Supervisor":
        st.caption("Solo un administrador puede liberar departamentos.")

    st.markdown("##### Restricciones activas")
    restricciones_resumen = [
        {
            "Tipo": "Vencida" if item["vencida"] else (
                "Bloqueo" if item["bloquea_entrega"] else "Observación"
            ),
            "Recinto": item["recinto"],
            "Partida": item["partida"],
            "Responsable": item["responsable"],
            "Compromiso": item["fecha_compromiso"],
            "Detalle": item["titulo"],
        }
        for item in ficha["restricciones"][:8]
    ]
    mostrar_tabla(restricciones_resumen, "Sin restricciones activas.")

    st.markdown("##### Partidas pendientes para liberar")
    pendientes = [
        {
            "Recinto": item["recinto"],
            "Partida": item["partida"],
            "Estado": item["estado"].replace("_", " ").title(),
            "Responsable": item["responsable"] or "",
            "Compromiso": item["fecha_compromiso"] or "",
        }
        for item in ficha["pendientes"][:12]
    ]
    mostrar_tabla(pendientes, "Sin pendientes críticos para liberar.")

    st.markdown("##### Historial reciente")
    historial = [
        {
            "Fecha": item["fecha"],
            "Usuario": item["usuario"],
            "Recinto": item["recinto"],
            "Partida": item["partida"],
            "Nuevo": item["estado_nuevo"].replace("_", " ").title(),
        }
        for item in ficha["historial"]
    ]
    mostrar_tabla(historial, "Sin historial reciente.")


def clave_recinto(nombre: str) -> str:
    return nombre.casefold().replace("ã±", "ñ")


def estado_partida_legible(estado: str) -> str:
    return ETIQUETA_POR_ESTADO_PARTIDA.get(estado, estado).replace("_", " ").title()


def recintos_ordenados(partidas: list[dict]) -> list[dict]:
    recintos = {}
    for partida in partidas:
        nombre = partida["recinto"]
        recintos.setdefault(nombre, []).append(partida)

    resultado = []
    for nombre, items in recintos.items():
        aplicables = [item for item in items if item["estado"] != "no_aplica"]
        verificadas = [item for item in aplicables if item["estado"] == "verificada"]
        total = len(aplicables)
        avance = round(len(verificadas) * 100 / total) if total else 0
        resultado.append(
            {
                "nombre": nombre,
                "partidas": sorted(items, key=lambda item: item["orden"]),
                "total": total,
                "verificadas": len(verificadas),
                "avance": avance,
            }
        )

    return sorted(
        resultado,
        key=lambda item: (
            ORDEN_RECINTO.get(clave_recinto(item["nombre"]), 999),
            item["nombre"],
        ),
    )


def resumen_recintos(recintos: list[dict]) -> tuple[int, int]:
    aplicables = [recinto for recinto in recintos if recinto["total"]]
    completados = [
        recinto
        for recinto in aplicables
        if recinto["verificadas"] == recinto["total"]
    ]
    return len(completados), len(aplicables)


def proxima_accion_departamento(ficha: dict) -> str:
    partidas = ficha["partidas"]
    bloqueada = next(
        (partida for partida in partidas if partida["estado"] == "bloqueada"),
        None,
    )
    if bloqueada:
        return f'Resolver bloqueo en {bloqueada["recinto"]}: {bloqueada["partida"]}'

    observada = next(
        (partida for partida in partidas if partida["estado"] == "observada"),
        None,
    )
    if observada:
        return f'Revisar observacion en {observada["recinto"]}: {observada["partida"]}'

    terminada = next(
        (partida for partida in partidas if partida["estado"] == "terminada"),
        None,
    )
    if terminada:
        return f'Verificar {terminada["recinto"]}: {terminada["partida"]}'

    pendiente = next(
        (
            partida
            for partida in partidas
            if partida["estado"] in {"no_iniciada", "en_proceso"}
        ),
        None,
    )
    if pendiente:
        return f'Actualizar {pendiente["recinto"]}: {pendiente["partida"]}'

    return "Sin acciones pendientes"


def impacto_departamento(ficha: dict) -> str:
    pendientes = sum(
        1
        for partida in ficha["partidas"]
        if partida["estado"] not in {"verificada", "no_aplica"}
    )
    if pendientes == 0 and ficha["bloqueos_activos"] == 0:
        return "Departamento listo para liberacion administrativa."
    if ficha["bloqueos_activos"]:
        return f'Desbloquear permite retomar {pendientes} partidas aplicables.'
    return f'Completar pendientes permite avanzar {pendientes} partidas aplicables.'


def color_estado_departamento(ficha: dict) -> str:
    if ficha["bloqueos_activos"]:
        return "#fee2e2"
    if ficha["estado_operativo"] == "liberable":
        return "#dcfce7"
    if ficha["observaciones_activas"]:
        return "#fef3c7"
    if ficha["avance_general"] > 0:
        return "#dbeafe"
    return "#f1f5f9"


def texto_estado_departamento(ficha: dict) -> str:
    if ficha["bloqueos_activos"]:
        return "Bloqueado"
    if ficha["estado_operativo"] == "liberable":
        return "Liberable"
    if ficha["observaciones_activas"]:
        return "Observado"
    if ficha["avance_general"] > 0:
        return "En proceso"
    return "Sin iniciar"


def normalizar_ficha_departamento(ficha: dict) -> dict:
    partidas = ficha.get("partidas", [])
    ficha["departamento_id"] = ficha.get("departamento_id", ficha.get("id"))
    ficha["avance_general"] = ficha.get(
        "avance_general",
        ficha.get("avance_porcentaje", 0),
    )
    ficha["ultima_actualizacion"] = ficha.get(
        "ultima_actualizacion",
        ficha.get("fecha_ultima_revision"),
    )
    ficha["bloqueos_activos"] = ficha.get(
        "bloqueos_activos",
        sum(1 for partida in partidas if partida["estado"] == "bloqueada"),
    )
    ficha["observaciones_activas"] = ficha.get(
        "observaciones_activas",
        sum(1 for partida in partidas if partida["estado"] == "observada"),
    )
    return ficha


def obtener_avances_departamentos_gestion() -> list[dict]:
    departamentos = listar_departamentos_seleccionables()
    resultado = []
    for departamento in departamentos:
        ficha = normalizar_ficha_departamento(
            obtener_avance_departamento(departamento["id"])
        )
        recintos = recintos_ordenados(ficha["partidas"])
        completados, total_recintos = resumen_recintos(recintos)
        ficha["recintos_ordenados"] = recintos
        ficha["recintos_completados"] = completados
        ficha["total_recintos"] = total_recintos
        ficha["proxima_accion"] = proxima_accion_departamento(ficha)
        ficha["impacto_esperado"] = impacto_departamento(ficha)
        resultado.append(ficha)
    return sorted(resultado, key=lambda item: (item["piso"], item["numero"]))


def render_chip(texto: str, color_fondo: str = "#e2e8f0", color_texto: str = "#0f172a"):
    st.markdown(
        (
            f'<span style="display:inline-block;padding:.2rem .5rem;'
            f'border-radius:999px;background:{color_fondo};color:{color_texto};'
            f'font-size:.8rem;font-weight:600;margin:.1rem .15rem .1rem 0;">'
            f'{escape(texto)}</span>'
        ),
        unsafe_allow_html=True,
    )


def mostrar_departamentos():
    vista = st.session_state.get("departamentos_vista", "lista")
    departamento_id = st.session_state.get("departamento_avance_id")
    recinto = st.session_state.get("departamento_recinto")

    if vista == "recinto" and departamento_id and recinto:
        mostrar_departamento_recinto(departamento_id, recinto)
    elif vista == "ficha" and departamento_id:
        mostrar_departamento_ficha(departamento_id)
    else:
        mostrar_departamentos_lista()


def mostrar_departamentos_lista():
    st.title("Departamentos")
    st.caption("Lista operativa para decidir que departamento revisar ahora.")

    departamentos = obtener_avances_departamentos_gestion()
    if not departamentos:
        st.info("No hay departamentos configurados.")
        return

    st.session_state["departamentos_vista"] = "lista"
    for ficha in departamentos:
        with st.container(border=True):
            encabezado, metricas, accion = st.columns([2.2, 1.6, 1])
            with encabezado:
                st.subheader(f'Departamento {ficha["numero"]}')
                st.write(f'Piso {ficha["piso"]} · {ficha["tipologia"] or "Sin tipologia"}')
                render_chip(
                    texto_estado_departamento(ficha),
                    color_estado_departamento(ficha),
                )
                if ficha["estado_operativo"] == "liberable":
                    render_chip("Liberable", "#dcfce7", "#166534")
                if ficha["bloqueos_activos"]:
                    render_chip("Bloqueado", "#fee2e2", "#991b1b")
                if any(
                    partida["estado"] == "terminada"
                    for partida in ficha["partidas"]
                ):
                    render_chip("Pendiente de Verificacion", "#fef3c7", "#92400e")
                if ficha["proxima_accion"] != "Sin acciones pendientes":
                    render_chip("Proxima Accion", "#dbeafe", "#1e40af")
            with metricas:
                st.metric("Avance General", f'{ficha["avance_general"]}%')
                st.write(
                    "Recintos completados / total: "
                    f'{ficha["recintos_completados"]}/{ficha["total_recintos"]}'
                )
            with accion:
                if st.button(
                    "Abrir ficha",
                    key=f'abrir_ficha_{ficha["departamento_id"]}',
                    type="primary",
                    width="stretch",
                ):
                    st.session_state["departamento_avance_id"] = ficha["departamento_id"]
                    st.session_state["departamentos_vista"] = "ficha"
                    st.rerun()


def mostrar_departamento_ficha(departamento_id: int):
    ficha = normalizar_ficha_departamento(
        obtener_avance_departamento(departamento_id)
    )
    recintos = recintos_ordenados(ficha["partidas"])
    completados, total_recintos = resumen_recintos(recintos)
    ficha["proxima_accion"] = proxima_accion_departamento(ficha)
    ficha["impacto_esperado"] = impacto_departamento(ficha)

    if st.button("Volver a lista"):
        st.session_state["departamentos_vista"] = "lista"
        st.session_state.pop("departamento_recinto", None)
        st.rerun()

    st.title(f'Departamento {ficha["numero"]}')
    render_chip(texto_estado_departamento(ficha), color_estado_departamento(ficha))
    st.markdown(f'**Proxima accion:** {ficha["proxima_accion"]}')
    st.markdown(f'**Impacto esperado:** {ficha["impacto_esperado"]}')

    columnas = st.columns(5)
    columnas[0].metric("Avance General", f'{ficha["avance_general"]}%')
    columnas[1].metric("Piso", ficha["piso"])
    columnas[2].metric("Tipologia", ficha["tipologia"] or "Sin tipologia")
    columnas[3].metric(
        "Ultima actualizacion",
        ficha["ultima_actualizacion"] or "Sin registro",
    )
    st.progress(ficha["avance_general"] / 100)
    st.caption(f"Recintos completados / total: {completados}/{total_recintos}")

    st.subheader("Recintos")
    for recinto in recintos:
        with st.container(border=True):
            datos, accion = st.columns([3, 1])
            with datos:
                st.markdown(f'**{recinto["nombre"]}**')
                st.write(
                    f'Avance {recinto["avance"]}% · '
                    f'{recinto["verificadas"]}/{recinto["total"]} partidas verificadas'
                )
                st.progress(recinto["avance"] / 100)
            with accion:
                if st.button(
                    "Abrir recinto",
                    key=f'abrir_recinto_{departamento_id}_{recinto["nombre"]}',
                    width="stretch",
                ):
                    st.session_state["departamento_recinto"] = recinto["nombre"]
                    st.session_state["departamentos_vista"] = "recinto"
                    st.rerun()


def guardar_estado_partida_automatico(
    partida: dict,
    clave_estado: str,
    clave_comentario: str,
    clave_causa: str,
    clave_responsable: str,
    clave_fecha: str,
):
    usuario = st.session_state.get("usuario_activo")
    if usuario is None:
        st.error("Debe existir un usuario activo para actualizar partidas.")
        return

    fecha_compromiso = st.session_state.get(clave_fecha)

    try:
        actualizar_estado_partida(
            estado_partida_id=partida["estado_partida_id"],
            estado_nuevo=st.session_state.get(clave_estado),
            usuario_id=usuario["id"],
            comentario=st.session_state.get(clave_comentario, ""),
            causa=st.session_state.get(clave_causa, ""),
            responsable_id=st.session_state.get(clave_responsable),
            fecha_compromiso=fecha_compromiso.isoformat()
            if fecha_compromiso
            else None,
        )
        st.toast("Partida actualizada.")
    except (ValueError, sqlite3.IntegrityError) as error:
        st.error(mensaje_amigable(error))


def mostrar_departamento_recinto(departamento_id: int, nombre_recinto: str):
    ficha = normalizar_ficha_departamento(
        obtener_avance_departamento(departamento_id)
    )
    recintos = recintos_ordenados(ficha["partidas"])
    recinto = next(
        (item for item in recintos if item["nombre"] == nombre_recinto),
        None,
    )
    if recinto is None:
        st.warning("El recinto seleccionado ya no esta disponible.")
        st.session_state["departamentos_vista"] = "ficha"
        st.session_state.pop("departamento_recinto", None)
        return

    if st.button("Volver a ficha"):
        st.session_state["departamentos_vista"] = "ficha"
        st.session_state.pop("departamento_recinto", None)
        st.rerun()

    st.title(nombre_recinto)
    st.caption(f'Departamento {ficha["numero"]} · Piso {ficha["piso"]}')
    columnas = st.columns(3)
    columnas[0].metric("Avance recinto", f'{recinto["avance"]}%')
    columnas[1].metric("Verificadas", recinto["verificadas"])
    columnas[2].metric("Aplicables", recinto["total"])
    st.progress(recinto["avance"] / 100)

    usuario = st.session_state.get("usuario_activo")
    solo_lectura = es_solo_lectura(usuario)
    responsables = listar_responsables()
    responsable_por_id = {responsable["id"]: responsable for responsable in responsables}

    for partida in recinto["partidas"]:
        dependencias = obtener_dependencias_criticas_partida(
            nombre_recinto,
            partida["partida"],
        )
        with st.container(border=True):
            encabezado, control = st.columns([2.4, 1.4])
            with encabezado:
                st.markdown(f'**{partida["partida"]}**')
                st.write(f'Especialidad: {partida.get("especialidad") or "Sin especialidad"}')
                if dependencias:
                    textos_dependencias = [
                        (
                            f'{dependencia["partida_dependencia"]} '
                            f'({dependencia["condicion"]})'
                        )
                        for dependencia in dependencias
                    ]
                    st.write("Depende de: " + ", ".join(textos_dependencias))
                else:
                    st.write("Depende de: Sin dependencia critica")
            with control:
                estado_actual = partida["estado"]
                if solo_lectura:
                    st.write(estado_partida_legible(estado_actual))
                    continue

                opciones = list(ETIQUETA_POR_ESTADO_PARTIDA)
                if usuario and usuario["rol"] == "Supervisor":
                    opciones = [
                        "no_iniciada",
                        "en_proceso",
                        "terminada",
                        "observada",
                        "bloqueada",
                    ]

                if estado_actual not in opciones:
                    st.write(estado_partida_legible(estado_actual))
                    st.caption("Estado no editable por el rol activo.")
                    continue

                clave_estado = f'estado_{partida["estado_partida_id"]}'
                clave_comentario = f'comentario_{partida["estado_partida_id"]}'
                clave_causa = f'causa_{partida["estado_partida_id"]}'
                clave_responsable = f'responsable_{partida["estado_partida_id"]}'
                clave_fecha = f'fecha_{partida["estado_partida_id"]}'

                st.session_state.setdefault(clave_estado, estado_actual)
                st.session_state.setdefault(clave_comentario, partida.get("comentario") or "")
                st.session_state.setdefault(clave_causa, partida.get("causa") or "")
                st.session_state.setdefault(
                    clave_responsable,
                    partida.get("responsable_id"),
                )
                fecha_actual = None
                if partida.get("fecha_compromiso"):
                    try:
                        fecha_actual = date.fromisoformat(partida["fecha_compromiso"])
                    except ValueError:
                        fecha_actual = None
                st.session_state.setdefault(clave_fecha, fecha_actual or date.today())

                st.selectbox(
                    "Estado",
                    opciones,
                    key=clave_estado,
                    format_func=estado_partida_legible,
                    on_change=guardar_estado_partida_automatico,
                    args=(
                        partida,
                        clave_estado,
                        clave_comentario,
                        clave_causa,
                        clave_responsable,
                        clave_fecha,
                    ),
                )

                if st.session_state[clave_estado] in {"observada", "bloqueada"}:
                    with st.expander("Datos requeridos"):
                        st.text_area(
                            "Comentario",
                            key=clave_comentario,
                            on_change=guardar_estado_partida_automatico,
                            args=(
                                partida,
                                clave_estado,
                                clave_comentario,
                                clave_causa,
                                clave_responsable,
                                clave_fecha,
                            ),
                        )
                        if st.session_state[clave_estado] == "bloqueada":
                            st.text_input(
                                "Causa",
                                key=clave_causa,
                                on_change=guardar_estado_partida_automatico,
                                args=(
                                    partida,
                                    clave_estado,
                                    clave_comentario,
                                    clave_causa,
                                    clave_responsable,
                                    clave_fecha,
                                ),
                            )
                            st.selectbox(
                                "Responsable",
                                [None, *responsable_por_id],
                                key=clave_responsable,
                                format_func=lambda valor: (
                                    "Sin responsable"
                                    if valor is None
                                    else responsable_por_id[valor]["nombre"]
                                ),
                                on_change=guardar_estado_partida_automatico,
                                args=(
                                    partida,
                                    clave_estado,
                                    clave_comentario,
                                    clave_causa,
                                    clave_responsable,
                                    clave_fecha,
                                ),
                            )
                            st.date_input(
                                "Fecha compromiso",
                                key=clave_fecha,
                                on_change=guardar_estado_partida_automatico,
                                args=(
                                    partida,
                                    clave_estado,
                                    clave_comentario,
                                    clave_causa,
                                    clave_responsable,
                                    clave_fecha,
                                ),
                            )


def opciones_estado_para_usuario(usuario: dict) -> dict[str, str]:
    opciones = dict(ETIQUETAS_ESTADO_PARTIDA)
    if usuario["rol"] != "Administrador":
        opciones.pop("Verificada", None)
        opciones.pop("No aplica", None)
    return opciones


def texto_dependencias_partida(recinto: str, partida: str) -> str:
    dependencias = obtener_dependencias_criticas_partida(recinto, partida)
    if not dependencias:
        return "Sin dependencia critica"
    return ", ".join(
        f'{dependencia["partida_dependencia"]} ({dependencia["condicion"]})'
        for dependencia in dependencias
    )


def alternar_partida_terreno(clave_seleccion: str, estado_partida_id: int):
    seleccionadas = set(st.session_state.get(clave_seleccion, []))
    if estado_partida_id in seleccionadas:
        seleccionadas.remove(estado_partida_id)
    else:
        seleccionadas.add(estado_partida_id)
    st.session_state[clave_seleccion] = sorted(seleccionadas)


def guardar_accion_terreno(
    *,
    clave_seleccion: str,
    nuevo_estado: str,
    usuario: dict,
):
    seleccionadas = st.session_state.get(clave_seleccion, [])
    try:
        resultado = actualizar_estados_partidas(
            estado_partida_ids=seleccionadas,
            nuevo_estado=nuevo_estado,
            usuario_id=usuario["id"],
            comentario="",
        )
        st.session_state[clave_seleccion] = []
        st.session_state["terreno_mensaje"] = "Cambios guardados"
        st.session_state["terreno_actualizadas"] = resultado["actualizadas"]
        st.rerun()
    except (ValueError, sqlite3.IntegrityError) as error:
        st.error(mensaje_amigable(error))


def mostrar_terreno():
    st.title("Avance en terreno")
    st.caption("Actualización rápida desde celular.")

    usuario = st.session_state.get("usuario_activo")
    if usuario is None:
        st.warning("Configura al menos un usuario antes de actualizar partidas.")
        return

    departamentos = listar_departamentos_seleccionables()
    if not departamentos:
        st.info("Todavía no hay departamentos configurados.")
        return

    pisos = sorted({departamento["piso"] for departamento in departamentos})
    piso_actual = st.selectbox(
        "Piso",
        pisos,
        format_func=nombre_del_nivel,
        key="terreno_piso",
    )
    departamentos_piso = [
        departamento
        for departamento in departamentos
        if departamento["piso"] == piso_actual
    ]
    departamentos_piso = sorted(
        departamentos_piso,
        key=lambda departamento: clave_numero_departamento(departamento["numero"]),
    )
    departamento_por_numero = {
        departamento["numero"]: departamento["id"]
        for departamento in departamentos_piso
    }
    numero_departamento = st.selectbox(
        "Departamento",
        list(departamento_por_numero),
        key=f"terreno_departamento_{piso_actual}",
    )
    departamento_id = departamento_por_numero[numero_departamento]

    try:
        ficha = normalizar_ficha_departamento(
            obtener_avance_departamento(departamento_id)
        )
    except ValueError as error:
        st.warning(str(error))
        return

    recintos = recintos_ordenados(ficha["partidas"])
    if not recintos:
        st.info("El departamento no tiene recintos configurados.")
        return

    recinto_por_nombre = {recinto["nombre"]: recinto for recinto in recintos}
    nombre_recinto = st.selectbox(
        "Recinto",
        list(recinto_por_nombre),
        key=f"terreno_recinto_{departamento_id}",
    )
    recinto = recinto_por_nombre[nombre_recinto]

    metricas = st.columns(2)
    metricas[0].metric("Depto", f'{ficha["avance_general"]}%')
    metricas[1].metric("Recinto", f'{recinto["avance"]}%')
    st.progress(recinto["avance"] / 100)

    clave_terminadas = f"terreno_mostrar_terminadas_{departamento_id}_{nombre_recinto}"
    mostrar_terminadas = st.toggle(
        "Mostrar terminadas",
        value=st.session_state.get(clave_terminadas, False),
        key=clave_terminadas,
    )
    estados_ocultos = {"terminada", "verificada", "no_aplica"}
    partidas_visibles = [
        partida
        for partida in recinto["partidas"]
        if mostrar_terminadas or partida["estado"] not in estados_ocultos
    ]

    mensaje = st.session_state.pop("terreno_mensaje", None)
    actualizadas = st.session_state.pop("terreno_actualizadas", None)
    if mensaje:
        detalle = f" ({actualizadas} partidas)" if actualizadas is not None else ""
        st.success(f"{mensaje}{detalle}.")

    if not partidas_visibles:
        st.success("No hay partidas pendientes en este recinto.")
        return

    clave_seleccion = f"terreno_seleccion_{departamento_id}_{nombre_recinto}"
    seleccion_validas = {
        partida["estado_partida_id"]
        for partida in partidas_visibles
    }
    st.session_state[clave_seleccion] = [
        identificador
        for identificador in st.session_state.get(clave_seleccion, [])
        if identificador in seleccion_validas
    ]

    if es_solo_lectura(usuario):
        st.info("El usuario activo es solo lectura; no puede modificar partidas.")
        for partida in partidas_visibles:
            with st.container(border=True):
                st.markdown(f'**{partida["partida"]}**')
                st.caption(estado_partida_legible(partida["estado"]))
                st.write(f'Especialidad: {partida.get("especialidad") or "Sin especialidad"}')
                st.write(
                    "Depende de: "
                    + texto_dependencias_partida(nombre_recinto, partida["partida"])
                )
        return

    seleccionadas = set(st.session_state.get(clave_seleccion, []))
    st.markdown("#### Partidas pendientes")
    st.caption("Toca una tarjeta para seleccionarla.")

    for partida in partidas_visibles:
        estado_partida_id = partida["estado_partida_id"]
        seleccionada = estado_partida_id in seleccionadas
        etiqueta_boton = "Seleccionada" if seleccionada else "Seleccionar"
        tipo_boton = "primary" if seleccionada else "secondary"

        with st.container(border=True):
            st.markdown(f'**{partida["partida"]}**')
            st.caption(estado_partida_legible(partida["estado"]))
            st.write(f'Especialidad: {partida.get("especialidad") or "Sin especialidad"}')
            st.write(
                "Depende de: "
                + texto_dependencias_partida(nombre_recinto, partida["partida"])
            )
            st.button(
                etiqueta_boton,
                key=f"terreno_toggle_{departamento_id}_{estado_partida_id}",
                type=tipo_boton,
                width="stretch",
                on_click=alternar_partida_terreno,
                args=(clave_seleccion, estado_partida_id),
            )

    seleccionadas = st.session_state.get(clave_seleccion, [])
    st.markdown(f"**Seleccionadas:** {len(seleccionadas)}")

    acciones = st.columns(2 if usuario["rol"] == "Administrador" else 1)
    with acciones[0]:
        if st.button(
            "Marcar como Terminada",
            type="primary",
            width="stretch",
            disabled=not seleccionadas,
        ):
            guardar_accion_terreno(
                clave_seleccion=clave_seleccion,
                nuevo_estado="terminada",
                usuario=usuario,
            )

    if usuario["rol"] == "Administrador":
        with acciones[1]:
            if st.button(
                "Verificar",
                type="primary",
                width="stretch",
                disabled=not seleccionadas,
            ):
                guardar_accion_terreno(
                    clave_seleccion=clave_seleccion,
                    nuevo_estado="verificada",
                    usuario=usuario,
                )


def mostrar_configuracion():
    st.title("Configuración inicial")
    st.caption("Carga los datos mínimos de la torre piloto.")

    pestanas = st.tabs(
        [
            "1. Obra y torre",
            "2. Departamentos",
            "3. Tipologías",
            "4. Usuarios",
            "5. Responsables",
            "6. Carga Montevista V1",
            "7. Dependencias críticas",
            "8. Importar avance",
        ]
    )

    with pestanas[0]:
        izquierda, derecha = st.columns(2)

        with izquierda:
            st.subheader("Nueva obra")
            with st.form("form_obra", clear_on_submit=True):
                nombre_obra = st.text_input("Nombre de la obra")
                guardar_obra = st.form_submit_button("Guardar obra")
            if guardar_obra:
                ejecutar_y_notificar(crear_obra, nombre_obra, mensaje="Obra creada.")

        with derecha:
            st.subheader("Nueva torre")
            obras = listar_obras()
            if not obras:
                st.warning("Primero debes crear una obra.")
            else:
                opciones_obras = {obra["nombre"]: obra["id"] for obra in obras}
                with st.form("form_torre", clear_on_submit=True):
                    obra_nombre = st.selectbox("Obra", opciones_obras)
                    nombre_torre = st.text_input("Nombre de torre o bloque")
                    guardar_torre = st.form_submit_button("Guardar torre")
                if guardar_torre:
                    ejecutar_y_notificar(
                        crear_torre,
                        opciones_obras[obra_nombre],
                        nombre_torre,
                        mensaje="Torre creada.",
                    )

    with pestanas[1]:
        st.subheader("Carga rápida de departamentos")
        st.write(
            "Ingresa un departamento por línea usando el formato "
            "`piso, número`. Ejemplo: `2, 201`."
        )
        obras = listar_obras()
        if not obras:
            st.warning("Primero debes crear una obra y una torre.")
        else:
            obra_por_nombre = {obra["nombre"]: obra["id"] for obra in obras}
            obra_seleccionada = st.selectbox(
                "Obra",
                obra_por_nombre,
                key="obra_departamentos",
            )
            torres = listar_torres(obra_por_nombre[obra_seleccionada])
            if not torres:
                st.warning("Esta obra todavía no tiene torres.")
            else:
                torre_por_nombre = {torre["nombre"]: torre["id"] for torre in torres}
                with st.form("form_departamentos", clear_on_submit=True):
                    torre_seleccionada = st.selectbox("Torre", torre_por_nombre)
                    texto_departamentos = st.text_area(
                        "Departamentos",
                        placeholder="2, 201\n2, 202\n3, 301",
                        height=180,
                    )
                    guardar_departamentos = st.form_submit_button(
                        "Guardar departamentos"
                    )
                if guardar_departamentos:
                    try:
                        departamentos = interpretar_departamentos(
                            texto_departamentos
                        )
                        cantidad = crear_departamentos(
                            torre_por_nombre[torre_seleccionada],
                            departamentos,
                        )
                        st.success(f"Se guardaron {cantidad} departamentos.")
                    except (ValueError, sqlite3.IntegrityError) as error:
                        st.error(mensaje_amigable(error))

    with pestanas[2]:
        st.subheader("Tipologías y recintos")
        st.caption(
            "Crea cada tipo de departamento y define los recintos que se "
            "revisarán durante el levantamiento."
        )

        izquierda, derecha = st.columns(2)
        with izquierda:
            with st.form("form_tipologia", clear_on_submit=True):
                nombre_tipologia = st.text_input(
                    "Nombre de la tipología",
                    placeholder="Ej.: 2D, 3D o 3D + estar",
                )
                texto_recintos = st.text_area(
                    "Recintos, uno por línea",
                    placeholder=(
                        "Living comedor\nDormitorio principal\n"
                        "Dormitorio 1\nBaño principal\nTerraza"
                    ),
                    height=210,
                )
                guardar_tipologia = st.form_submit_button(
                    "Guardar tipología",
                    type="primary",
                )
            if guardar_tipologia:
                recintos = texto_recintos.splitlines()
                ejecutar_y_notificar(
                    crear_tipologia,
                    nombre_tipologia,
                    recintos,
                    mensaje="Tipología creada.",
                )

        with derecha:
            tipologias = listar_tipologias()
            departamentos = listar_departamentos_seleccionables()
            if not tipologias:
                st.info("Crea una tipología para comenzar las asignaciones.")
            elif not departamentos:
                st.info("Todavía no hay departamentos para asignar.")
            else:
                tipologia_por_nombre = {
                    tipologia["nombre"]: tipologia["id"]
                    for tipologia in tipologias
                }
                departamento_por_etiqueta = {
                    (
                        f'{departamento["torre"]} · '
                        f'{nombre_del_nivel(departamento["piso"])} · Depto '
                        f'{departamento["numero"]}'
                    ): departamento["id"]
                    for departamento in departamentos
                }
                with st.form("form_asignar_tipologia"):
                    tipologia_elegida = st.selectbox(
                        "Tipología",
                        tipologia_por_nombre,
                    )
                    departamentos_elegidos = st.multiselect(
                        "Departamentos",
                        departamento_por_etiqueta,
                        placeholder="Selecciona todos los que correspondan",
                    )
                    asignar = st.form_submit_button(
                        "Asignar tipología",
                        type="primary",
                    )
                if asignar:
                    try:
                        cantidad = asignar_tipologia_departamentos(
                            [
                                departamento_por_etiqueta[etiqueta]
                                for etiqueta in departamentos_elegidos
                            ],
                            tipologia_por_nombre[tipologia_elegida],
                        )
                        st.success(
                            f"Tipología asignada a {cantidad} departamentos."
                        )
                        st.rerun()
                    except (ValueError, sqlite3.IntegrityError) as error:
                        st.error(mensaje_amigable(error))

        tipologias = listar_tipologias()
        if tipologias:
            tabla_tipologias = [
                {
                    "Tipología": tipologia["nombre"],
                    "Recintos": ", ".join(tipologia["recintos"]),
                    "Departamentos asignados": tipologia[
                        "departamentos_asignados"
                    ],
                }
                for tipologia in tipologias
            ]
            mostrar_tabla(tabla_tipologias, "")

            st.divider()
            st.subheader("Checklist por recinto")
            st.caption(
                "Define las partidas que deben revisarse en cada recinto. "
                "Guardar reemplaza el checklist anterior de ese recinto."
            )

            tipologia_por_nombre = {
                tipologia["nombre"]: tipologia["id"]
                for tipologia in tipologias
            }
            tipologia_checklist = st.selectbox(
                "Tipología del checklist",
                tipologia_por_nombre,
                key="tipologia_checklist",
            )
            tipologia_id = tipologia_por_nombre[tipologia_checklist]
            recintos = listar_recintos_tipologia(tipologia_id)

            if not recintos:
                st.warning("Esta tipología no tiene recintos configurados.")
            else:
                recinto_por_nombre = {
                    recinto["nombre"]: recinto["id"] for recinto in recintos
                }
                recinto_checklist = st.selectbox(
                    "Recinto",
                    recinto_por_nombre,
                    key="recinto_checklist",
                )
                recinto_id = recinto_por_nombre[recinto_checklist]
                partidas = listar_catalogo("partidas")
                partida_por_nombre = {
                    partida["nombre"]: partida["id"] for partida in partidas
                }
                checklist = obtener_checklist_tipologia(tipologia_id)
                partidas_actuales = {
                    partida["nombre"]
                    for recinto in checklist
                    if recinto["id"] == recinto_id
                    for partida in recinto["partidas"]
                }

                with st.form("form_checklist_recinto"):
                    partidas_elegidas = st.multiselect(
                        "Partidas esperadas",
                        partida_por_nombre,
                        default=[
                            nombre
                            for nombre in partida_por_nombre
                            if nombre in partidas_actuales
                        ],
                        placeholder="Selecciona las partidas del recinto",
                    )
                    guardar_checklist = st.form_submit_button(
                        "Guardar checklist",
                        type="primary",
                    )

                if guardar_checklist:
                    try:
                        cantidad = configurar_partidas_tipologia(
                            recinto_id,
                            [
                                partida_por_nombre[nombre]
                                for nombre in partidas_elegidas
                            ],
                        )
                        st.success(
                            f"Checklist guardado con {cantidad} partidas."
                        )
                        st.rerun()
                    except (ValueError, sqlite3.IntegrityError) as error:
                        st.error(mensaje_amigable(error))

                resumen_checklist = obtener_checklist_tipologia(tipologia_id)
                recinto_actual = next(
                    (
                        recinto
                        for recinto in resumen_checklist
                        if recinto["id"] == recinto_id
                    ),
                    None,
                )
                if recinto_actual and recinto_actual["partidas"]:
                    st.markdown("##### Peso")
                    st.caption(
                        "Toda partida del checklist es obligatoria si aplica. "
                        "Peso 2 para partidas principales, peso 1 para montaje o terminacion."
                    )
                    with st.form("form_pesos_obligatoriedad"):
                        cambios_configuracion = []
                        for partida in recinto_actual["partidas"]:
                            fila = st.columns([3, 1])
                            fila[0].write(partida["nombre"])
                            peso = fila[1].selectbox(
                                "Peso",
                                [1, 2],
                                index=[1, 2].index(partida["peso_avance"]),
                                key=f'peso_{partida["recinto_partida_id"]}',
                                label_visibility="collapsed",
                            )
                            cambios_configuracion.append(
                                (
                                    partida["recinto_partida_id"],
                                    peso,
                                )
                            )
                        guardar_configuracion_partidas = st.form_submit_button(
                            "Guardar pesos",
                            type="primary",
                        )
                    if guardar_configuracion_partidas:
                        try:
                            for recinto_partida_id, peso in cambios_configuracion:
                                actualizar_configuracion_partida_recinto(
                                    recinto_partida_id=recinto_partida_id,
                                    peso_avance=peso,
                                )
                            st.success("Pesos actualizados.")
                            st.rerun()
                        except (ValueError, sqlite3.IntegrityError) as error:
                            st.error(mensaje_amigable(error))

                tabla_checklist = [
                    {
                        "Recinto": recinto["nombre"],
                        "Partidas esperadas": ", ".join(
                            (
                                f'{partida["nombre"]} '
                                f'(P{partida["peso_avance"]}, Aplicable)'
                            )
                            for partida in recinto["partidas"]
                        )
                        or "Sin configurar",
                        "Cantidad": len(recinto["partidas"]),
                    }
                    for recinto in resumen_checklist
                ]
                mostrar_tabla(tabla_checklist, "")

    with pestanas[3]:
        st.subheader("Usuarios de la aplicación")
        st.caption(
            "El administrador verifica cierres; el supervisor registra y gestiona."
        )
        with st.form("form_usuario", clear_on_submit=True):
            nombre_usuario = st.text_input("Nombre completo")
            rol = st.selectbox(
                "Rol",
                ["Administrador", "Supervisor", "Solo lectura"],
            )
            guardar_usuario = st.form_submit_button("Guardar usuario")
        if guardar_usuario:
            ejecutar_y_notificar(
                crear_usuario,
                nombre_usuario,
                rol,
                mensaje="Usuario creado.",
            )
        mostrar_tabla(listar_usuarios(), "Todavía no hay usuarios.")

    with pestanas[4]:
        st.subheader("Responsables de problemas")
        with st.form("form_responsable", clear_on_submit=True):
            nombre_responsable = st.text_input("Nombre completo")
            empresa = st.text_input("Empresa")
            cargo = st.text_input("Cargo")
            guardar_responsable = st.form_submit_button("Guardar responsable")
        if guardar_responsable:
            ejecutar_y_notificar(
                crear_responsable,
                nombre_responsable,
                empresa,
                cargo,
                mensaje="Responsable creado.",
            )
        mostrar_tabla(listar_responsables(), "Todavía no hay responsables.")

    with pestanas[5]:
        st.subheader("Carga base Proyecto Montevista")
        st.caption(
            "Carga tipologías, recintos, checklists y asignaciones de la Torre B. "
            "Antes de modificar la base se crea un respaldo."
        )

        resumen = obtener_resumen_configuracion()
        columnas = st.columns(5)
        columnas[0].metric("Obras", resumen["obras"])
        columnas[1].metric("Torres", resumen["torres"])
        columnas[2].metric("Departamentos", resumen["departamentos"])
        columnas[3].metric("Usuarios", resumen["usuarios"])
        columnas[4].metric("Responsables", resumen["responsables"])

        st.warning(
            "La carga es idempotente: puede ejecutarse más de una vez sin "
            "duplicar tipologías o checklists. Si existen cambios manuales en "
            "la configuración, revísalos después de cargar."
        )

        if st.button(
            "Cargar configuración Montevista V1",
            type="primary",
            width="stretch",
        ):
            try:
                resultado = cargar_configuracion_v1(crear_respaldo=True)
                st.success("Configuración Montevista V1 cargada.")
                if resultado["respaldo"]:
                    st.info(f'Respaldo creado: {resultado["respaldo"]}')
                mostrar_tabla(
                    [
                        {
                            "Tipologías procesadas": resultado["tipologias"],
                            "Recintos procesados": resultado["recintos"],
                            "Partidas procesadas": resultado["partidas"],
                            "Checklist partidas": resultado["checklist_partidas"],
                            "Departamentos asignados": resultado[
                                "departamentos_asignados"
                            ],
                        }
                    ],
                    "",
                )
                if resultado["departamentos_no_encontrados"]:
                    st.error(
                        "Departamentos no encontrados: "
                        + ", ".join(resultado["departamentos_no_encontrados"])
                    )
                else:
                    st.success("Todos los departamentos definidos fueron encontrados.")
            except (ValueError, sqlite3.IntegrityError, OSError) as error:
                st.error(mensaje_amigable(error))

    with pestanas[6]:
        st.subheader("Dependencias críticas")
        st.caption(
            "Estas reglas solo generan advertencias operativas. No bloquean "
            "cambios de estado ni modifican avances automáticamente."
        )

        dependencias = listar_dependencias_criticas()
        recintos_dependencias = sorted(
            {dependencia["recinto"] for dependencia in dependencias}
        )
        recinto_filtro = st.selectbox(
            "Recinto",
            ["Todos", *recintos_dependencias],
            key="filtro_dependencias_recinto",
        )
        dependencias_visibles = [
            dependencia
            for dependencia in dependencias
            if recinto_filtro == "Todos"
            or dependencia["recinto"] == recinto_filtro
        ]
        tabla_dependencias = [
            {
                "ID": dependencia["id"],
                "Recinto": dependencia["recinto"],
                "Partida": dependencia["partida"],
                "Dependencia": dependencia["dependencia"],
                "Grupo": dependencia["grupo"],
                "Condicion": dependencia.get("tipo_condicion", "AND"),
                "Descripcion": dependencia["descripcion"],
                "Activa": "Si" if dependencia["activa"] else "No",
            }
            for dependencia in dependencias_visibles
        ]
        mostrar_tabla(tabla_dependencias, "No hay dependencias configuradas.")

        izquierda, derecha = st.columns(2)
        with izquierda:
            st.markdown("##### Agregar o reactivar")
            with st.form("form_dependencia_critica"):
                recinto = st.text_input(
                    "Recinto",
                    placeholder="Ej.: Living - Comedor o Dormitorio 1",
                )
                partida = st.text_input(
                    "Partida",
                    placeholder="Ej.: Guardapolvo",
                )
                dependencia = st.text_input(
                    "Dependencia",
                    placeholder="Ej.: Empaste",
                )
                descripcion = st.text_input(
                    "Descripcion",
                    placeholder="Ej.: Empaste terminado",
                )
                grupo = st.number_input(
                    "Grupo",
                    min_value=1,
                    value=1,
                    step=1,
                )
                tipo_condicion = st.selectbox(
                    "Condicion",
                    ["AND", "OR"],
                    help=(
                        "AND exige todas las dependencias del grupo; "
                        "OR exige al menos una alternativa."
                    ),
                )
                guardar_dependencia = st.form_submit_button(
                    "Guardar dependencia",
                    type="primary",
                )
            if guardar_dependencia:
                try:
                    crear_dependencia_critica(
                        recinto=recinto,
                        partida=partida,
                        dependencia=dependencia,
                        descripcion=descripcion,
                        grupo=int(grupo),
                        tipo_condicion=tipo_condicion,
                    )
                    st.success("Dependencia guardada.")
                    st.rerun()
                except (ValueError, sqlite3.IntegrityError) as error:
                    st.error(mensaje_amigable(error))

        with derecha:
            st.markdown("##### Desactivar")
            activas = [
                dependencia
                for dependencia in dependencias_visibles
                if dependencia["activa"]
            ]
            if not activas:
                st.info("No hay dependencias activas para desactivar.")
            else:
                opciones = {
                    (
                        f'#{dependencia["id"]} - {dependencia["recinto"]} - '
                        f'{dependencia["partida"]} depende de '
                        f'{dependencia["dependencia"]}'
                    ): dependencia["id"]
                    for dependencia in activas
                }
                dependencia_elegida = st.selectbox(
                    "Dependencia activa",
                    opciones,
                    key="dependencia_desactivar",
                )
                if st.button("Desactivar dependencia", width="stretch"):
                    try:
                        desactivar_dependencia_critica(
                            opciones[dependencia_elegida]
                        )
                        st.success("Dependencia desactivada.")
                        st.rerun()
                    except (ValueError, sqlite3.IntegrityError) as error:
                        st.error(mensaje_amigable(error))

    with pestanas[7]:
        st.subheader("Importacion inicial de avance")
        st.caption(
            "Descarga la plantilla, completa los estados existentes y vuelve a "
            "cargar el archivo. No se crean departamentos, recintos ni partidas."
        )

        plantilla = obtener_plantilla_importacion_avance()
        if plantilla:
            st.download_button(
                "Descargar plantilla Excel",
                data=crear_excel_descarga(plantilla),
                file_name="plantilla_avance_inicial.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                width="stretch",
            )
        else:
            st.info("No hay partidas configuradas para generar la plantilla.")

        usuario_importacion = st.session_state.get("usuario_activo")
        if usuario_importacion is None:
            st.warning("Configura un usuario activo antes de importar avance.")
            return
        if es_solo_lectura(usuario_importacion):
            st.info("El usuario activo es solo lectura; no puede importar avance.")
            return

        archivo_excel = st.file_uploader(
            "Importar Excel",
            type=["xlsx"],
            accept_multiple_files=False,
        )
        if archivo_excel is not None:
            try:
                datos_excel = pd.read_excel(archivo_excel, dtype=str).fillna("")
                registros_excel = datos_excel.to_dict(orient="records")
                if st.button("Validar e importar", type="primary", width="stretch"):
                    resultado = importar_avance_desde_filas(
                        registros_excel,
                        usuario_importacion["id"],
                    )
                    columnas = st.columns(3)
                    columnas[0].metric(
                        "Filas procesadas",
                        resultado["filas_procesadas"],
                    )
                    columnas[1].metric(
                        "Filas actualizadas",
                        resultado["filas_actualizadas"],
                    )
                    columnas[2].metric(
                        "Filas con error",
                        resultado["filas_con_error"],
                    )
                    if resultado["errores"]:
                        st.error(
                            "Se detectaron errores. Esas filas no fueron actualizadas."
                        )
                        mostrar_tabla(resultado["errores"], "")
                    else:
                        st.success("Importacion completada sin errores.")
            except Exception as error:
                st.error(mensaje_amigable(error))


def mostrar_problemas():
    st.title("Problemas")
    st.caption("Registra una causa comun y asociala a uno o varios departamentos.")

    usuarios = listar_usuarios()
    responsables = listar_responsables()
    departamentos = listar_departamentos_seleccionables()
    partidas = listar_catalogo("partidas")
    tipos = listar_catalogo("tipos_problema")
    recintos = listar_catalogo("recintos")

    faltantes = []
    if not usuarios:
        faltantes.append("usuarios")
    if not responsables:
        faltantes.append("responsables")
    if not departamentos:
        faltantes.append("departamentos")
    if faltantes:
        st.warning("Completa primero en Configuracion: " + ", ".join(faltantes) + ".")
        return

    usuario_activo = st.session_state.get("usuario_activo")
    if usuario_activo is None:
        st.warning("Configura al menos un usuario antes de registrar problemas.")
        return
    if es_solo_lectura(usuario_activo):
        st.info("El usuario activo es solo lectura; no puede registrar problemas.")
        return

    responsable_por_nombre = {
        responsable["nombre"]: responsable["id"] for responsable in responsables
    }
    partida_por_nombre = {partida["nombre"]: partida["id"] for partida in partidas}
    tipo_por_nombre = {tipo["nombre"]: tipo["id"] for tipo in tipos}
    recinto_por_nombre = {recinto["nombre"]: recinto["id"] for recinto in recintos}
    departamento_por_etiqueta = {
        (
            f'{departamento["torre"]} - Piso {departamento["piso"]} - '
            f'Depto {departamento["numero"]}'
        ): departamento["id"]
        for departamento in departamentos
    }

    with st.expander("Registrar nuevo problema", expanded=True):
        with st.form("form_problema", clear_on_submit=True):
            fila_1 = st.columns(2)
            fila_1[0].text_input(
                "Registrado por",
                value=f'{usuario_activo["nombre"]} - {usuario_activo["rol"]}',
                disabled=True,
            )
            responsable = fila_1[1].selectbox("Responsable", responsable_por_nombre)

            titulo = st.text_input(
                "Titulo del problema",
                placeholder="Ej.: Falta instalacion de perfiles de ventana",
            )

            fila_2 = st.columns(3)
            partida = fila_2[0].selectbox("Partida", partida_por_nombre)
            tipo = fila_2[1].selectbox("Tipo de problema", tipo_por_nombre)
            recinto = fila_2[2].selectbox("Recinto", recinto_por_nombre)

            departamentos_elegidos = st.multiselect(
                "Departamentos afectados",
                departamento_por_etiqueta,
                placeholder="Selecciona uno o varios departamentos",
            )

            fila_3 = st.columns(2)
            fecha_deteccion = fila_3[0].date_input(
                "Fecha de deteccion",
                value=date.today(),
                format="DD/MM/YYYY",
            )
            fecha_compromiso = fila_3[1].date_input(
                "Fecha compromiso",
                value=date.today() + timedelta(days=7),
                format="DD/MM/YYYY",
            )

            comentario = st.text_area(
                "Comentario corto",
                placeholder="Describe concretamente que falta o que debe corregirse.",
            )
            fila_4 = st.columns(2)
            requiere_retrabajo = fila_4[0].checkbox("Requiere retrabajo")
            afecta_funcionalidad = fila_4[1].checkbox("Afecta funcionalidad")

            bloquea = tipo in {
                "Falta material",
                "Observacion grave",
                "Retrabajo pendiente",
                "Instalacion incompleta",
                "No funciona",
            } or requiere_retrabajo or afecta_funcionalidad
            if bloquea:
                st.error("Resultado automatico: bloquea la entrega.")
            else:
                st.info("Resultado automatico: observacion no bloqueante.")

            guardar = st.form_submit_button("Registrar problema", type="primary")

        if guardar:
            try:
                problema_id = crear_problema(
                    titulo=titulo,
                    partida_id=partida_por_nombre[partida],
                    tipo_problema_id=tipo_por_nombre[tipo],
                    responsable_id=responsable_por_nombre[responsable],
                    creado_por_usuario_id=usuario_activo["id"],
                    departamento_ids=[
                        departamento_por_etiqueta[etiqueta]
                        for etiqueta in departamentos_elegidos
                    ],
                    recinto_id=recinto_por_nombre[recinto],
                    fecha_deteccion=fecha_deteccion,
                    fecha_compromiso=fecha_compromiso,
                    comentario_corto=comentario,
                    requiere_retrabajo=requiere_retrabajo,
                    afecta_funcionalidad=afecta_funcionalidad,
                )
                st.success(f"Problema #{problema_id} registrado correctamente.")
            except (ValueError, sqlite3.IntegrityError) as error:
                st.error(mensaje_amigable(error))

    st.subheader("Problemas registrados")
    problemas = listar_problemas()
    if problemas:
        tabla = pd.DataFrame(problemas)
        tabla["bloquea_entrega"] = tabla["bloquea_entrega"].map({1: "Si", 0: "No"})
        st.dataframe(tabla, width="stretch", hide_index=True)
    else:
        st.write("Todavia no hay problemas registrados.")

def mostrar_seguimiento():
    st.title("Seguimiento")
    st.caption(
        "Actualiza cada departamento por separado hasta su verificación final."
    )

    restricciones = listar_restricciones()
    if not restricciones:
        st.info("Todavía no hay restricciones para gestionar.")
        return

    estados_filtro = st.multiselect(
        "Mostrar estados",
        ["Abierto", "En gestión", "Resuelto", "Verificado"],
        default=["Abierto", "En gestión", "Resuelto"],
    )
    visibles = [
        restriccion
        for restriccion in restricciones
        if restriccion["estado"] in estados_filtro
    ]
    if not visibles:
        st.info("No hay casos con los estados seleccionados.")
        return

    etiqueta_por_id = {
        restriccion["id"]: (
            f'#{restriccion["id"]} · Depto {restriccion["departamento"]} · '
            f'{restriccion["titulo"]} · {restriccion["estado"]}'
        )
        for restriccion in visibles
    }
    restriccion_por_id = {
        restriccion["id"]: restriccion for restriccion in visibles
    }
    restriccion_id = st.selectbox(
        "Caso a gestionar",
        options=list(etiqueta_por_id),
        format_func=lambda identificador: etiqueta_por_id[identificador],
    )
    caso = restriccion_por_id[restriccion_id]

    columnas = st.columns(5)
    columnas[0].metric("Departamento", caso["departamento"])
    columnas[1].metric("Estado", caso["estado"])
    columnas[2].metric("Responsable", caso["responsable"])
    columnas[3].metric(
        "Bloquea entrega",
        "Sí" if caso["bloquea_entrega"] else "No",
    )

    st.write(
        f'**Ubicación:** {caso["torre"]}, Piso {caso["piso"]}, '
        f'{caso["recinto"]}'
    )
    st.write(f'**Partida / tipo:** {caso["partida"]} · {caso["tipo"]}')

    siguiente_estado = {
        "Abierto": "En gestión",
        "En gestión": "Resuelto",
        "Resuelto": "Verificado",
    }.get(caso["estado"])

    if siguiente_estado is None:
        st.success("Este caso ya está verificado.")
    else:
        usuario_activo = st.session_state.get("usuario_activo")
        if usuario_activo is None:
            st.warning("Configura al menos un usuario antes de gestionar casos.")
            return
        if es_solo_lectura(usuario_activo):
            st.info("El usuario activo es solo lectura; no puede gestionar casos.")
            return
        usuarios = [usuario_activo]
        usuario_por_etiqueta = {
            f'{usuario["nombre"]} · {usuario["rol"]}': usuario
            for usuario in usuarios
        }
        with st.form(f"form_seguimiento_{restriccion_id}"):
            st.text_input(
                "Actualizado por",
                value=f'{usuario_activo["nombre"]} · {usuario_activo["rol"]}',
                disabled=True,
            )
            st.text_input(
                "Siguiente estado",
                value=siguiente_estado,
                disabled=True,
            )
            fecha_compromiso = st.date_input(
                "Fecha compromiso",
                value=date.fromisoformat(caso["fecha_compromiso"]),
                format="DD/MM/YYYY",
            )
            comentario_caso = st.text_area(
                "Descripción actual del caso",
                value=caso["comentario_corto"],
            )
            nota = st.text_area(
                "Nota de seguimiento (opcional)",
                placeholder="Ej.: Material recibido; instalación programada.",
            )
            avanzar = st.form_submit_button(
                f"Pasar a {siguiente_estado}",
                type="primary",
            )

        if avanzar:
            try:
                actualizar_restriccion(
                    restriccion_id=restriccion_id,
                    usuario_id=usuario_activo["id"],
                    nuevo_estado=siguiente_estado,
                    fecha_compromiso=fecha_compromiso,
                    comentario_corto=comentario_caso,
                    nota_seguimiento=nota,
                )
                st.success(f"El caso pasó a {siguiente_estado}.")
                st.rerun()
            except (ValueError, sqlite3.IntegrityError) as error:
                st.error(mensaje_amigable(error))

    historial = obtener_historial_restriccion(restriccion_id)
    st.subheader("Historial")
    mostrar_tabla(historial, "Todavía no hay movimientos registrados.")


def mostrar_levantamiento():
    st.title("Avance por departamento")
    st.caption(
        "Actualiza partidas por recinto con trazabilidad de cada cambio."
    )

    departamentos = listar_departamentos_seleccionables()
    if not departamentos:
        st.info("Todavía no hay departamentos configurados.")
        return

    departamento_por_etiqueta = {
        (
            f'{departamento["torre"]} · '
            f'{nombre_del_nivel(departamento["piso"])} · '
            f'Depto {departamento["numero"]}'
        ): departamento["id"]
        for departamento in departamentos
    }
    departamento_elegido = st.selectbox(
        "Departamento",
        departamento_por_etiqueta,
        index=indice_departamento_preseleccionado(
            departamento_por_etiqueta,
            st.session_state.get("departamento_avance_id"),
        ),
    )
    departamento_id = departamento_por_etiqueta[departamento_elegido]
    st.session_state["departamento_avance_id"] = departamento_id

    try:
        avance = obtener_avance_departamento(departamento_id)
    except ValueError as error:
        st.warning(str(error))
        return

    columnas = st.columns(5)
    columnas[0].metric("Tipología", avance["tipologia"])
    columnas[1].metric("Etapa", avance["etapa_actual"].replace("_", " ").title())
    columnas[2].metric(
        "Estado",
        avance["estado_operativo"].replace("_", " ").title(),
    )
    columnas[3].metric(
        "Avance oficial",
        f'{avance["avance_oficial_porcentaje"]}%',
    )
    columnas[4].metric(
        "Avance declarado",
        f'{avance["avance_declarado_porcentaje"]}%',
    )
    st.progress(avance["avance_oficial_porcentaje"] / 100)

    etiquetas_estado = {
        "No iniciada": "no_iniciada",
        "En proceso": "en_proceso",
        "Terminada": "terminada",
        "Observada": "observada",
        "Bloqueada": "bloqueada",
        "Verificada": "verificada",
        "No aplica": "no_aplica",
    }
    etiquetas_por_estado = {valor: etiqueta for etiqueta, valor in etiquetas_estado.items()}

    recintos = list(dict.fromkeys(partida["recinto"] for partida in avance["partidas"]))
    recinto_elegido = st.selectbox(
        "Recinto",
        recintos,
        key=f"recinto_avance_{departamento_id}",
    )
    partidas_recinto_todas = [
        partida for partida in avance["partidas"] if partida["recinto"] == recinto_elegido
    ]
    clave_terminadas = f"mostrar_terminadas_{departamento_id}_{recinto_elegido}"
    if st.button("Mostrar partidas terminadas", key=f"boton_{clave_terminadas}"):
        st.session_state[clave_terminadas] = not st.session_state.get(
            clave_terminadas,
            False,
        )
    mostrar_terminadas = st.session_state.get(clave_terminadas, False)
    partidas_recinto = [
        partida
        for partida in partidas_recinto_todas
        if mostrar_terminadas
        or partida["estado"] not in {"terminada", "verificada", "no_aplica"}
    ]

    tabla = pd.DataFrame(
        [
            {
                "Partida": partida["partida"],
                "Estado": etiquetas_por_estado.get(
                    partida["estado"],
                    partida["estado"].replace("_", " ").title(),
                ),
                "Responsable": partida["responsable"] or "",
                "Fecha compromiso": partida["fecha_compromiso"] or "",
            }
            for partida in partidas_recinto
        ]
    )
    st.dataframe(tabla, width="stretch", hide_index=True)

    advertencias_dependencias = obtener_advertencias_dependencias_departamento(
        departamento_id,
        [partida["estado_partida_id"] for partida in partidas_recinto],
    )
    if advertencias_dependencias:
        with st.expander("Advertencias de dependencias criticas", expanded=True):
            for advertencia in advertencias_dependencias:
                st.warning(
                    f'{advertencia["partida"]}: requiere '
                    f'{advertencia["dependencia"]} '
                    f'({advertencia["estado_dependencia"]}). '
                    f'{advertencia["detalle"]}'
                )

    responsables = listar_responsables()
    usuario_registro = st.session_state.get("usuario_activo")
    if usuario_registro is None:
        st.warning("Configura al menos un usuario antes de actualizar partidas.")
        return
    if es_solo_lectura(usuario_registro):
        st.info("El usuario activo es solo lectura; no puede modificar partidas.")
        return
    usuarios = [usuario_registro]
    usuario_por_etiqueta = {
        f'{usuario["nombre"]} · {usuario["rol"]}': usuario
        for usuario in usuarios
    }
    responsable_por_nombre = {
        responsable["nombre"]: responsable["id"]
        for responsable in responsables
    }

    st.subheader("Actualización masiva")
    with st.form("form_actualizar_partidas"):
        st.text_input(
            "Actualizado por",
            value=f'{usuario_registro["nombre"]} · {usuario_registro["rol"]}',
            disabled=True,
        )
        opciones_estado = dict(etiquetas_estado)
        if usuario_registro["rol"] != "Administrador":
            opciones_estado.pop("Verificada", None)
            opciones_estado.pop("No aplica", None)

        nuevo_estado_etiqueta = st.selectbox(
            "Nuevo estado",
            opciones_estado,
        )
        nuevo_estado = opciones_estado[nuevo_estado_etiqueta]

        opciones_partidas = {
            (
                f'{partida["partida"]} · '
                f'{etiquetas_por_estado.get(partida["estado"], partida["estado"])}'
            ): partida["estado_partida_id"]
            for partida in partidas_recinto
        }
        partidas_elegidas = st.multiselect(
            "Partidas a actualizar",
            opciones_partidas,
            placeholder="Selecciona una o varias partidas del recinto",
        )

        st.caption(
            "Si seleccionas Bloqueada, completa causa, responsable y fecha."
        )
        causa = st.text_input(
            "Causa del bloqueo",
            placeholder="Ej.: Falta material, interferencia o trabajo pendiente",
        )
        responsable = st.selectbox(
            "Responsable del bloqueo",
            ["Sin seleccionar", *responsable_por_nombre],
        )
        fecha_compromiso = st.date_input(
            "Fecha compromiso",
            value=date.today() + timedelta(days=7),
            format="DD/MM/YYYY",
        )
        comentario = st.text_area(
            "Comentario de la actualización",
            placeholder="Quedará registrado en el historial de cada partida seleccionada.",
        )
        guardar = st.form_submit_button(
            "Aplicar estado",
            type="primary",
        )

    if guardar:
        try:
            resultado = actualizar_estados_partidas(
                estado_partida_ids=[
                    opciones_partidas[etiqueta] for etiqueta in partidas_elegidas
                ],
                nuevo_estado=nuevo_estado,
                usuario_id=usuario_registro["id"],
                causa=causa,
                responsable_id=responsable_por_nombre.get(responsable),
                fecha_compromiso=fecha_compromiso,
                comentario=comentario,
            )
            st.success(
                f'Se actualizaron {resultado["actualizadas"]} partidas. '
                "Estado del departamento: "
                + resultado["estado_operativo"].replace("_", " ").title()
            )
            st.rerun()
        except (ValueError, sqlite3.IntegrityError) as error:
            st.error(mensaje_amigable(error))

    historial = obtener_historial_partidas_departamento(departamento_id)
    st.subheader("Historial reciente")
    if historial:
        tabla_historial = pd.DataFrame(
            [
                {
                    "Fecha": movimiento["fecha"],
                    "Usuario": movimiento["usuario"],
                    "Recinto": movimiento["recinto"],
                    "Partida": movimiento["partida"],
                    "Anterior": etiquetas_por_estado.get(
                        movimiento["estado_anterior"],
                        movimiento["estado_anterior"] or "",
                    ),
                    "Nuevo": etiquetas_por_estado.get(
                        movimiento["estado_nuevo"],
                        movimiento["estado_nuevo"],
                    ),
                    "Comentario": movimiento["comentario"] or "",
                }
                for movimiento in historial
            ]
        )
        st.dataframe(tabla_historial, width="stretch", hide_index=True)
    else:
        st.write("Todavía no hay cambios registrados para este departamento.")


def mostrar_reportes():
    st.title("Reportes")
    st.caption("Tablas operativas descargables para reunion y seguimiento.")

    reportes = {
        "Pendientes por departamento": (
            obtener_reporte_pendientes_departamento,
            "pendientes_por_departamento.csv",
        ),
        "Pendientes por responsable": (
            obtener_reporte_pendientes_responsable,
            "pendientes_por_responsable.csv",
        ),
        "Bloqueos vencidos": (
            obtener_reporte_bloqueos_vencidos,
            "bloqueos_vencidos.csv",
        ),
        "Avance por piso": (
            obtener_reporte_avance_piso,
            "avance_por_piso.csv",
        ),
        "Avance por tipologia": (
            obtener_reporte_avance_tipologia,
            "avance_por_tipologia.csv",
        ),
        "Departamentos liberables": (
            obtener_reporte_departamentos_liberables,
            "departamentos_liberables.csv",
        ),
        "Historial": (
            obtener_reporte_historial,
            "historial.csv",
        ),
    }

    nombre_reporte = st.selectbox("Reporte", list(reportes))
    funcion_reporte, archivo = reportes[nombre_reporte]
    registros = filtrar_reporte(funcion_reporte())

    mostrar_tabla(registros, "No hay registros para este reporte.")
    descargar_csv(registros, archivo)


def filtrar_reporte(registros: list[dict]) -> list[dict]:
    if not registros:
        return registros

    columnas = st.columns(4)
    estados = sorted(
        {
            str(registro.get("estado", ""))
            for registro in registros
            if registro.get("estado")
        }
    )
    responsables = sorted(
        {
            str(registro.get("responsable", ""))
            for registro in registros
            if registro.get("responsable")
        }
    )
    pisos = sorted(
        {
            str(registro.get("piso", ""))
            for registro in registros
            if registro.get("piso") != ""
        }
    )
    especialidades = sorted(
        {
            str(registro.get("especialidad", ""))
            for registro in registros
            if registro.get("especialidad")
        }
    )
    texto = columnas[0].text_input("Buscar")
    estado = columnas[1].selectbox("Estado", ["Todos", *estados])
    responsable = columnas[2].selectbox("Responsable", ["Todos", *responsables])
    piso = columnas[3].selectbox("Piso", ["Todos", *pisos])
    especialidad = columnas[4].selectbox(
        "Especialidad",
        ["Todas", *especialidades],
    )

    filtrados = registros
    if texto.strip():
        busqueda = texto.strip().casefold()
        filtrados = [
            registro
            for registro in filtrados
            if busqueda in " ".join(str(valor) for valor in registro.values()).casefold()
        ]
    if estado != "Todos":
        filtrados = [
            registro
            for registro in filtrados
            if str(registro.get("estado", "")) == estado
        ]
    if responsable != "Todos":
        filtrados = [
            registro
            for registro in filtrados
            if str(registro.get("responsable", "")) == responsable
        ]
    if piso != "Todos":
        filtrados = [
            registro
            for registro in filtrados
            if str(registro.get("piso", "")) == piso
        ]
    if especialidad != "Todas":
        filtrados = [
            registro
            for registro in filtrados
            if str(registro.get("especialidad", "")) == especialidad
        ]

    return filtrados


def interpretar_departamentos(texto: str) -> list[tuple[int, str]]:
    resultado = []
    for numero_linea, linea in enumerate(texto.splitlines(), start=1):
        linea = linea.strip()
        if not linea:
            continue
        partes = [parte.strip() for parte in linea.split(",")]
        if len(partes) != 2:
            raise ValueError(
                f"La línea {numero_linea} debe tener el formato: piso, número."
            )
        try:
            piso = int(partes[0])
        except ValueError as error:
            raise ValueError(
                f"El piso de la línea {numero_linea} debe ser un número entero."
            ) from error
        resultado.append((piso, partes[1]))
    return resultado


def ejecutar_y_notificar(funcion, *argumentos, mensaje: str):
    try:
        funcion(*argumentos)
        st.success(mensaje)
    except (ValueError, sqlite3.IntegrityError) as error:
        st.error(mensaje_amigable(error))


def mensaje_amigable(error: Exception) -> str:
    texto = str(error)
    if "UNIQUE constraint failed" in texto:
        return "Ese registro ya existe."
    if "FOREIGN KEY constraint failed" in texto:
        return "Falta un dato relacionado o dejó de estar disponible."
    return texto


def mostrar_tabla(registros: list[dict], mensaje_vacio: str):
    if registros:
        st.dataframe(
            pd.DataFrame(registros),
            width="stretch",
            hide_index=True,
        )
    else:
        st.write(mensaje_vacio)


def indice_departamento_preseleccionado(
    opciones: dict[str, int],
    departamento_id: int | None,
) -> int:
    if departamento_id is None:
        return 0
    for indice, identificador in enumerate(opciones.values()):
        if identificador == departamento_id:
            return indice
    return 0


paginas = [
    "Inicio",
    "Terreno",
    "Departamentos",
    "Problemas",
    "Seguimiento",
    "Reportes",
    "Configuración",
]
pagina_actual = st.session_state.get("pagina", "Inicio")
mostrar_marca_sidebar()
pagina = st.sidebar.radio(
    "Navegación",
    paginas,
    index=paginas.index(pagina_actual) if pagina_actual in paginas else 0,
    key="pagina",
)
st.session_state["usuario_activo"] = obtener_usuario_activo()

if pagina == "Inicio":
    mostrar_inicio()
elif pagina == "Terreno":
    mostrar_terreno()
elif pagina == "Departamentos":
    mostrar_departamentos()
elif pagina == "Problemas":
    mostrar_problemas()
elif pagina == "Seguimiento":
    mostrar_seguimiento()
elif pagina == "Reportes":
    mostrar_reportes()
else:
    mostrar_configuracion()


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    :root {
        --cop-bg: #F5F7FA;
        --cop-bg-soft: #EEF2F7;
        --cop-card: #FFFFFF;
        --cop-border: #E5E7EB;
        --cop-text: #1F2937;
        --cop-muted: #6B7280;
        --cop-primary: #2563EB;
        --cop-green: #16A34A;
        --cop-yellow: #F59E0B;
        --cop-red: #DC2626;
        --cop-gray: #9CA3AF;
        --cop-sidebar: #111827;
        --cop-radius: 12px;
        --cop-radius-lg: 16px;
        --cop-shadow: 0 8px 24px rgba(15, 23, 42, .06);
    }

    html, body, [class*="css"] {
        font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        background: var(--cop-bg);
        color: var(--cop-text);
    }

    .main .block-container {
        max-width: 1280px;
        padding-top: 48px;
        padding-bottom: 48px;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--cop-text);
        letter-spacing: 0;
    }

    h1 {
        font-size: 2.15rem;
        font-weight: 700;
        margin-bottom: 8px;
    }

    h2, h3 {
        font-weight: 700;
    }

    p, label, .stCaption, [data-testid="stCaptionContainer"] {
        color: var(--cop-muted);
    }

    section[data-testid="stSidebar"] {
        background: var(--cop-sidebar);
        border-right: 1px solid rgba(255, 255, 255, .08);
    }

    section[data-testid="stSidebar"] * {
        color: #F9FAFB;
    }

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] .stCaption {
        color: #D1D5DB;
    }

    .cop-sidebar-brand {
        padding: 8px 0 24px;
        margin-bottom: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, .10);
    }

    .cop-sidebar-logo {
        color: #FFFFFF;
        font-size: 1.18rem;
        font-weight: 700;
        line-height: 1.2;
    }

    .cop-sidebar-subtitle {
        color: #9CA3AF;
        font-size: .76rem;
        font-weight: 500;
        margin-top: 4px;
    }

    section[data-testid="stSidebar"] [role="radiogroup"] label {
        border-radius: var(--cop-radius);
        padding: 8px 10px;
        transition: background-color 160ms ease, color 160ms ease;
    }

    section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(255, 255, 255, .08);
    }

    [data-testid="stMetric"],
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--cop-card);
        border: 1px solid var(--cop-border);
        border-radius: var(--cop-radius-lg);
        box-shadow: var(--cop-shadow);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 16px;
    }

    [data-testid="stMetric"] {
        padding: 16px;
    }

    [data-testid="stMetricLabel"] {
        color: var(--cop-muted);
        font-weight: 500;
    }

    [data-testid="stMetricValue"] {
        color: var(--cop-text);
        font-weight: 700;
    }

    .stButton > button,
    .stDownloadButton > button,
    button[kind="primary"] {
        min-height: 42px;
        border-radius: var(--cop-radius);
        border: 1px solid var(--cop-border);
        font-weight: 600;
        transition: background-color 160ms ease, border-color 160ms ease, transform 160ms ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: var(--cop-primary);
        transform: translateY(-1px);
    }

    .stButton > button[kind="primary"],
    .stFormSubmitButton > button[kind="primary"],
    button[kind="primary"] {
        background: var(--cop-primary);
        border-color: var(--cop-primary);
        color: #FFFFFF;
    }

    input,
    textarea,
    div[data-baseweb="select"] > div,
    div[data-baseweb="base-input"] {
        border-radius: var(--cop-radius) !important;
    }

    input:focus,
    textarea:focus,
    div[data-baseweb="select"] div:focus-within {
        border-color: var(--cop-primary) !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, .14) !important;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--cop-border);
        border-radius: var(--cop-radius-lg);
        overflow: hidden;
        box-shadow: var(--cop-shadow);
    }

    .stAlert {
        border-radius: var(--cop-radius);
        border: 1px solid var(--cop-border);
    }

    .stProgress > div > div > div {
        background: var(--cop-primary);
    }

    .cop-hero {
        display: grid;
        grid-template-columns: minmax(0, 1.2fr) minmax(17rem, .8fr);
        gap: 24px;
        align-items: stretch;
        background: var(--cop-card);
        border: 1px solid var(--cop-border);
        border-radius: var(--cop-radius-lg);
        box-shadow: var(--cop-shadow);
        padding: 24px;
        margin-bottom: 24px;
    }
    .cop-kicker {
        color: var(--cop-primary);
        font-size: .78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .08em;
    }
    .cop-hero h1 {
        margin: 4px 0 8px;
    }
    .cop-hero p {
        margin: 0;
        max-width: 42rem;
    }
    .cop-context-grid {
        display: grid;
        gap: 10px;
    }
    .cop-context-grid div,
    .cop-action-card,
    .cop-dept-card {
        background: #FFFFFF;
        border: 1px solid var(--cop-border);
        border-radius: var(--cop-radius);
    }
    .cop-context-grid div {
        padding: 12px 14px;
    }
    .cop-context-grid span,
    .cop-action-card span,
    .cop-dept-card small,
    .cop-dept-card__meta {
        color: var(--cop-muted);
        font-size: .82rem;
        font-weight: 500;
    }
    .cop-context-grid strong {
        display: block;
        color: var(--cop-text);
        margin-top: 2px;
    }
    .cop-action-card {
        min-height: 11.5rem;
        padding: 18px;
        box-shadow: var(--cop-shadow);
    }
    .cop-action-card strong {
        display: block;
        color: var(--cop-text);
        font-size: 2rem;
        line-height: 1;
        margin: 12px 0;
    }
    .cop-action-card p {
        min-height: 2.6rem;
        margin: 0 0 12px;
    }
    .cop-action-card em,
    .cop-dept-card em {
        color: var(--cop-primary);
        font-style: normal;
        font-weight: 700;
    }
    .cop-dept-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(14rem, 1fr));
        gap: 14px;
        margin: 8px 0 24px;
    }
    .cop-dept-card {
        border-left: 5px solid var(--cop-gray);
        padding: 16px;
        box-shadow: var(--cop-shadow);
    }
    .cop-dept-card__top,
    .cop-dept-card__meta {
        display: flex;
        justify-content: space-between;
        gap: 10px;
        align-items: center;
    }
    .cop-dept-card__top span {
        border-radius: 999px;
        padding: 4px 9px;
        background: var(--cop-bg-soft);
        color: var(--cop-text);
        font-size: .76rem;
        font-weight: 700;
        white-space: nowrap;
    }
    .cop-dept-card__progress {
        margin: 16px 0 12px;
    }
    .cop-dept-card__progress b {
        color: var(--cop-text);
        font-size: 1.8rem;
        line-height: 1;
    }
    .cop-dept-card__progress small {
        display: block;
        margin-top: 4px;
    }
    .cop-dept-card.is-ready { border-left-color: var(--cop-green); }
    .cop-dept-card.is-blocked { border-left-color: var(--cop-red); }
    .cop-dept-card.is-risk { border-left-color: var(--cop-yellow); }
    .cop-dept-card.is-progress { border-left-color: var(--cop-primary); }

    .leyenda-semaforo {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin: 8px 0 16px;
        color: var(--cop-muted);
        font-size: .9rem;
    }
    .leyenda-semaforo span {
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .punto {
        width: 12px;
        height: 12px;
        border-radius: 999px;
        display: inline-block;
    }
    .punto.rojo { background: var(--cop-red); }
    .punto.amarillo { background: var(--cop-yellow); }
    .punto.verde { background: var(--cop-green); }
    .punto.azul { background: var(--cop-primary); }
    .punto.gris { background: var(--cop-gray); }
    .matriz-torre {
        background: var(--cop-card);
        border: 1px solid var(--cop-border);
        border-radius: var(--cop-radius-lg);
        overflow: hidden;
        margin-bottom: 24px;
        box-shadow: var(--cop-shadow);
    }
    .fila-nivel {
        display: grid;
        grid-template-columns: minmax(8.5rem, 10rem) 1fr;
        border-bottom: 1px solid var(--cop-border);
        min-height: 5.25rem;
    }
    .fila-nivel:last-child { border-bottom: 0; }
    .nombre-nivel {
        display: flex;
        align-items: center;
        padding: 16px;
        background: var(--cop-bg-soft);
        color: var(--cop-text);
        font-weight: 700;
        border-right: 1px solid var(--cop-border);
    }
    .departamentos-nivel {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 12px;
        padding: 16px;
    }
    .tarjeta-departamento {
        width: 6.5rem;
        min-height: 5.2rem;
        border: 1px solid;
        border-left-width: 5px;
        border-radius: var(--cop-radius);
        display: flex;
        flex-direction: column;
        justify-content: center;
        padding: 8px 12px;
        box-sizing: border-box;
        box-shadow: 0 4px 12px rgba(15, 23, 42, .05);
    }
    .tarjeta-departamento strong {
        font-size: 1.05rem;
        line-height: 1.1;
    }
    .tarjeta-departamento small {
        font-size: .66rem;
        margin-top: .16rem;
    }
    @media (max-width: 700px) {
        .cop-hero {
            grid-template-columns: 1fr;
            padding: 18px;
        }
        .cop-action-card {
            min-height: auto;
        }
        .cop-dept-grid {
            grid-template-columns: 1fr;
        }
        .fila-nivel { grid-template-columns: 1fr; }
        .nombre-nivel {
            border-right: 0;
            border-bottom: 1px solid var(--cop-border);
            padding: 12px 16px;
        }
        .tarjeta-departamento { width: 5.8rem; }
        .main .block-container {
            padding: 24px 16px 32px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)
