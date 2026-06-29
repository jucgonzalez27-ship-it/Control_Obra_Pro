# DEC-001 - Dependencias Críticas

Estado: CONGELADO

## Decisión

Solo se modelan dependencias críticas físicas.

Una dependencia crítica existe cuando una partida no puede ejecutarse físicamente sin otra previamente terminada.

## No Se Modela

- Buenas prácticas.
- Calidad.
- Secuencia ideal.
- Preferencias de ejecución.
- Excepciones normales de obra.

## Uso En La App

Las dependencias solo generan advertencias operativas.

Nunca bloquean cambios de estado.

Nunca modifican automáticamente el avance.

## Condiciones

- AND: todas las partidas deben estar terminadas.
- OR: una de las alternativas debe estar terminada.
