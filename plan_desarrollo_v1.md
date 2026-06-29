# Control Obra Pro - Plan de desarrollo V1

Documento de trabajo generado a partir de la especificacion funcional consolidada V1 y del estado actual del codigo.

## Lectura ejecutiva

Control Obra Pro debe cerrar su V1 como una herramienta de control diario de terminaciones por departamento, recinto y partida. El foco no es calidad total, ERP, compras, bodega ni programacion avanzada. El foco operativo es responder rapido:

- Que esta listo.
- Que esta en proceso.
- Que falta.
- Que esta bloqueado.
- Que responsable o especialidad debe actuar.
- Que departamentos estan proximos a liberarse.

La base actual ya cubre una parte importante: obra, torre, departamentos, tipologias, checklists, avance declarado/oficial, estados de partida, restricciones, historial, dashboard y seguimiento. La V1 debe reforzar usabilidad en terreno, reportabilidad y control de roles.

## Estado actual detectado

Implementado:

- Dashboard principal con indicadores, matriz de departamentos, filtros y ficha lateral.
- Flujo de avance por departamento y recinto.
- Actualizacion masiva de partidas.
- Estados de partida: no iniciada, en proceso, terminada, observada, bloqueada, verificada y no aplica.
- Avance declarado y oficial con peso de partida.
- Materializacion de checklist por tipologia.
- Problemas madre asociados a varios departamentos.
- Restricciones por problema y bloqueos directos de partida.
- Historial de cambios de partidas.
- Seguimiento de restricciones.
- Roles base: Administrador y Supervisor.
- Carga V1 de Proyecto Montevista desde script.
- Tests unitarios para modelo, reglas, servicios, presentacion y configuracion V1.

Pendiente o incompleto:

- Login o seleccion de usuario global.
- Rol Responsable / Contratista.
- Rol Solo lectura.
- Reportes exportables.
- Vista de pendientes por responsable/especialidad.
- Especialidad asociada a partidas/responsables.
- Umbral de partidas sin movimiento.
- Flujo formal de liberacion/verificacion de departamento.
- Configuracion Montevista V1 desde la interfaz.
- Unificacion visual de problemas, restricciones y bloqueos de partida.
- Limpieza de scripts antiguos que apuntan a `obra.db`.

## Brechas criticas para usar en obra

### 1. Confirmar configuracion Montevista

Necesario:

- Relacion final departamento-tipologia.
- Checklist definitivo de Dormitorio.
- Checklist definitivo de Banos.
- Checklist definitivo de Walk-in Closet.
- Checklist definitivo de Terraza.
- Pesos 1/2 por partida.
- Partidas obligatorias y no obligatorias.
- Responsables reales y especialidades.

Criterio de aceptacion:

- La app permite cargar o revisar la configuracion Montevista desde Streamlit.
- Se visualiza cuantos departamentos quedaron asignados.
- Se informan departamentos no encontrados o sin tipologia.
- El administrador puede revisar tipologias, recintos y checklists antes de operar.

### 2. Optimizar levantamiento en terreno

Necesario:

- Mostrar primero partidas pendientes del recinto.
- Reducir pasos para actualizar varias partidas.
- Mantener usuario activo durante la sesion.
- Validar comentario obligatorio para observada/bloqueada segun regla.

Criterio de aceptacion:

- Un supervisor puede seleccionar departamento, recinto, varias partidas y aplicar estado en menos de 30 segundos.
- Supervisor no puede verificar ni marcar no aplica.
- Administrador puede verificar y marcar no aplica.

### 3. Reportes Excel V1

Necesario:

- Pendientes por departamento.
- Pendientes por responsable.
- Bloqueos vencidos.
- Avance por piso.
- Avance por tipologia.
- Departamentos liberables.
- Historial de cambios.

Criterio de aceptacion:

- Existe una pantalla Reportes.
- El administrador puede descargar un archivo Excel o CSV con datos operativos.
- Los reportes incluyen responsable, fechas, estado, comentario y dias vencido/sin movimiento cuando aplique.

### 4. Responsables y especialidades

Necesario:

- Agregar especialidad a responsables o crear catalogo de especialidades.
- Asociar partidas a especialidad responsable.
- Filtrar dashboard y reportes por especialidad.

Criterio de aceptacion:

- El usuario puede responder quien debe actuar.
- Existen pendientes agrupados por responsable y especialidad.

### 5. Bitacora operativa

Necesario:

- Vista consolidada de actividad reciente.
- Cambios de estado, verificaciones, bloqueos y cierres.
- Filtro por fecha, usuario, departamento y tipo de movimiento.

Criterio de aceptacion:

- El Centro de Comando muestra que cambio desde la ultima revision.
- La ficha de departamento muestra historial reciente suficiente para tomar decision.

## Orden recomendado de implementacion

### Paso 1 - Configuracion V1 desde la app

Alcance:

- Agregar en Configuracion una seccion "Carga Montevista V1".
- Ejecutar `cargar_configuracion_v1(crear_respaldo=True)`.
- Mostrar resumen de tipologias, recintos, partidas, checklists, departamentos asignados y no encontrados.

Archivos probables:

- `app.py`
- `database/cargar_configuracion_v1.py`
- tests nuevos o ampliados en `tests/test_configuracion_v1.py`

### Paso 2 - Reportes base sin Excel complejo

Alcance:

- Crear pagina "Reportes".
- Mostrar tablas descargables CSV con `st.download_button`.
- Partir por pendientes por departamento, pendientes por responsable, bloqueos vencidos e historial.

Archivos probables:

- `app.py`
- `database/servicios.py`
- tests en `tests/test_servicios.py`

### Paso 3 - Especialidades

Alcance:

- Agregar campo `especialidad` a responsables o catalogo simple.
- Mostrar especialidad en responsables.
- Usarla en filtros y reportes.

Archivos probables:

- `database/modelo_v01.py`
- `database/servicios.py`
- `app.py`
- tests de migracion y servicios.

### Paso 4 - Usuario activo y permisos UI

Alcance:

- Selector global de usuario en sidebar.
- Reutilizar ese usuario en avance, problemas y seguimiento.
- Ocultar acciones no permitidas segun rol.
- Mantener validaciones de backend como fuente de verdad.

Archivos probables:

- `app.py`
- `database/servicios.py` si se incorporan nuevos roles.

### Paso 5 - Centro de Comando refinado

Alcance:

- Agregar metricas faltantes: en proceso y liberables.
- Agregar filtro por tipologia y especialidad.
- Mostrar pendientes y bloqueos vencidos destacados.
- Mostrar actividad reciente.

Archivos probables:

- `app.py`
- `database/servicios.py`

### Paso 6 - Flujo formal de liberacion

Alcance:

- Definir estado formal de departamento liberado/verificado.
- Registrar usuario, fecha y comentario.
- Impedir liberacion si hay obligatorias no verificadas, bloqueos activos u observaciones bloqueantes.

Archivos probables:

- `database/modelo_v01.py`
- `database/servicios.py`
- `app.py`
- tests nuevos.

## Decisiones que debe confirmar el usuario antes de codificar ciertas partes

Criticas:

- Checklist final de Dormitorio.
- Checklist final de Banos.
- Checklist final de Walk-in Closet.
- Checklist final de Terraza.
- Matriz de pesos 1/2.
- Matriz de partidas no obligatorias.
- Umbral de dias sin movimiento.
- Responsables reales y especialidades.

Puede avanzar con supuesto temporal:

- Rol Responsable/Contratista puede quedar para V1.1.
- Login real con password puede quedar para V1.1.
- Fotos pueden quedar para V1.1.
- Entrega formal puede quedar como accion manual de administrador si no se define ahora.

## Primer cambio recomendado

Implementar "Carga Montevista V1" dentro de Configuracion.

Motivo:

- Reduce dependencia de scripts manuales.
- Permite repetir la configuracion con respaldo.
- Ayuda a validar que la base activa esta lista para operar.
- Es una mejora pequena, acotada y de alto valor antes de reportes y permisos.

