from pathlib import Path
from datetime import date
import tempfile
import unittest

from database.cargar_configuracion_v1 import cargar_configuracion_v1
from database.servicios import (
    asignar_tipologia_departamento,
    asignar_tipologia_departamentos,
    configurar_partidas_tipologia,
    crear_dependencia_critica,
    crear_departamentos,
    crear_obra,
    crear_responsable,
    crear_tipologia,
    crear_torre,
    crear_usuario,
    crear_problema,
    actualizar_estado_partida,
    actualizar_estados_partidas,
    actualizar_configuracion_partida_recinto,
    actualizar_restriccion,
    actualizar_especialidad_partida,
    desactivar_dependencia_critica,
    listar_catalogo,
    listar_departamentos,
    listar_departamentos_seleccionables,
    listar_dependencias_criticas,
    listar_especialidades,
    listar_problemas,
    listar_recintos_tipologia,
    listar_restricciones,
    listar_tipologias,
    obtener_resumen_configuracion,
    obtener_ficha_departamento,
    obtener_avance_departamento,
    obtener_advertencias_dependencias_departamento,
    obtener_checklist_tipologia,
    obtener_dependencias_criticas_partida,
    obtener_dashboard_departamentos,
    obtener_ficha_dashboard_departamento,
    obtener_historial_partidas_departamento,
    obtener_historial_restriccion,
    obtener_partidas_por_especialidad,
    obtener_pendientes_por_especialidad,
    obtener_resumen_pendientes_especialidad,
    obtener_resumen_dashboard,
    obtener_resumen_pisos,
    preparar_base,
)


class ServiciosTest(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.ruta_db = Path(self.temporal.name) / "servicios.db"
        preparar_base(self.ruta_db)

    def tearDown(self):
        self.temporal.cleanup()

    def test_configuracion_inicial_completa(self):
        obra_id = crear_obra("Edificio Piloto", self.ruta_db)
        torre_id = crear_torre(obra_id, "Torre A", self.ruta_db)
        crear_departamentos(
            torre_id,
            [(2, "201"), (2, "202"), (3, "301")],
            self.ruta_db,
        )
        crear_usuario("Ana Administradora", "Administrador", self.ruta_db)
        crear_responsable(
            "Raúl Responsable",
            "Constructora",
            "Capataz",
            self.ruta_db,
        )

        resumen = obtener_resumen_configuracion(self.ruta_db)
        self.assertEqual(
            resumen,
            {
                "obras": 1,
                "torres": 1,
                "departamentos": 3,
                "usuarios": 1,
                "responsables": 1,
            },
        )
        estados = listar_departamentos(self.ruta_db)
        self.assertEqual(len(estados), 3)
        self.assertTrue(
            all(departamento["estado"] == "Sin revisar" for departamento in estados)
        )

    def test_especialidades_v1_mapean_partidas_existentes(self):
        especialidades = listar_especialidades()
        self.assertIn("Puertas", especialidades)
        self.assertIn("Terminaciones Generales", especialidades)

        partidas_puertas = obtener_partidas_por_especialidad(
            "Puertas",
            self.ruta_db,
        )
        self.assertIn(
            "Puerta",
            [partida["nombre"] for partida in partidas_puertas],
        )

    def test_actualizar_especialidad_partida(self):
        partida_id = next(
            partida["id"]
            for partida in listar_catalogo("partidas", self.ruta_db)
            if partida["nombre"] == "Puerta"
        )

        actualizar_especialidad_partida(
            partida_id,
            "Terminaciones Generales",
            self.ruta_db,
        )

        partidas = obtener_partidas_por_especialidad(
            "Terminaciones Generales",
            self.ruta_db,
        )
        self.assertIn("Puerta", [partida["nombre"] for partida in partidas])

    def test_pendientes_por_especialidad_filtra_partidas(self):
        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        crear_departamentos(torre_id, [(1, "101")], self.ruta_db)
        tipologia_id = crear_tipologia("1D", ["Living"], self.ruta_db)
        departamento_id = listar_departamentos_seleccionables(
            self.ruta_db
        )[0]["id"]
        asignar_tipologia_departamento(
            departamento_id,
            tipologia_id,
            self.ruta_db,
        )
        recinto_id = listar_recintos_tipologia(tipologia_id, self.ruta_db)[0]["id"]
        partida_id = next(
            partida["id"]
            for partida in listar_catalogo("partidas", self.ruta_db)
            if partida["nombre"] == "Puerta"
        )
        configurar_partidas_tipologia(recinto_id, [partida_id], self.ruta_db)
        obtener_avance_departamento(departamento_id, self.ruta_db)

        pendientes = obtener_pendientes_por_especialidad("Puertas", self.ruta_db)
        resumen = obtener_resumen_pendientes_especialidad(self.ruta_db)

        self.assertEqual(len(pendientes), 1)
        self.assertEqual(pendientes[0]["especialidad"], "Puertas")
        self.assertEqual(resumen[0]["especialidad"], "Puertas")
        self.assertEqual(resumen[0]["pendientes"], 1)

    def test_dependencias_criticas_cocina_generan_advertencias(self):
        cargar_configuracion_v1(self.ruta_db)
        dependencias = obtener_dependencias_criticas_partida(
            "Cocina",
            "Empaste",
            self.ruta_db,
        )
        self.assertTrue(
            any(dependencia["dependencia"] == "Tabique" for dependencia in dependencias)
        )

        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        crear_departamentos(torre_id, [(1, "101")], self.ruta_db)
        admin_id = crear_usuario("Ana", "Administrador", self.ruta_db)
        tipologia_id = crear_tipologia("1D", ["Cocina"], self.ruta_db)
        departamento_id = listar_departamentos_seleccionables(
            self.ruta_db
        )[0]["id"]
        asignar_tipologia_departamento(
            departamento_id,
            tipologia_id,
            self.ruta_db,
        )
        recinto_id = listar_recintos_tipologia(tipologia_id, self.ruta_db)[0]["id"]
        partidas = {
            partida["nombre"]: partida["id"]
            for partida in listar_catalogo("partidas", self.ruta_db)
        }
        configurar_partidas_tipologia(
            recinto_id,
            [partidas["Tabique"], partidas["Empaste"]],
            self.ruta_db,
        )
        avance = obtener_avance_departamento(departamento_id, self.ruta_db)
        empaste = next(
            partida for partida in avance["partidas"] if partida["partida"] == "Empaste"
        )
        tabique = next(
            partida
            for partida in avance["partidas"]
            if partida["partida"] == "Tabique"
        )

        advertencias = obtener_advertencias_dependencias_departamento(
            departamento_id,
            [empaste["estado_partida_id"]],
            self.ruta_db,
        )
        self.assertEqual(len(advertencias), 1)
        self.assertEqual(advertencias[0]["dependencia"], "Tabique")

        actualizar_estado_partida(
            estado_partida_id=tabique["estado_partida_id"],
            nuevo_estado="terminada",
            usuario_id=admin_id,
            ruta_db=self.ruta_db,
        )
        advertencias = obtener_advertencias_dependencias_departamento(
            departamento_id,
            [empaste["estado_partida_id"]],
            self.ruta_db,
        )
        self.assertEqual(advertencias, [])

    def test_dependencias_criticas_living_comedor_generan_advertencias(self):
        cargar_configuracion_v1(self.ruta_db)
        dependencias = obtener_dependencias_criticas_partida(
            "Living - Comedor",
            "Guardapolvo",
            self.ruta_db,
        )
        self.assertTrue(
            any(dependencia["dependencia"] == "Empaste" for dependencia in dependencias)
        )

        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        crear_departamentos(torre_id, [(1, "101")], self.ruta_db)
        admin_id = crear_usuario("Ana", "Administrador", self.ruta_db)
        tipologia_id = crear_tipologia("1D", ["Living - Comedor"], self.ruta_db)
        departamento_id = listar_departamentos_seleccionables(
            self.ruta_db
        )[0]["id"]
        asignar_tipologia_departamento(
            departamento_id,
            tipologia_id,
            self.ruta_db,
        )
        recinto_id = listar_recintos_tipologia(tipologia_id, self.ruta_db)[0]["id"]
        partidas = {
            partida["nombre"]: partida["id"]
            for partida in listar_catalogo("partidas", self.ruta_db)
        }
        configurar_partidas_tipologia(
            recinto_id,
            [partidas["Empaste"], partidas["Guardapolvo"]],
            self.ruta_db,
        )
        avance = obtener_avance_departamento(departamento_id, self.ruta_db)
        empaste = next(
            partida for partida in avance["partidas"] if partida["partida"] == "Empaste"
        )
        guardapolvo = next(
            partida
            for partida in avance["partidas"]
            if partida["partida"] == "Guardapolvo"
        )

        advertencias = obtener_advertencias_dependencias_departamento(
            departamento_id,
            [guardapolvo["estado_partida_id"]],
            self.ruta_db,
        )
        self.assertEqual(len(advertencias), 1)
        self.assertEqual(advertencias[0]["dependencia"], "Empaste")

        actualizar_estado_partida(
            estado_partida_id=empaste["estado_partida_id"],
            nuevo_estado="terminada",
            usuario_id=admin_id,
            ruta_db=self.ruta_db,
        )
        advertencias = obtener_advertencias_dependencias_departamento(
            departamento_id,
            [guardapolvo["estado_partida_id"]],
            self.ruta_db,
        )
        self.assertEqual(advertencias, [])

    def test_dependencias_criticas_or_generan_una_advertencia_por_grupo(self):
        cargar_configuracion_v1(self.ruta_db)
        crear_dependencia_critica(
            recinto="Baño 1",
            partida="Vanitorio",
            dependencia="Fragüe",
            descripcion="Fragüe muro terminado o mano final pintura terminada",
            grupo=1,
            tipo_condicion="OR",
            ruta_db=self.ruta_db,
        )
        crear_dependencia_critica(
            recinto="Baño 1",
            partida="Vanitorio",
            dependencia="Mano final de pintura",
            descripcion="Fragüe muro terminado o mano final pintura terminada",
            grupo=1,
            tipo_condicion="OR",
            ruta_db=self.ruta_db,
        )

        dependencias = obtener_dependencias_criticas_partida(
            "Baño 1",
            "Vanitorio",
            self.ruta_db,
        )
        self.assertEqual(
            {dependencia["tipo_condicion"] for dependencia in dependencias},
            {"OR"},
        )

        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        crear_departamentos(torre_id, [(1, "101")], self.ruta_db)
        admin_id = crear_usuario("Ana", "Administrador", self.ruta_db)
        tipologia_id = crear_tipologia("1B", ["Baño 1"], self.ruta_db)
        departamento_id = listar_departamentos_seleccionables(
            self.ruta_db
        )[0]["id"]
        asignar_tipologia_departamento(
            departamento_id,
            tipologia_id,
            self.ruta_db,
        )
        recinto_id = listar_recintos_tipologia(tipologia_id, self.ruta_db)[0]["id"]
        partidas = {
            partida["nombre"]: partida["id"]
            for partida in listar_catalogo("partidas", self.ruta_db)
        }
        configurar_partidas_tipologia(
            recinto_id,
            [
                partidas["Fragüe"],
                partidas["Mano final de pintura"],
                partidas["Vanitorio"],
            ],
            self.ruta_db,
        )
        avance = obtener_avance_departamento(departamento_id, self.ruta_db)
        frague = next(
            partida for partida in avance["partidas"] if partida["partida"] == "Fragüe"
        )
        vanitorio = next(
            partida
            for partida in avance["partidas"]
            if partida["partida"] == "Vanitorio"
        )

        advertencias = obtener_advertencias_dependencias_departamento(
            departamento_id,
            [vanitorio["estado_partida_id"]],
            self.ruta_db,
        )
        self.assertEqual(len(advertencias), 1)
        self.assertEqual(
            advertencias[0]["dependencia"],
            "Fragüe OR Mano final de pintura",
        )

        actualizar_estado_partida(
            estado_partida_id=frague["estado_partida_id"],
            nuevo_estado="terminada",
            usuario_id=admin_id,
            ruta_db=self.ruta_db,
        )
        advertencias = obtener_advertencias_dependencias_departamento(
            departamento_id,
            [vanitorio["estado_partida_id"]],
            self.ruta_db,
        )
        self.assertEqual(advertencias, [])

    def test_dependencias_criticas_banos_y_variantes_por_tipologia(self):
        cargar_configuracion_v1(self.ruta_db)

        self.assertEqual(
            obtener_dependencias_criticas_partida(
                "Baño 1",
                "Tina",
                self.ruta_db,
            ),
            [],
        )
        self.assertEqual(
            obtener_dependencias_criticas_partida(
                "Baño 2",
                "Receptáculo",
                self.ruta_db,
            ),
            [],
        )
        dependencias_mampara = obtener_dependencias_criticas_partida(
            "Baño 2",
            "Mampara",
            self.ruta_db,
        )
        dependencias_espejo = obtener_dependencias_criticas_partida(
            "Baño 1",
            "Espejo",
            self.ruta_db,
        )
        self.assertEqual(
            [dependencia["dependencia"] for dependencia in dependencias_mampara],
            ["Receptáculo"],
        )
        self.assertEqual(
            [dependencia["dependencia"] for dependencia in dependencias_espejo],
            ["Fragüe muro"],
        )

        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        crear_departamentos(torre_id, [(1, "101")], self.ruta_db)
        admin_id = crear_usuario("Ana", "Administrador", self.ruta_db)
        tipologia_id = crear_tipologia("1B", ["Baño 2"], self.ruta_db)
        departamento_id = listar_departamentos_seleccionables(
            self.ruta_db
        )[0]["id"]
        asignar_tipologia_departamento(
            departamento_id,
            tipologia_id,
            self.ruta_db,
        )
        recinto_id = listar_recintos_tipologia(tipologia_id, self.ruta_db)[0]["id"]
        partidas = {
            partida["nombre"]: partida["id"]
            for partida in listar_catalogo("partidas", self.ruta_db)
        }
        configurar_partidas_tipologia(
            recinto_id,
            [partidas["Receptáculo"], partidas["Mampara"]],
            self.ruta_db,
        )
        avance = obtener_avance_departamento(departamento_id, self.ruta_db)
        receptaculo = next(
            partida
            for partida in avance["partidas"]
            if partida["partida"] == "Receptáculo"
        )
        mampara = next(
            partida for partida in avance["partidas"] if partida["partida"] == "Mampara"
        )

        advertencias = obtener_advertencias_dependencias_departamento(
            departamento_id,
            [mampara["estado_partida_id"]],
            self.ruta_db,
        )
        self.assertEqual(len(advertencias), 1)
        self.assertEqual(advertencias[0]["dependencia"], "Receptáculo")

        actualizar_estado_partida(
            estado_partida_id=receptaculo["estado_partida_id"],
            nuevo_estado="terminada",
            usuario_id=admin_id,
            ruta_db=self.ruta_db,
        )
        advertencias = obtener_advertencias_dependencias_departamento(
            departamento_id,
            [mampara["estado_partida_id"]],
            self.ruta_db,
        )
        self.assertEqual(advertencias, [])

    def test_dependencias_dormitorio_y_configuracion_editable(self):
        dependencias_guardapolvo = obtener_dependencias_criticas_partida(
            "Dormitorio 1",
            "Guardapolvo",
            self.ruta_db,
        )
        dependencias_piso = obtener_dependencias_criticas_partida(
            "Dormitorio 1",
            "Piso flotante",
            self.ruta_db,
        )
        dependencias_junquillo = obtener_dependencias_criticas_partida(
            "Dormitorio 1",
            "Junquillo",
            self.ruta_db,
        )

        self.assertEqual(
            [dependencia["dependencia"] for dependencia in dependencias_guardapolvo],
            ["Empaste"],
        )
        self.assertEqual(dependencias_piso, [])
        self.assertEqual(
            [dependencia["dependencia"] for dependencia in dependencias_junquillo],
            ["Piso flotante"],
        )

        dependencia_id = crear_dependencia_critica(
            recinto="Dormitorio 1",
            partida="Guardapolvo",
            dependencia="Piso flotante",
            descripcion="Regla temporal de prueba",
            ruta_db=self.ruta_db,
        )
        desactivar_dependencia_critica(dependencia_id, self.ruta_db)
        preparar_base(self.ruta_db)

        dependencias = listar_dependencias_criticas(self.ruta_db)
        temporal = next(
            dependencia
            for dependencia in dependencias
            if dependencia["id"] == dependencia_id
        )
        self.assertEqual(temporal["activa"], 0)

    def test_dormitorio_hereda_dependencias_y_partidas_base(self):
        cargar_configuracion_v1(self.ruta_db)

        dependencias_radiador = obtener_dependencias_criticas_partida(
            "Dormitorio 1",
            "Radiador",
            self.ruta_db,
        )
        dependencias_cornisa = obtener_dependencias_criticas_partida(
            "Dormitorio 1",
            "Cornisa",
            self.ruta_db,
        )
        dependencias_puerta = obtener_dependencias_criticas_partida(
            "Dormitorio 1",
            "Cerradura",
            self.ruta_db,
        )

        self.assertTrue(
            any(dependencia["dependencia"] == "Tabique" for dependencia in dependencias_radiador)
        )
        self.assertEqual(
            [dependencia["dependencia"] for dependencia in dependencias_cornisa],
            ["Empaste"],
        )
        self.assertEqual(
            [dependencia["dependencia"] for dependencia in dependencias_puerta],
            ["Puerta"],
        )

        tipologias = listar_tipologias(self.ruta_db)
        c1_id = next(
            tipologia["id"] for tipologia in tipologias if tipologia["nombre"] == "C1"
        )
        c2_id = next(
            tipologia["id"] for tipologia in tipologias if tipologia["nombre"] == "C2"
        )
        checklist_c1 = obtener_checklist_tipologia(c1_id, self.ruta_db)
        dormitorio_principal = next(
            recinto
            for recinto in checklist_c1
            if recinto["nombre"] == "Dormitorio Principal"
        )
        nombres = {partida["nombre"] for partida in dormitorio_principal["partidas"]}
        self.assertIn("Closet", nombres)
        self.assertIn("Radiador", nombres)

        recintos_c2 = listar_recintos_tipologia(c2_id, self.ruta_db)
        self.assertIn(
            "Walk-in Closet",
            {recinto["nombre"] for recinto in recintos_c2},
        )

    def test_walkin_closet_hereda_configuracion_de_dormitorio(self):
        cargar_configuracion_v1(self.ruta_db)

        tipologias = listar_tipologias(self.ruta_db)
        c2_id = next(
            tipologia["id"] for tipologia in tipologias if tipologia["nombre"] == "C2"
        )
        checklist = obtener_checklist_tipologia(c2_id, self.ruta_db)
        dormitorio = next(
            recinto for recinto in checklist if recinto["nombre"] == "Dormitorio 1"
        )
        walkin = next(
            recinto for recinto in checklist if recinto["nombre"] == "Walk-in Closet"
        )
        self.assertEqual(
            [partida["nombre"] for partida in walkin["partidas"]],
            [partida["nombre"] for partida in dormitorio["partidas"]],
        )

        dependencias_heredadas = obtener_dependencias_criticas_partida(
            "Walk-in Closet",
            "Guardapolvo",
            self.ruta_db,
        )
        self.assertEqual(
            [dependencia["dependencia"] for dependencia in dependencias_heredadas],
            ["Empaste"],
        )
        self.assertEqual(dependencias_heredadas[0]["recinto"], "Dormitorio")

        crear_dependencia_critica(
            recinto="Walk-in Closet",
            partida="Guardapolvo",
            dependencia="Piso flotante",
            descripcion="Sobrescritura de prueba",
            ruta_db=self.ruta_db,
        )
        dependencias_propias = obtener_dependencias_criticas_partida(
            "Walk-in Closet",
            "Guardapolvo",
            self.ruta_db,
        )
        self.assertEqual(
            [dependencia["dependencia"] for dependencia in dependencias_propias],
            ["Piso flotante"],
        )

    def test_rechaza_departamentos_repetidos_en_misma_carga(self):
        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        with self.assertRaisesRegex(ValueError, "repetido"):
            crear_departamentos(
                torre_id,
                [(2, "201"), (3, "201")],
                self.ruta_db,
            )

    def test_crear_problema_multiple_actualiza_semaforo(self):
        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        crear_departamentos(
            torre_id,
            [(2, "201"), (2, "202")],
            self.ruta_db,
        )
        usuario_id = crear_usuario(
            "Ana",
            "Administrador",
            self.ruta_db,
        )
        responsable_id = crear_responsable(
            "Raúl",
            ruta_db=self.ruta_db,
        )
        departamentos = listar_departamentos_seleccionables(self.ruta_db)
        partida_id = listar_catalogo("partidas", self.ruta_db)[0]["id"]
        tipo_id = next(
            tipo["id"]
            for tipo in listar_catalogo("tipos_problema", self.ruta_db)
            if tipo["nombre"] == "Falta material"
        )
        recinto_id = listar_catalogo("recintos", self.ruta_db)[0]["id"]

        problema_id = crear_problema(
            titulo="Faltan ventanas",
            partida_id=partida_id,
            tipo_problema_id=tipo_id,
            responsable_id=responsable_id,
            creado_por_usuario_id=usuario_id,
            departamento_ids=[departamento["id"] for departamento in departamentos],
            recinto_id=recinto_id,
            fecha_deteccion=date(2026, 6, 24),
            fecha_compromiso=date(2026, 6, 30),
            comentario_corto="No llegaron los perfiles.",
            requiere_retrabajo=False,
            afecta_funcionalidad=False,
            ruta_db=self.ruta_db,
        )

        self.assertEqual(problema_id, 1)
        problemas = listar_problemas(self.ruta_db)
        self.assertEqual(problemas[0]["departamentos_afectados"], 2)
        self.assertEqual(problemas[0]["bloquea_entrega"], 1)
        estados = listar_departamentos(self.ruta_db)
        self.assertTrue(
            all(departamento["estado"] == "Bloqueado" for departamento in estados)
        )

    def test_fecha_compromiso_no_puede_ser_anterior(self):
        with self.assertRaisesRegex(ValueError, "no puede ser anterior"):
            crear_problema(
                titulo="Problema",
                partida_id=1,
                tipo_problema_id=1,
                responsable_id=1,
                creado_por_usuario_id=1,
                departamento_ids=[1],
                recinto_id=1,
                fecha_deteccion=date(2026, 6, 24),
                fecha_compromiso=date(2026, 6, 23),
                comentario_corto="Comentario",
                requiere_retrabajo=False,
                afecta_funcionalidad=False,
                ruta_db=self.ruta_db,
            )

    def test_flujo_individual_hasta_verificado(self):
        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        crear_departamentos(torre_id, [(2, "201")], self.ruta_db)
        admin_id = crear_usuario("Ana", "Administrador", self.ruta_db)
        supervisor_id = crear_usuario("Sergio", "Supervisor", self.ruta_db)
        responsable_id = crear_responsable("Raúl", ruta_db=self.ruta_db)
        departamento_id = listar_departamentos_seleccionables(
            self.ruta_db
        )[0]["id"]
        tipo_id = next(
            tipo["id"]
            for tipo in listar_catalogo("tipos_problema", self.ruta_db)
            if tipo["nombre"] == "Falta material"
        )
        crear_problema(
            titulo="Faltan ventanas",
            partida_id=listar_catalogo("partidas", self.ruta_db)[0]["id"],
            tipo_problema_id=tipo_id,
            responsable_id=responsable_id,
            creado_por_usuario_id=supervisor_id,
            departamento_ids=[departamento_id],
            recinto_id=listar_catalogo("recintos", self.ruta_db)[0]["id"],
            fecha_deteccion=date(2026, 6, 24),
            fecha_compromiso=date(2026, 6, 30),
            comentario_corto="Faltan perfiles.",
            requiere_retrabajo=False,
            afecta_funcionalidad=False,
            ruta_db=self.ruta_db,
        )
        restriccion_id = listar_restricciones(self.ruta_db)[0]["id"]

        actualizar_restriccion(
            restriccion_id=restriccion_id,
            usuario_id=supervisor_id,
            nuevo_estado="En gestión",
            fecha_compromiso=date(2026, 7, 1),
            comentario_corto="Perfiles solicitados.",
            ruta_db=self.ruta_db,
        )
        actualizar_restriccion(
            restriccion_id=restriccion_id,
            usuario_id=supervisor_id,
            nuevo_estado="Resuelto",
            fecha_compromiso=date(2026, 7, 1),
            comentario_corto="Perfiles instalados.",
            nota_seguimiento="Trabajo terminado.",
            ruta_db=self.ruta_db,
        )
        estado_antes = listar_departamentos(self.ruta_db)[0]["estado"]
        self.assertEqual(estado_antes, "Bloqueado")

        actualizar_restriccion(
            restriccion_id=restriccion_id,
            usuario_id=admin_id,
            nuevo_estado="Verificado",
            fecha_compromiso=date(2026, 7, 1),
            comentario_corto="Perfiles instalados.",
            ruta_db=self.ruta_db,
        )
        estado_despues = listar_departamentos(self.ruta_db)[0]["estado"]
        self.assertEqual(estado_despues, "Sin revisar")
        historial = obtener_historial_restriccion(
            restriccion_id,
            self.ruta_db,
        )
        self.assertEqual(len(historial), 3)

    def test_supervisor_no_puede_verificar(self):
        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        crear_departamentos(torre_id, [(2, "201")], self.ruta_db)
        supervisor_id = crear_usuario("Sergio", "Supervisor", self.ruta_db)
        responsable_id = crear_responsable("Raúl", ruta_db=self.ruta_db)
        crear_problema(
            titulo="Detalle",
            partida_id=listar_catalogo("partidas", self.ruta_db)[0]["id"],
            tipo_problema_id=listar_catalogo(
                "tipos_problema",
                self.ruta_db,
            )[0]["id"],
            responsable_id=responsable_id,
            creado_por_usuario_id=supervisor_id,
            departamento_ids=[
                listar_departamentos_seleccionables(self.ruta_db)[0]["id"]
            ],
            recinto_id=listar_catalogo("recintos", self.ruta_db)[0]["id"],
            fecha_deteccion=date(2026, 6, 24),
            fecha_compromiso=date(2026, 6, 30),
            comentario_corto="Detalle.",
            requiere_retrabajo=False,
            afecta_funcionalidad=False,
            ruta_db=self.ruta_db,
        )
        restriccion_id = listar_restricciones(self.ruta_db)[0]["id"]
        actualizar_restriccion(
            restriccion_id=restriccion_id,
            usuario_id=supervisor_id,
            nuevo_estado="En gestión",
            fecha_compromiso=date(2026, 6, 30),
            comentario_corto="En trabajo.",
            ruta_db=self.ruta_db,
        )
        actualizar_restriccion(
            restriccion_id=restriccion_id,
            usuario_id=supervisor_id,
            nuevo_estado="Resuelto",
            fecha_compromiso=date(2026, 6, 30),
            comentario_corto="Terminado.",
            ruta_db=self.ruta_db,
        )
        with self.assertRaisesRegex(ValueError, "Solo un administrador"):
            actualizar_restriccion(
                restriccion_id=restriccion_id,
                usuario_id=supervisor_id,
                nuevo_estado="Verificado",
                fecha_compromiso=date(2026, 6, 30),
                comentario_corto="Terminado.",
                ruta_db=self.ruta_db,
            )

    def test_ficha_departamento_incluye_tipologia_y_recintos(self):
        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        crear_departamentos(torre_id, [(2, "201")], self.ruta_db)
        departamento_id = listar_departamentos_seleccionables(
            self.ruta_db
        )[0]["id"]
        tipologia_id = crear_tipologia(
            "2D",
            ["Living", "Dormitorio 1", "Dormitorio 2", "Baño"],
            self.ruta_db,
        )
        asignar_tipologia_departamento(
            departamento_id,
            tipologia_id,
            self.ruta_db,
        )

        ficha = obtener_ficha_departamento(
            departamento_id,
            self.ruta_db,
        )

        self.assertEqual(ficha["tipologia"], "2D")
        self.assertEqual(ficha["etapa_actual"], "obra_gruesa")
        self.assertEqual(ficha["estado_operativo"], "sin_revisar")
        self.assertEqual(
            [recinto["nombre"] for recinto in ficha["recintos"]],
            ["Living", "Dormitorio 1", "Dormitorio 2", "Baño"],
        )
        self.assertEqual(ficha["observaciones_activas"], [])

    def test_ficha_funciona_sin_tipologia_asignada(self):
        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        crear_departamentos(torre_id, [(2, "201")], self.ruta_db)
        departamento_id = listar_departamentos_seleccionables(
            self.ruta_db
        )[0]["id"]

        ficha = obtener_ficha_departamento(
            departamento_id,
            self.ruta_db,
        )

        self.assertIsNone(ficha["tipologia"])
        self.assertEqual(ficha["recintos"], [])

    def test_asignacion_masiva_de_tipologia(self):
        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        crear_departamentos(
            torre_id,
            [(1, "101"), (1, "102"), (2, "201")],
            self.ruta_db,
        )
        tipologia_id = crear_tipologia(
            "2D",
            ["Living", "Dormitorio 1", "Dormitorio 2"],
            self.ruta_db,
        )
        departamentos = listar_departamentos_seleccionables(self.ruta_db)

        cantidad = asignar_tipologia_departamentos(
            [departamento["id"] for departamento in departamentos[:2]],
            tipologia_id,
            self.ruta_db,
        )

        self.assertEqual(cantidad, 2)
        tipologia = listar_tipologias(self.ruta_db)[0]
        self.assertEqual(tipologia["departamentos_asignados"], 2)
        self.assertEqual(
            tipologia["recintos"],
            ["Living", "Dormitorio 1", "Dormitorio 2"],
        )

    def test_asignacion_masiva_requiere_departamentos(self):
        tipologia_id = crear_tipologia(
            "2D",
            ["Living"],
            self.ruta_db,
        )
        with self.assertRaisesRegex(ValueError, "al menos un departamento"):
            asignar_tipologia_departamentos(
                [],
                tipologia_id,
                self.ruta_db,
            )

    def test_configurar_partidas_de_un_recinto(self):
        tipologia_id = crear_tipologia(
            "2D",
            ["Living", "Baño"],
            self.ruta_db,
        )
        recinto_id = listar_recintos_tipologia(
            tipologia_id,
            self.ruta_db,
        )[0]["id"]
        partidas = listar_catalogo("partidas", self.ruta_db)

        cantidad = configurar_partidas_tipologia(
            recinto_id,
            [partidas[0]["id"], partidas[1]["id"]],
            self.ruta_db,
        )

        self.assertEqual(cantidad, 2)
        checklist = obtener_checklist_tipologia(
            tipologia_id,
            self.ruta_db,
        )
        self.assertEqual(len(checklist[0]["partidas"]), 2)
        self.assertEqual(checklist[1]["partidas"], [])

    def test_reconfigurar_reemplaza_el_checklist_anterior(self):
        tipologia_id = crear_tipologia(
            "2D",
            ["Living"],
            self.ruta_db,
        )
        recinto_id = listar_recintos_tipologia(
            tipologia_id,
            self.ruta_db,
        )[0]["id"]
        partidas = listar_catalogo("partidas", self.ruta_db)
        configurar_partidas_tipologia(
            recinto_id,
            [partidas[0]["id"], partidas[1]["id"]],
            self.ruta_db,
        )

        configurar_partidas_tipologia(
            recinto_id,
            [partidas[2]["id"]],
            self.ruta_db,
        )

        checklist = obtener_checklist_tipologia(
            tipologia_id,
            self.ruta_db,
        )
        self.assertEqual(
            [partida["id"] for partida in checklist[0]["partidas"]],
            [partidas[2]["id"]],
        )

    def test_avance_de_departamento_se_calcula_desde_partidas(self):
        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        crear_departamentos(torre_id, [(1, "101")], self.ruta_db)
        usuario_id = crear_usuario("Ana", "Administrador", self.ruta_db)
        tipologia_id = crear_tipologia(
            "1D",
            ["Living"],
            self.ruta_db,
        )
        departamento_id = listar_departamentos_seleccionables(
            self.ruta_db
        )[0]["id"]
        asignar_tipologia_departamento(
            departamento_id,
            tipologia_id,
            self.ruta_db,
        )
        recinto_id = listar_recintos_tipologia(
            tipologia_id,
            self.ruta_db,
        )[0]["id"]
        partidas = listar_catalogo("partidas", self.ruta_db)[:2]
        configurar_partidas_tipologia(
            recinto_id,
            [partida["id"] for partida in partidas],
            self.ruta_db,
        )
        avance = obtener_avance_departamento(
            departamento_id,
            self.ruta_db,
        )
        self.assertEqual(avance["avance_porcentaje"], 0)

        actualizar_estado_partida(
            estado_partida_id=avance["partidas"][0]["estado_partida_id"],
            nuevo_estado="terminada",
            usuario_id=usuario_id,
            ruta_db=self.ruta_db,
        )
        avance = obtener_avance_departamento(
            departamento_id,
            self.ruta_db,
        )
        self.assertEqual(avance["avance_porcentaje"], 0)
        self.assertEqual(avance["avance_oficial_porcentaje"], 0)
        self.assertEqual(avance["avance_declarado_porcentaje"], 50)
        self.assertEqual(avance["estado_operativo"], "en_proceso")

        actualizar_estado_partida(
            estado_partida_id=avance["partidas"][1]["estado_partida_id"],
            nuevo_estado="verificada",
            usuario_id=usuario_id,
            ruta_db=self.ruta_db,
        )
        avance = obtener_avance_departamento(
            departamento_id,
            self.ruta_db,
        )
        self.assertEqual(avance["avance_porcentaje"], 50)
        self.assertEqual(avance["avance_oficial_porcentaje"], 50)
        self.assertEqual(avance["avance_declarado_porcentaje"], 100)
        self.assertEqual(avance["estado_operativo"], "en_proceso")

    def test_avance_ponderado_deriva_obligatoriedad_de_aplicabilidad(self):
        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        crear_departamentos(torre_id, [(1, "101")], self.ruta_db)
        usuario_id = crear_usuario("Ana", "Administrador", self.ruta_db)
        tipologia_id = crear_tipologia("1D", ["Living"], self.ruta_db)
        departamento_id = listar_departamentos_seleccionables(
            self.ruta_db
        )[0]["id"]
        asignar_tipologia_departamento(
            departamento_id,
            tipologia_id,
            self.ruta_db,
        )
        recinto_id = listar_recintos_tipologia(
            tipologia_id,
            self.ruta_db,
        )[0]["id"]
        partidas = listar_catalogo("partidas", self.ruta_db)[:2]
        configurar_partidas_tipologia(
            recinto_id,
            [partida["id"] for partida in partidas],
            self.ruta_db,
        )
        checklist = obtener_checklist_tipologia(tipologia_id, self.ruta_db)
        principal = checklist[0]["partidas"][0]
        no_aplicable = checklist[0]["partidas"][1]
        actualizar_configuracion_partida_recinto(
            recinto_partida_id=principal["recinto_partida_id"],
            peso_avance=2,
            ruta_db=self.ruta_db,
        )
        actualizar_configuracion_partida_recinto(
            recinto_partida_id=no_aplicable["recinto_partida_id"],
            peso_avance=1,
            ruta_db=self.ruta_db,
        )
        avance = obtener_avance_departamento(departamento_id, self.ruta_db)

        actualizar_estado_partida(
            estado_partida_id=avance["partidas"][0]["estado_partida_id"],
            nuevo_estado="verificada",
            usuario_id=usuario_id,
            ruta_db=self.ruta_db,
        )

        avance = obtener_avance_departamento(departamento_id, self.ruta_db)
        self.assertEqual(avance["avance_oficial_porcentaje"], 67)
        self.assertEqual(avance["estado_operativo"], "en_proceso")

        actualizar_estado_partida(
            estado_partida_id=avance["partidas"][1]["estado_partida_id"],
            nuevo_estado="no_aplica",
            usuario_id=usuario_id,
            ruta_db=self.ruta_db,
        )

        avance = obtener_avance_departamento(departamento_id, self.ruta_db)
        self.assertEqual(avance["avance_oficial_porcentaje"], 100)
        self.assertEqual(avance["estado_operativo"], "liberable")

    def test_partida_bloqueada_exige_restriccion(self):
        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        crear_departamentos(torre_id, [(1, "101")], self.ruta_db)
        usuario_id = crear_usuario("Ana", "Administrador", self.ruta_db)
        responsable_id = crear_responsable("Raúl", ruta_db=self.ruta_db)
        tipologia_id = crear_tipologia("1D", ["Living"], self.ruta_db)
        departamento_id = listar_departamentos_seleccionables(
            self.ruta_db
        )[0]["id"]
        asignar_tipologia_departamento(
            departamento_id,
            tipologia_id,
            self.ruta_db,
        )
        recinto_id = listar_recintos_tipologia(
            tipologia_id,
            self.ruta_db,
        )[0]["id"]
        partida_id = listar_catalogo("partidas", self.ruta_db)[0]["id"]
        configurar_partidas_tipologia(
            recinto_id,
            [partida_id],
            self.ruta_db,
        )
        estado_partida_id = obtener_avance_departamento(
            departamento_id,
            self.ruta_db,
        )["partidas"][0]["estado_partida_id"]

        with self.assertRaisesRegex(ValueError, "causa es obligatoria"):
            actualizar_estado_partida(
                estado_partida_id=estado_partida_id,
                nuevo_estado="bloqueada",
                usuario_id=usuario_id,
                ruta_db=self.ruta_db,
            )

        estado = actualizar_estado_partida(
            estado_partida_id=estado_partida_id,
            nuevo_estado="bloqueada",
            usuario_id=usuario_id,
            causa="Falta material",
            responsable_id=responsable_id,
            fecha_compromiso=date(2026, 7, 1),
            comentario="Pendiente proveedor.",
            ruta_db=self.ruta_db,
        )
        self.assertEqual(estado, "bloqueado")

    def test_actualizacion_masiva_registra_historial_y_respeta_roles(self):
        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        crear_departamentos(torre_id, [(1, "101")], self.ruta_db)
        admin_id = crear_usuario("Ana", "Administrador", self.ruta_db)
        supervisor_id = crear_usuario("Sergio", "Supervisor", self.ruta_db)
        tipologia_id = crear_tipologia("1D", ["Living"], self.ruta_db)
        departamento_id = listar_departamentos_seleccionables(
            self.ruta_db
        )[0]["id"]
        asignar_tipologia_departamento(
            departamento_id,
            tipologia_id,
            self.ruta_db,
        )
        recinto_id = listar_recintos_tipologia(
            tipologia_id,
            self.ruta_db,
        )[0]["id"]
        partidas = listar_catalogo("partidas", self.ruta_db)[:2]
        configurar_partidas_tipologia(
            recinto_id,
            [partida["id"] for partida in partidas],
            self.ruta_db,
        )
        avance = obtener_avance_departamento(departamento_id, self.ruta_db)
        estado_ids = [
            partida["estado_partida_id"] for partida in avance["partidas"]
        ]

        resultado = actualizar_estados_partidas(
            estado_partida_ids=estado_ids,
            nuevo_estado="observada",
            usuario_id=supervisor_id,
            comentario="Detalles menores por revisar.",
            ruta_db=self.ruta_db,
        )

        self.assertEqual(resultado["actualizadas"], 2)
        self.assertEqual(resultado["estado_operativo"], "observado")
        historial = obtener_historial_partidas_departamento(
            departamento_id,
            ruta_db=self.ruta_db,
        )
        self.assertEqual(len(historial), 2)
        self.assertEqual(historial[0]["estado_nuevo"], "observada")
        self.assertEqual(historial[0]["comentario"], "Detalles menores por revisar.")

        with self.assertRaisesRegex(ValueError, "Solo un administrador"):
            actualizar_estado_partida(
                estado_partida_id=estado_ids[0],
                nuevo_estado="verificada",
                usuario_id=supervisor_id,
                ruta_db=self.ruta_db,
            )

        actualizar_estado_partida(
            estado_partida_id=estado_ids[0],
            nuevo_estado="verificada",
            usuario_id=admin_id,
            comentario="Verificado en terreno.",
            ruta_db=self.ruta_db,
        )

    def test_dashboard_resume_departamentos_pisos_y_ficha(self):
        obra_id = crear_obra("Obra", self.ruta_db)
        torre_id = crear_torre(obra_id, "A", self.ruta_db)
        crear_departamentos(
            torre_id,
            [(1, "101"), (1, "102")],
            self.ruta_db,
        )
        admin_id = crear_usuario("Ana", "Administrador", self.ruta_db)
        responsable_id = crear_responsable("Raúl", ruta_db=self.ruta_db)
        tipologia_id = crear_tipologia("1D", ["Living"], self.ruta_db)
        departamentos = listar_departamentos_seleccionables(self.ruta_db)
        asignar_tipologia_departamentos(
            [departamento["id"] for departamento in departamentos],
            tipologia_id,
            self.ruta_db,
        )
        recinto_id = listar_recintos_tipologia(tipologia_id, self.ruta_db)[0]["id"]
        partidas = listar_catalogo("partidas", self.ruta_db)[:2]
        configurar_partidas_tipologia(
            recinto_id,
            [partida["id"] for partida in partidas],
            self.ruta_db,
        )
        avance = obtener_avance_departamento(departamentos[0]["id"], self.ruta_db)
        actualizar_estado_partida(
            estado_partida_id=avance["partidas"][0]["estado_partida_id"],
            nuevo_estado="bloqueada",
            usuario_id=admin_id,
            causa="Falta material",
            responsable_id=responsable_id,
            fecha_compromiso=date(2026, 7, 1),
            comentario="Pendiente proveedor.",
            ruta_db=self.ruta_db,
        )

        dashboard = obtener_dashboard_departamentos(self.ruta_db)
        resumen = obtener_resumen_dashboard(self.ruta_db)
        pisos = obtener_resumen_pisos(self.ruta_db)
        ficha = obtener_ficha_dashboard_departamento(
            departamentos[0]["id"],
            self.ruta_db,
        )

        depto_101 = next(
            departamento
            for departamento in dashboard
            if departamento["departamento"] == "101"
        )
        self.assertEqual(depto_101["estado"], "Bloqueado")
        self.assertEqual(depto_101["bloqueos_activos"], 1)
        self.assertEqual(depto_101["responsable_principal"], "Raúl")
        self.assertEqual(resumen["total"], 2)
        self.assertEqual(resumen["bloqueados"], 1)
        self.assertEqual(pisos[0]["bloqueados"], 1)
        self.assertEqual(len(ficha["bloqueos"]), 1)
        self.assertGreaterEqual(len(ficha["pendientes"]), 1)


if __name__ == "__main__":
    unittest.main()
