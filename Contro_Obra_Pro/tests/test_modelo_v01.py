from pathlib import Path
import sqlite3
import tempfile
import unittest

from database.modelo_v01 import conectar, inicializar_base


class ModeloV01Test(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.ruta_db = Path(self.temporal.name) / "prueba.db"
        inicializar_base(self.ruta_db)
        self.conexion = conectar(self.ruta_db)
        self._cargar_datos_base()

    def tearDown(self):
        self.conexion.close()
        self.temporal.cleanup()

    def _id(self, tabla, nombre):
        return self.conexion.execute(
            f"SELECT id FROM {tabla} WHERE nombre = ?",
            (nombre,),
        ).fetchone()["id"]

    def _cargar_datos_base(self):
        self.conexion.execute(
            "INSERT INTO obras (nombre) VALUES ('Obra piloto')"
        )
        obra_id = self.conexion.execute(
            "SELECT id FROM obras WHERE nombre = 'Obra piloto'"
        ).fetchone()["id"]
        self.conexion.execute(
            "INSERT INTO torres (obra_id, nombre) VALUES (?, 'A')",
            (obra_id,),
        )
        torre_id = self.conexion.execute(
            "SELECT id FROM torres WHERE nombre = 'A'"
        ).fetchone()["id"]
        self.conexion.execute(
            """
            INSERT INTO departamentos (torre_id, piso, numero)
            VALUES (?, 2, '201')
            """,
            (torre_id,),
        )
        self.conexion.execute(
            """
            INSERT INTO usuarios (nombre, rol)
            VALUES ('Ana Admin', 'Administrador'),
                   ('Sergio Supervisor', 'Supervisor')
            """
        )
        self.conexion.execute(
            "INSERT INTO responsables (nombre) VALUES ('Raúl Responsable')"
        )
        self.conexion.commit()

    def _crear_problema_y_restriccion(self, tipo="Falta material"):
        self.conexion.execute(
            """
            INSERT INTO problemas_madre (
                titulo, partida_id, tipo_problema_id,
                responsable_id, creado_por_usuario_id
            )
            VALUES (
                'Problema de prueba',
                ?, ?,
                (SELECT id FROM responsables LIMIT 1),
                (SELECT id FROM usuarios WHERE rol = 'Supervisor')
            )
            """,
            (
                self._id("partidas", "Ventanas"),
                self._id("tipos_problema", tipo),
            ),
        )
        problema_id = self.conexion.execute(
            "SELECT id FROM problemas_madre ORDER BY id DESC LIMIT 1"
        ).fetchone()["id"]
        departamento_id = self.conexion.execute(
            "SELECT id FROM departamentos LIMIT 1"
        ).fetchone()["id"]
        recinto_id = self._id("recintos", "Living comedor")
        bloquea = 1 if tipo == "Falta material" else 0
        self.conexion.execute(
            """
            INSERT INTO restricciones (
                problema_madre_id, departamento_id, recinto_id,
                fecha_deteccion, fecha_compromiso, comentario_corto,
                requiere_retrabajo, afecta_funcionalidad, bloquea_entrega
            )
            VALUES (?, ?, ?, '2026-06-24', '2026-06-30',
                    'Comentario obligatorio', 0, 0, ?)
            """,
            (problema_id, departamento_id, recinto_id, bloquea),
        )
        self.conexion.commit()
        return problema_id

    def test_semaforo_se_calcula_desde_restricciones(self):
        self._crear_problema_y_restriccion()
        estado = self.conexion.execute(
            "SELECT estado FROM v_estado_departamentos"
        ).fetchone()["estado"]
        self.assertEqual(estado, "Bloqueado")

    def test_base_rechaza_bloqueo_manual_incorrecto(self):
        with self.assertRaisesRegex(
            sqlite3.IntegrityError,
            "bloquea_entrega no coincide",
        ):
            self.conexion.execute(
                """
                INSERT INTO problemas_madre (
                    titulo, partida_id, tipo_problema_id,
                    responsable_id, creado_por_usuario_id
                )
                VALUES (
                    'Otro problema',
                    ?, ?,
                    (SELECT id FROM responsables LIMIT 1),
                    (SELECT id FROM usuarios LIMIT 1)
                )
                """,
                (
                    self._id("partidas", "Ventanas"),
                    self._id("tipos_problema", "Otro"),
                ),
            )
            problema_id = self.conexion.execute(
                "SELECT id FROM problemas_madre ORDER BY id DESC LIMIT 1"
            ).fetchone()["id"]
            self.conexion.execute(
                """
                INSERT INTO restricciones (
                    problema_madre_id, departamento_id, recinto_id,
                    fecha_deteccion, fecha_compromiso, comentario_corto,
                    requiere_retrabajo, afecta_funcionalidad, bloquea_entrega
                )
                VALUES (
                    ?,
                    (SELECT id FROM departamentos LIMIT 1),
                    ?,
                    '2026-06-24', '2026-06-30', 'Detalle menor',
                    0, 0, 1
                )
                """,
                (problema_id, self._id("recintos", "Living comedor")),
            )

    def test_solo_administrador_puede_verificar(self):
        self._crear_problema_y_restriccion()
        supervisor_id = self.conexion.execute(
            "SELECT id FROM usuarios WHERE rol = 'Supervisor'"
        ).fetchone()["id"]

        with self.assertRaisesRegex(
            sqlite3.IntegrityError,
            "solo un administrador",
        ):
            self.conexion.execute(
                """
                UPDATE restricciones
                SET estado = 'Verificado',
                    verificado_por_usuario_id = ?,
                    fecha_verificacion = CURRENT_TIMESTAMP
                """,
                (supervisor_id,),
            )

    def test_cambio_de_tipo_recalcula_bloqueo(self):
        problema_id = self._crear_problema_y_restriccion()
        self.conexion.execute(
            """
            UPDATE problemas_madre
            SET tipo_problema_id = ?
            WHERE id = ?
            """,
            (self._id("tipos_problema", "Otro"), problema_id),
        )
        bloquea = self.conexion.execute(
            "SELECT bloquea_entrega FROM restricciones"
        ).fetchone()["bloquea_entrega"]
        self.assertEqual(bloquea, 0)


if __name__ == "__main__":
    unittest.main()
