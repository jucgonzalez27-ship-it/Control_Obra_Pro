import unittest

from database.reglas import calcular_bloqueo, calcular_semaforo


class ReglasBloqueoTest(unittest.TestCase):
    def test_tipo_bloqueante(self):
        self.assertTrue(calcular_bloqueo("Falta material"))

    def test_detalle_menor_no_bloquea(self):
        self.assertFalse(calcular_bloqueo("Otro"))

    def test_retrabajo_bloquea_aunque_el_tipo_no_bloquee(self):
        self.assertTrue(calcular_bloqueo("Falta mano de obra", requiere_retrabajo=True))

    def test_falla_funcional_bloquea(self):
        self.assertTrue(calcular_bloqueo("Otro", afecta_funcionalidad=True))


class ReglasSemaforoTest(unittest.TestCase):
    def test_rojo_si_hay_restriccion_bloqueante_activa(self):
        restricciones = [{"estado": "Abierto", "bloquea_entrega": True}]
        self.assertEqual(calcular_semaforo(restricciones), "Bloqueado")

    def test_amarillo_si_solo_hay_observaciones_activas(self):
        restricciones = [{"estado": "En gestión", "bloquea_entrega": False}]
        self.assertEqual(
            calcular_semaforo(restricciones),
            "Observado no bloqueante",
        )

    def test_verde_si_todo_esta_verificado(self):
        restricciones = [{"estado": "Verificado", "bloquea_entrega": True}]
        self.assertEqual(calcular_semaforo(restricciones), "Liberable")


if __name__ == "__main__":
    unittest.main()
