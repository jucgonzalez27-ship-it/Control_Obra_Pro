# DEC-005 - Obligatoriedad, Verificación Y Liberación

Estado: CONGELADO

## Principio

El supervisor no certifica el avance oficial del departamento.

El supervisor únicamente declara el avance observado en terreno.

## Avance Declarado

Es registrado por supervisores y responsables de especialidad.

Su objetivo es:

- Informar el progreso diario.
- Indicar dónde hubo avance.
- Facilitar la planificación de la revisión.
- Evitar que el administrador deba recorrer todos los departamentos.

El avance declarado no libera departamentos.

No modifica el avance oficial.

## Avance Oficial

Solo puede ser registrado por el Administrador.

Representa la verificación física del trabajo ejecutado.

Cada partida verificada aumenta el avance oficial.

## Obligatoriedad

Todas las partidas que formen parte del checklist de un recinto son obligatorias.

No existe el concepto de partida opcional.

La única excepción es el estado `No aplica`, definido por la configuración de la tipología o del recinto.

## Reglas

- Partida aplicable: obligatoria.
- Partida `No aplica`: se excluye del cálculo de avance y de la liberación.
- Un recinto no puede considerarse terminado si tiene partidas aplicables pendientes.

## Configuración

La obligatoriedad no debe configurarse por partida.

Debe derivarse automáticamente de la aplicabilidad.

## Estado Liberable

Un departamento pasa a estado Liberable únicamente cuando:

- Todas las partidas aplicables están verificadas.
- No existen bloqueos activos.
- No existen observaciones bloqueantes.

El estado Liberable representa que el departamento está listo para su liberación administrativa.

## Objetivo Del Sistema

El sistema no busca reemplazar la revisión del administrador.

Busca indicarle con precisión qué departamentos debe revisar primero para optimizar su tiempo y reducir recorridos innecesarios por la obra.
