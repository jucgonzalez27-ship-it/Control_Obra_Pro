"""Funciones pequeñas de presentación, independientes de Streamlit."""


def nombre_del_nivel(piso: int) -> str:
    if piso < 0:
        return "Subterráneo"
    return f"Piso {piso}"


def estado_corto(estado: str) -> str:
    if estado == "Observado no bloqueante":
        return "Observado"
    return estado


def clave_numero_departamento(numero: str):
    texto = str(numero)
    try:
        return 0, int(texto)
    except ValueError:
        return 1, texto.casefold()
