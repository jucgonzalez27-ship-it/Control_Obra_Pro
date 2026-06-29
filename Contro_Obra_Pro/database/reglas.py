"""Reglas de negocio puras de la versión 0.1."""

TIPOS_BLOQUEANTES = {
    "Falta material",
    "Observación grave",
    "Retrabajo pendiente",
    "Instalación incompleta",
    "No funciona",
}

ESTADOS_ACTIVOS = {"Abierto", "En gestión", "Resuelto"}


def calcular_bloqueo(
    tipo_problema: str,
    requiere_retrabajo: bool = False,
    afecta_funcionalidad: bool = False,
) -> bool:
    """Indica si una restricción impide entregar el departamento."""
    return (
        tipo_problema in TIPOS_BLOQUEANTES
        or requiere_retrabajo
        or afecta_funcionalidad
    )


def calcular_semaforo(restricciones: list[dict]) -> str:
    """Calcula el estado del departamento a partir de sus restricciones."""
    activas = [
        restriccion
        for restriccion in restricciones
        if restriccion["estado"] in ESTADOS_ACTIVOS
    ]

    if any(restriccion["bloquea_entrega"] for restriccion in activas):
        return "Bloqueado"
    if activas:
        return "Observado no bloqueante"
    return "Liberable"

