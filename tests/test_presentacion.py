import unittest

from presentacion import clave_numero_departamento, estado_corto, nombre_del_nivel


class PresentacionTest(unittest.TestCase):
    def test_nombre_subterraneo(self):
        self.assertEqual(nombre_del_nivel(-1), "Subterráneo")

    def test_nombre_piso(self):
        self.assertEqual(nombre_del_nivel(3), "Piso 3")

    def test_estado_observado_corto(self):
        self.assertEqual(
            estado_corto("Observado no bloqueante"),
            "Observado",
        )

    def test_departamentos_se_ordenan_numericamente(self):
        numeros = ["100", "03", "20"]
        self.assertEqual(
            sorted(numeros, key=clave_numero_departamento),
            ["03", "20", "100"],
        )


if __name__ == "__main__":
    unittest.main()
