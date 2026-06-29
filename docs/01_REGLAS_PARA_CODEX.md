# Reglas Para Codex

Estado: CONGELADO

## Regla Principal

Implementar únicamente funcionalidades definidas.

Si existe duda funcional:

`PENDIENTE DE DEFINICIÓN.`

No inventar.

## Antes De Implementar

Codex debe verificar:

1. Existe definición funcional.
2. Pertenece a V1.
3. No modifica reglas existentes.

Si no existe definición funcional, no implementar.

Si no pertenece a V1, mover a backlog.

Si modifica reglas existentes, solicitar aprobación antes de continuar.

## No Modificar Sin Autorización

- Reglas funcionales.
- Estados.
- Flujos.
- Validaciones.
- Dependencias críticas.
- Pesos.
- Roles.
- Liberación.
- Alcance V1.

## Configuración

La información funcional debe quedar configurable:

- Checklists.
- Pesos.
- Especialidades.
- Dependencias.
- Tipologías.
- Recintos.

PENDIENTE DE DEFINICIÓN: estrategia final para migrar configuraciones actualmente cargadas desde código a configuración administrable en base de datos.

## Dependencias

Solo modelar dependencias críticas.

Una dependencia crítica existe cuando una partida no puede ejecutarse físicamente sin otra previamente terminada.

No modelar:

- Buenas prácticas.
- Preferencias del jefe de terreno.
- Métodos constructivos.
- Excepciones normales.

Nunca bloquear cambios de estado. Solo generar advertencias.
