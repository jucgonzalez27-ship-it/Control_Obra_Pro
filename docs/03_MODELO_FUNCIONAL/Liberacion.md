# Liberación

Estado: DEFINIDO

## Acción

Liberar departamento.

Solo Administrador.

## Validaciones Antes De Liberar

No permitir liberar si existe:

- Bloqueos activos.
- Observaciones bloqueantes.
- Partidas aplicables sin verificar.

## Estado Liberable

Un departamento pasa a estado Liberable únicamente cuando:

- Todas las partidas aplicables están verificadas.
- No existen bloqueos activos.
- No existen observaciones bloqueantes.

El estado Liberable representa que el departamento está listo para su liberación administrativa.

## Registro

Al liberar se debe registrar:

- Usuario.
- Fecha.
- Hora.
- Comentario.

## Pendiente

PENDIENTE DE DEFINICIÓN: confirmar si la liberación equivale a estado final o si existe un estado posterior llamado `Entregado`.
