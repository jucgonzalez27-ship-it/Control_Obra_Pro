from pathlib import Path
import sqlite3
import tempfile
import unittest

from database.cargar_configuracion_v1 import cargar_configuracion_v1
from database.modelo_v01 import inicializar_base


DEPARTAMENTOS_MONTEVISTA = [
    (-1, "03"),
    (-1, "04"),
    (-1, "05"),
    (-1, "06"),
    (-1, "07"),
    (1, "13"),
    (1, "14"),
    (1, "15"),
    (1, "16"),
    (1, "17"),
    (1, "18"),
    (2, "23"),
    (2, "24"),
    (2, "25"),
    (2, "26"),
    (2, "27"),
    (2, "28"),
    (2, "29"),
    (3, "33"),
    (3, "34"),
    (3, "35"),
    (3, "36"),
    (3, "37"),
    (3, "38"),
    (3, "39"),
    (4, "43"),
    (4, "44"),
    (4, "45"),
    (4, "46"),
    (4, "47"),
    (4, "48"),
    (4, "49"),
    (5, "53"),
    (5, "54"),
    (5, "55"),
    (5, "56"),
    (5, "57"),
    (5, "58"),
    (5, "59"),
]


class ConfiguracionV1Test(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.ruta_db = Path(self.temporal.name) / "v1.db"
        inicializar_base(self.ruta_db)
        self.conexion = sqlite3.connect(self.ruta_db)
        self.conexion.row_factory = sqlite3.Row
        self._crear_departamentos()

    def tearDown(self):
        self.conexion.close()
        self.temporal.cleanup()

    def _crear_departamentos(self):
        self.conexion.execute(
            "INSERT INTO obras (nombre) VALUES ('PROYECTO MONTEVISTA')"
        )
        obra_id = self.conexion.execute("SELECT id FROM obras").fetchone()["id"]
        self.conexion.execute(
            "INSERT INTO torres (obra_id, nombre) VALUES (?, 'Torre B')",
            (obra_id,),
        )
        torre_id = self.conexion.execute("SELECT id FROM torres").fetchone()["id"]
        self.conexion.executemany(
            """
            INSERT INTO departamentos (torre_id, piso, numero)
            VALUES (?, ?, ?)
            """,
            [(torre_id, piso, numero) for piso, numero in DEPARTAMENTOS_MONTEVISTA],
        )
        self.conexion.commit()

    def test_carga_v1_es_idempotente_y_asigna_departamentos(self):
        cargar_configuracion_v1(self.ruta_db)
        cargar_configuracion_v1(self.ruta_db)

        tipologias = self.conexion.execute(
            "SELECT COUNT(*) FROM tipologias"
        ).fetchone()[0]
        recintos = self.conexion.execute(
            "SELECT COUNT(*) FROM tipologia_recinto"
        ).fetchone()[0]
        asignados = self.conexion.execute(
            """
            SELECT COUNT(*)
            FROM departamentos
            WHERE tipologia_id IS NOT NULL
            """
        ).fetchone()[0]
        living_c1 = self.conexion.execute(
            """
            SELECT COUNT(*)
            FROM recinto_partida rp
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN tipologias tip ON tip.id = tr.tipologia_id
            WHERE tip.nombre = 'C1'
              AND tr.nombre_recinto = 'Living - Comedor'
            """
        ).fetchone()[0]
        dormitorio_c1 = self.conexion.execute(
            """
            SELECT COUNT(*)
            FROM recinto_partida rp
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN tipologias tip ON tip.id = tr.tipologia_id
            WHERE tip.nombre = 'C1'
              AND tr.nombre_recinto = 'Dormitorio Principal'
            """
        ).fetchone()[0]
        bano_principal_c1 = self.conexion.execute(
            """
            SELECT COUNT(*)
            FROM recinto_partida rp
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN tipologias tip ON tip.id = tr.tipologia_id
            WHERE tip.nombre = 'C1'
              AND tr.nombre_recinto = 'Baño 2'
            """
        ).fetchone()[0]
        bano_secundario_c1 = self.conexion.execute(
            """
            SELECT COUNT(*)
            FROM recinto_partida rp
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN tipologias tip ON tip.id = tr.tipologia_id
            WHERE tip.nombre = 'C1'
              AND tr.nombre_recinto = 'Baño 1'
            """
        ).fetchone()[0]
        variantes_banos = self.conexion.execute(
            """
            SELECT
                tr.nombre_recinto,
                SUM(CASE WHEN p.nombre = 'Tina' THEN 1 ELSE 0 END) AS tina,
                SUM(CASE WHEN p.nombre = 'Receptáculo' THEN 1 ELSE 0 END) AS receptaculo,
                SUM(CASE WHEN p.nombre = 'Mampara' THEN 1 ELSE 0 END) AS mampara
            FROM recinto_partida rp
            JOIN partidas p ON p.id = rp.partida_id
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN tipologias tip ON tip.id = tr.tipologia_id
            WHERE tip.nombre = 'C1'
              AND tr.nombre_recinto IN ('Baño 1', 'Baño 2')
            GROUP BY tr.nombre_recinto
            """
        ).fetchall()
        pesos_operativos = self.conexion.execute(
            """
            SELECT tr.nombre_recinto, p.nombre, rp.peso_avance
            FROM recinto_partida rp
            JOIN partidas p ON p.id = rp.partida_id
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN tipologias tip ON tip.id = tr.tipologia_id
            WHERE tip.nombre = 'C1'
              AND (
                (tr.nombre_recinto = 'Living - Comedor'
                 AND p.nombre IN ('Empaste', 'Piso flotante', 'Cerradura'))
                OR (tr.nombre_recinto = 'Cocina'
                 AND p.nombre IN ('Mueble base', 'Mueble aéreo', 'Cubierta', 'Horno'))
                OR (tr.nombre_recinto = 'Dormitorio Principal'
                 AND p.nombre IN ('Closet', 'Mano final de pintura'))
                OR (tr.nombre_recinto = 'Baño 1'
                 AND p.nombre IN ('Cerámica muro', 'Cerámica piso', 'Espejo', 'Tina'))
                OR (tr.nombre_recinto = 'Terraza Principal'
                 AND p.nombre IN ('Textura', 'Piso cerámico'))
              )
            """
        ).fetchall()
        terraza_suite_c1 = self.conexion.execute(
            """
            SELECT COUNT(*)
            FROM recinto_partida rp
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN tipologias tip ON tip.id = tr.tipologia_id
            WHERE tip.nombre = 'C1'
              AND tr.nombre_recinto = 'Terraza Suite'
            """
        ).fetchone()[0]
        walkin_c2 = self.conexion.execute(
            """
            SELECT COUNT(*)
            FROM recinto_partida rp
            JOIN tipologia_recinto tr ON tr.id = rp.tipologia_recinto_id
            JOIN tipologias tip ON tip.id = tr.tipologia_id
            WHERE tip.nombre = 'C2'
              AND tr.nombre_recinto = 'Walk-in Closet'
            """
        ).fetchone()[0]
        recintos_sin_checklist = self.conexion.execute(
            """
            SELECT COUNT(*)
            FROM tipologia_recinto tr
            WHERE NOT EXISTS (
                SELECT 1
                FROM recinto_partida rp
                WHERE rp.tipologia_recinto_id = tr.id
            )
            """
        ).fetchone()[0]
        depto_03 = self.conexion.execute(
            """
            SELECT tip.nombre
            FROM departamentos d
            JOIN tipologias tip ON tip.id = d.tipologia_id
            WHERE d.numero = '03'
            """
        ).fetchone()["nombre"]

        self.assertEqual(tipologias, 5)
        self.assertEqual(recintos, 42)
        self.assertEqual(asignados, 39)
        self.assertEqual(living_c1, 13)
        self.assertEqual(dormitorio_c1, 14)
        self.assertEqual(walkin_c2, dormitorio_c1)
        self.assertEqual(bano_principal_c1, 21)
        self.assertEqual(bano_secundario_c1, 20)
        variantes_por_bano = {fila["nombre_recinto"]: dict(fila) for fila in variantes_banos}
        self.assertEqual(variantes_por_bano["Baño 1"]["tina"], 1)
        self.assertEqual(variantes_por_bano["Baño 1"]["receptaculo"], 0)
        self.assertEqual(variantes_por_bano["Baño 1"]["mampara"], 0)
        self.assertEqual(variantes_por_bano["Baño 2"]["tina"], 0)
        self.assertEqual(variantes_por_bano["Baño 2"]["receptaculo"], 1)
        self.assertEqual(variantes_por_bano["Baño 2"]["mampara"], 1)
        pesos = {
            (fila["nombre_recinto"], fila["nombre"]): fila["peso_avance"]
            for fila in pesos_operativos
        }
        self.assertEqual(pesos[("Living - Comedor", "Empaste")], 2)
        self.assertEqual(pesos[("Living - Comedor", "Piso flotante")], 2)
        self.assertEqual(pesos[("Living - Comedor", "Cerradura")], 1)
        self.assertEqual(pesos[("Cocina", "Mueble base")], 2)
        self.assertEqual(pesos[("Cocina", "Mueble aéreo")], 2)
        self.assertEqual(pesos[("Cocina", "Cubierta")], 2)
        self.assertEqual(pesos[("Cocina", "Horno")], 1)
        self.assertEqual(pesos[("Dormitorio Principal", "Closet")], 2)
        self.assertEqual(pesos[("Dormitorio Principal", "Mano final de pintura")], 2)
        self.assertEqual(pesos[("Baño 1", "Cerámica muro")], 2)
        self.assertEqual(pesos[("Baño 1", "Cerámica piso")], 2)
        self.assertEqual(pesos[("Baño 1", "Espejo")], 1)
        self.assertEqual(pesos[("Baño 1", "Tina")], 1)
        self.assertEqual(pesos[("Terraza Principal", "Textura")], 2)
        self.assertEqual(pesos[("Terraza Principal", "Piso cerámico")], 2)
        self.assertEqual(terraza_suite_c1, 6)
        self.assertEqual(recintos_sin_checklist, 0)
        self.assertEqual(depto_03, "F")


if __name__ == "__main__":
    unittest.main()
