"""Inicializa una base V0.1 limpia sin modificar obra.db."""

from modelo_v01 import inicializar_base


if __name__ == "__main__":
    ruta = inicializar_base()
    print(f"Base V0.1 creada correctamente en: {ruta}")

