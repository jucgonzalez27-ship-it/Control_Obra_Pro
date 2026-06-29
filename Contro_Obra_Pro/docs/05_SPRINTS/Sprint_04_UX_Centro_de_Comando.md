# Sprint 04 - UX Centro de Operaciones / Dashboard V1

Estado: CONGELADO

## Objetivo Del Sprint

Actualizar la experiencia operativa de Control Obra Pro para que cada pantalla ayude a tomar decisiones en obra.

Principio rector:

Control Obra Pro no muestra información para ser leída.

Muestra información para tomar decisiones.

Toda pantalla deberá respetar la siguiente jerarquía:

1. Decisión.
2. Acción.
3. Impacto.
4. Información.

Si una pantalla presenta primero datos y luego la acción, deberá rediseñarse.

---

# UX-01 Centro De Operaciones / Dashboard V1

Estado: CONGELADO

## Objetivo

Construir la pantalla inicial de Control Obra Pro.

Esta pantalla debe permitir que un administrador de obra entienda en menos de 10 segundos:

- Qué debe hacer hoy.
- Qué departamentos requieren atención.
- Qué restricciones están deteniendo la obra.
- Qué departamentos pueden seguir avanzando.
- Qué acciones tienen mayor impacto operativo.

El objetivo no es mostrar un dashboard decorativo.

El objetivo es responder:

¿Qué debo hacer ahora para liberar la mayor cantidad de departamentos durante la jornada de hoy?

## Filosofía

Control Obra Pro no es un sistema para registrar información.

Es un sistema para priorizar acciones operativas en obra.

El Centro de Operaciones debe ayudar a disminuir recorridos innecesarios y evitar que el administrador revise departamentos al azar.

## Regla Principal UX

Cada componente debe responder una sola pregunta:

- Acciones prioritarias: ¿Qué hago primero?
- Mapa de departamentos: ¿Dónde debo actuar?
- KPIs: ¿Cómo va la torre?
- Restricciones críticas: ¿Qué está deteniendo la obra?
- Compromisos próximos: ¿Qué no puedo olvidar hoy?

Si un componente no ayuda a tomar una decisión, no debe mostrarse.

## Layout General

La pantalla debe tener un diseño moderno tipo SaaS B2B, limpio y profesional.

Debe evitar apariencia de Excel, Power Apps o ERP antiguo.

## Estructura Visual

1. Sidebar izquierda.
2. Header superior con filtros.
3. Bloque de acciones prioritarias.
4. Mapa operativo de departamentos.
5. KPIs secundarios.
6. Restricciones críticas.
7. Compromisos próximos.

## Sidebar Izquierda

Debe contener navegación simple:

- Centro de Operaciones.
- Departamentos.
- Reglas Operativas y Restricciones.
- Partidas.
- Responsables.
- Reportes.
- Configuración.

La opción activa debe ser `Centro de Operaciones`.

## Header Superior

Debe ser limpio y compacto.

Debe contener:

- Selector de torre.
- Filtro por piso.
- Filtro por estado.
- Filtro por responsable.
- Buscador de departamento.

No agregar más filtros visibles en V1.

Filtros avanzados pueden quedar para futuro.

## Acciones Prioritarias

Este bloque aparece arriba del mapa.

Máximo 5 acciones.

El sistema debe mostrar acciones posibles de resolver hoy.

Cada tarjeta debe mostrar:

- Prioridad.
- Impacto.
- Causa.
- Acción recomendada.
- Responsable.
- Fecha/hora compromiso.

Regla:

No mostrar solo el problema.

Mostrar siempre problema + impacto + acción.

## Mapa Operativo De Departamentos

Este es el componente principal del Centro de Operaciones.

Debe ocupar el mayor espacio visual de la pantalla.

Debe representar la torre agrupada por piso.

Cada piso debe aparecer como una fila.

Cada departamento debe aparecer como una tarjeta compacta.

## Contenido De Cada Tarjeta En Mapa

Cada tarjeta debe mostrar solo:

- Número de departamento.
- Estado operativo mediante color.
- Avance oficial %.
- Cantidad de restricciones activas.

No mostrar dentro de la tarjeta:

- Responsable.
- Recinto.
- Observaciones.
- Comentarios.
- Especialidad.
- Fecha compromiso.

Esa información debe quedar para la ficha del departamento.

## Estados Visuales

Verde:

- Operativo / liberable.
- Significa que el departamento puede continuar su secuencia constructiva.
- Puede tener observaciones menores, pero no posee restricciones que detengan el avance.

Amarillo:

- Con riesgo / observado.
- Tiene observaciones o condiciones que requieren seguimiento, pero todavía puede seguir avanzando.

Rojo:

- Bloqueado.
- Tiene una restricción que impide continuar la secuencia constructiva.

Gris:

- Sin revisar o sin actualización.
- No existe información suficiente para tomar decisión.

Azul:

- Reservado para estados futuros.
- No usar en V1.

## Definición De Restricción

Una restricción no es cualquier partida pendiente.

Una restricción es una partida pendiente o condición que impide ejecutar otra partida posterior o continuar la secuencia constructiva normal.

Ejemplos:

- Falta mueble de cocina y eso impide instalar cubierta, lavaplatos o grifería: restricción.
- Falta espejo, pero no impide otras partidas: pendiente, no restricción.
- Raya menor en vidrio: observación, no restricción.
- Falta lavamanos y detiene instalación sanitaria o revisión del recinto: restricción.

## Restricción Inteligente

El sistema debe evitar falsos bloqueos.

Una partida pendiente solo bloquea cuando impide otra partida posterior.

Para esto, el sistema debe considerar dependencias entre partidas.

Debe existir una secuencia estándar por recinto/tipología, modificable por obra.

## KPIs Secundarios

Los KPIs no son el foco principal.

Deben ir en segundo nivel, después del mapa o en una franja lateral secundaria.

Mostrar solo 5 KPIs:

1. Departamentos liberables.
2. Departamentos bloqueados.
3. Departamentos con riesgo.
4. Avance oficial torre.
5. Restricciones críticas.

No agregar KPIs financieros, comerciales ni decorativos.

## Restricciones Críticas

Mostrar tabla pequeña ordenada por impacto.

Columnas:

- Impacto.
- Departamentos afectados.
- Problema.
- Responsable.
- Fecha compromiso.
- Acción.

## Compromisos Próximos

Mostrar solo compromisos del día.

No usar calendario completo.

Formato tipo timeline corto:

```text
09:00 - Llegada proveedor muebles
11:30 - Revisión Depto 804
15:00 - Ingreso pintura Piso 8
```

## Interacciones Permitidas Desde Centro De Operaciones

Desde esta pantalla solo deben existir estas acciones:

1. Entrar a ficha de departamento.
2. Registrar restricción.
3. Actualizar estado.
4. Ver responsable.

No agregar edición masiva ni formularios largos en V1.

Toda acción debe requerir el menor número posible de clics.

## Comportamiento Al Hacer Clic En Departamento

Un clic sobre la tarjeta abre la ficha del departamento.

La ficha debe mostrar:

- Estado operativo.
- Avance oficial.
- Avance declarado.
- Restricciones activas.
- Observaciones activas.
- Recintos.
- Partidas pendientes.
- Responsables.
- Fechas compromiso.
- Historial reciente.

El detalle pertenece a UX-03.

En UX-01 solo debe abrirse el acceso.

## Orden Visual Definitivo

1. Header superior.
2. Acciones prioritarias.
3. Mapa operativo de departamentos.
4. KPIs secundarios.
5. Restricciones críticas.
6. Compromisos próximos.

## Estilo Visual

Diseño moderno, sobrio y profesional.

Requisitos:

- Fondo claro.
- Sidebar oscura.
- Tarjetas blancas.
- Bordes suaves.
- Sombras sutiles.
- Tipografía sans serif moderna.
- Buena separación visual.
- Colores usados con moderación.
- Semáforo claro.
- Jerarquía visual fuerte.
- Look premium B2B.

Evitar:

- Gráficos circulares.
- Exceso de colores.
- Tablas tipo Excel.
- Formularios pesados.
- Dashboard financiero.
- Dashboard de marketing.
- Widgets decorativos.
- Pantallas saturadas.

---

# UX-02 Lista De Departamentos

Estado: DEFINIDO

## Objetivo

La lista de departamentos debe ayudar a decidir si vale la pena ingresar a un departamento ahora.

## Tarjeta De Departamento

Debe mostrar únicamente información útil para tomar una decisión inmediata.

Información visible:

- Número de departamento.
- Piso.
- Tipología.
- Estado operativo como chip de color.
- Porcentaje de avance general.
- Recintos completados / total.

Eliminar:

- Fecha de última actualización.

Agregar chips cuando correspondan:

- Próxima acción.
- Liberable.
- Bloqueado.
- Pendiente de Verificación.

La tarjeta debe responder:

¿Vale la pena ingresar a este departamento ahora?

---

# UX-03 Ficha Departamento

Estado: DEFINIDO

## Objetivo

La ficha debe permitir decidir qué hacer con el departamento antes de mostrar datos secundarios.

## Orden Oficial

La información deberá seguir el patrón oficial del producto:

1. Decisión.
2. Acción.
3. Impacto.
4. Información.

## Cabecera

La cabecera deberá mostrar:

- Departamento.
- Estado Operativo.
- Próxima Acción.
- Impacto esperado.

Luego recién mostrar:

- Avance General.
- Piso.
- Tipología.
- Última actualización.

Después mostrar los recintos.

No comenzar mostrando porcentajes.

---

# UX-04 Vista Recinto

Estado: DEFINIDO

## Objetivo

Mantener la estructura actual de actualización de partidas por recinto.

## Partidas

Para cada partida agregar:

- Especialidad responsable.
- Dependencia crítica cuando exista.

Ejemplo:

```text
Cubierta

Especialidad:
Muebles

Depende de:
Mueble Base
```

## Guardado

Mantener:

- Guardado automático.
- Sin botón Guardar.

---

# UX-05 Reglas Operativas Y Restricciones

Estado: DEFINIDO

## Nombre Del Módulo

No llamar `Restricciones`.

Nombre aprobado:

Reglas Operativas y Restricciones.

## Separación Obligatoria

Separar claramente:

- Restricciones operativas.
- Validaciones del sistema.
- Permisos.

---

# UX-06 Reportes

Estado: DEFINIDO

## Objetivo

Los reportes deben responder:

¿Qué acción debe ejecutar la obra?

No solo mostrar estadísticas.

## Eliminar

- Top 10 departamentos más avanzados.

## Agregar

- Departamentos Liberables.
- Departamentos Bloqueados.
- Restricciones por Especialidad.
- Partidas que más frenan la obra.
- Especialidades con mayor impacto operativo.

---

# UX-07 Flujo Diario

Estado: DEFINIDO

## Flujo Aprobado

```text
Centro de Comando
↓
Mapa Operativo
↓
Visor Operativo
↓
¿Necesita editar?
↓
NO
↓
Cerrar visor
↓
Seleccionar siguiente departamento

SI
↓
Abrir Ficha Departamento
↓
Seleccionar Recinto
↓
Actualizar Partidas
↓
Guardar Automáticamente
↓
Cerrar
↓
Volver al Centro de Comando
```

Nunca perder filtros ni contexto.
Nunca perder:

- Filtros.
- Posición.
- Contexto.

---

# Fuera De Alcance De Sprint 04

No definir ni implementar todavía:

- IA.
- COP.
- Chat.
- Predicciones.
- Módulos adicionales no definidos.

---

# Tareas De Implementación Posteriores

El Sprint 04 queda funcionalmente congelado.

Lo siguiente corresponde a implementación o diseño visual posterior, no a nuevas decisiones funcionales:

- Aplicar las decisiones UX en la interfaz.
- Ajustar responsive final si se implementa en una superficie móvil.
- Aplicar identidad corporativa definitiva cuando exista.
- Implementar el Visor Operativo respetando el flujo aprobado.
