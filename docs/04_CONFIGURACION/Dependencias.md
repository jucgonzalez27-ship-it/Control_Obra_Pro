# Dependencias Críticas

Estado: DEFINIDO

## Regla General

Solo modelar dependencias críticas.

Una dependencia crítica existe cuando una partida anterior debe estar terminada para poder ejecutar físicamente la siguiente.

No considerar:

- Buenas prácticas.
- Calidad.
- Secuencia ideal.
- Preferencias de ejecución.
- Excepciones normales de obra.

## Uso

Las dependencias solo generan advertencias operativas.

Nunca bloquean cambios de estado.

No modifican automáticamente estados de avance.

## Tipos De Condición

AND:

- Todas las partidas del grupo deben estar terminadas.

OR:

- Debe cumplirse al menos una alternativa del grupo.

## Configuración

Cada partida puede tener cero o más dependencias críticas.

La lógica debe poder modificarse desde configuración sin alterar código fuente.

PENDIENTE DE DEFINICIÓN: estrategia final para administrar toda la matriz desde interfaz/base sin constantes iniciales en código.
