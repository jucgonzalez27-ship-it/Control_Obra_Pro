# Definición operativa de Control Obra Pro

# Definición operativa de Control Obra Pro

Documento consolidado con las decisiones funcionales confirmadas para la
aplicación. Será la referencia principal para continuar el desarrollo sin
inventar reglas.

Fecha de consolidación: 25 de junio de 2026.

## Estado del documento

- Los puntos 1 al 10 quedan pendientes de definición.
- Las decisiones desde el punto 11 fueron respondidas y confirmadas.
- El alcance de V1 mínima operativa queda cerrado en el punto 26.
- Si una decisión futura contradice este documento, deberá actualizarse aquí
  antes de modificar la implementación.

---

## 1. Datos generales

**Pendiente.**

- Nombre de la obra:
- Torre o bloque piloto:
- Cantidad de pisos:
- Objetivo principal de la aplicación:
- Quién administrará la información:
- Quién revisará el dashboard:

---

## 2. Usuarios de la aplicación

**Pendiente.**

| Nombre | Rol                        | Etapa o especialidad |
| ------ | -------------------------- | -------------------- |
|        | Administrador / Supervisor |                      |

Pendiente definir:

- Quién puede actualizar partidas.
- Quién puede declarar una partida terminada.
- Usuarios y roles definitivos.

---

## 3. Responsables operativos

**Pendiente.**

| Nombre | Empresa | Cargo o especialidad |
| ------ | ------- | -------------------- |
|        |         |                      |

---

## 4. Departamentos

**Pendiente de confirmación final.**

Distribución actualmente cargada:

| Nivel        | Departamentos              |
| ------------ | -------------------------- |
| Subterráneo | 03, 04, 05, 06, 07         |
| Piso 1       | 13, 14, 15, 16, 17, 18     |
| Piso 2       | 23, 24, 25, 26, 27, 28, 29 |
| Piso 3       | 33, 34, 35, 36, 37, 38, 39 |
| Piso 4       | 43, 44, 45, 46, 47, 48, 49 |
| Piso 5       | 53, 54, 55, 56, 57, 58, 59 |

---

## 5. Tipologías

Definidas para la V1 de Control Obra Pro en Proyecto Montevista.

### Tipología C1

Departamentos:

Recintos:

1. Living - Comedor.
2. Cocina.
3. Dormitorio Principal.
4. Dormitorio 1.
5. Dormitorio 2.
6. Baño 1.
7. Baño 2.
8. Terraza Principal.
9. Terraza Suite.

### Tipología C2

Departamentos:

Recintos:

1. Living - Comedor.
2. Cocina.
3. Dormitorio Principal.
4. Dormitorio 1.
5. Baño 1.
6. Baño 2.
7. Walk-in Closet.
8. Terraza Principal.
9. Terraza Suite.

### Tipología D

Departamentos:

Recintos:

1. Living - Comedor.
2. Cocina.
3. Dormitorio Principal.
4. Dormitorio 1.
5. Baño 1.
6. Baño 2.
7. Walk-in Closet.
8. Terraza Principal.
9. Terraza Suite.

### Tipología E

Departamentos:

Recintos:

1. Living - Comedor.
2. Cocina.
3. Dormitorio Principal.
4. Dormitorio 1.
5. Baño 1.
6. Baño 2.
7. Walk-in Closet.
8. Terraza Principal.
9. Terraza Suite.

### Tipología F

Departamentos:

Recintos:

1. Living.
2. Cocina.
3. Dormitorio Principal.
4. Dormitorio 1.
5. Baño 1.
6. Baño 2.

---

## 6. Checklist por recinto

Los checklists se construirán por recinto, no por tipología. Las tipologías
solo definen qué recintos contiene cada departamento.

Las partidas representan hitos de avance, no observaciones de calidad. Sus
nombres deben ser genéricos y reutilizables para otros proyectos.

Las partidas deberán almacenarse en la base de datos para que puedan
agregarse, eliminarse o reordenarse sin modificar el código.

Los dormitorios utilizarán un mismo checklist maestro. Las terrazas Principal
y Suite utilizarán un mismo checklist maestro llamado Terraza.

Los baños utilizarán checklists diferenciados por artefacto principal:

- Baño Principal: receptáculo y mampara.
- Baño 1: tina.

### Living - Comedor

1. Tabique.
2. Empaste.
3. Aparejo.
4. Primera mano de pintura.
5. Mano final de pintura.
6. Piso flotante.
7. Guardapolvo.
8. Cornisa.
9. Junquillo.
10. Puerta.
11. Cerradura.
12. Componentes eléctricos.
13. Radiador.

### Cocina

1. Tabique.
2. Cerámica muro.
3. Cerámica piso.
4. Empaste.
5. Aparejo.
6. Primera mano de pintura.
7. Mano final de pintura.
8. Mueble base.
9. Mueble aéreo.
10. Estante, si aplica.
11. Cubierta.
12. Guardapolvo cerámico.
13. Cornisa.
14. Junquillo.
15. Puerta.
16. Cerradura.
17. Lavaplatos.
18. Grifería.
19. Encimera.
20. Horno.
21. Campana.
22. Componentes eléctricos.
23. Radiador.
24. Caldera.

### Dormitorio

Aplica para Dormitorio Principal, Dormitorio 1 y Dormitorio 2.

1. Tabique.
2. Empaste.
3. Aparejo.
4. Primera mano de pintura.
5. Mano final de pintura.
6. Piso flotante.
7. Guardapolvo.
8. Cornisa.
9. Junquillo.
10. Puerta.
11. Cerradura.
12. Closet.
13. Componentes eléctricos.
14. Radiador.

### Walk-in Closet

1. Tabique.
2. Empaste.
3. Aparejo.
4. Primera mano de pintura.
5. Mano final de pintura.
6. Piso flotante.
7. Guardapolvo.
8. Cornisa.
9. Junquillo.
10. Closet.
11. Componentes eléctricos.

### Baño Principal

Baño con receptáculo y mampara.

1. Tabique.
2. Cerámica muro.
3. Cerámica piso.
4. Empaste.
5. Aparejo.
6. Primera mano de pintura.
7. Mano final de pintura.
8. Guardapolvo cerámico.
9. Cornisa.
10. Puerta.
11. Cerradura.
12. Vanitorio.
13. Espejo.
14. Grifería.
15. Receptáculo.
16. Mampara.
17. WC.
18. Accesorios.
19. Componentes eléctricos.

### Baño 1

Baño con tina.

1. Tabique.
2. Cerámica muro.
3. Cerámica piso.
4. Empaste.
5. Aparejo.
6. Primera mano de pintura.
7. Mano final de pintura.
8. Guardapolvo cerámico.
9. Cornisa.
10. Puerta.
11. Cerradura.
12. Vanitorio.
13. Espejo.
14. Grifería.
15. Tina.
16. WC.
17. Accesorios.
18. Componentes eléctricos.

### Terraza

Aplica para Terraza Principal y Terraza Suite.

1. Textura.
2. Piso cerámico.
3. Guardapolvo cerámico.
4. Cielo.
5. Baranda vidriada.
6. Componentes eléctricos.

---

## 7. Catálogo definitivo de partidas

Catálogo provisional disponible en la aplicación:

- Tabiquería.
- Yeso / enlucido.
- Preparación base.
- Pavimento.
- Porcelanato muro.
- Porcelanato piso.
- Fragüe.
- Pintura.
- Muro.
- Cielo.
- Cornisa.
- Ventanas.
- Puerta.
- Muebles.
- Vanitorio.
- Grifería.
- Artefactos.
- Instalaciones.
- Equipamiento.
- Limpieza final.

El catálogo maestro V1 queda compuesto por 7 checklists reutilizables:

1. Living - Comedor.
2. Cocina.
3. Dormitorio.
4. Walk-in Closet.
5. Baño Principal.
6. Baño 1.
7. Terraza.

---

## 8. Etapas de construcción

**Pendiente.**

Orden provisional:

1. Obra gruesa.
2. Tabiquería.
3. Yeso y enlucidos.
4. Pavimentos.
5. Pintura.
6. Muebles y artefactos.
7. Terminación fina.
8. Preentrega.
9. Entregado.

Falta relacionar cada partida con su etapa y supervisor encargado.

---

## 9. Estados de partida

**Pendiente de revisar como catálogo completo.**

Estados provisionales:

- No iniciada.
- En proceso.
- Terminada.
- Bloqueada.
- Verificada.
- No aplica.

---

## 10. Configuración inicial y datos de origen

**Pendiente.**

Incluye cualquier dato de configuración no resuelto en los puntos anteriores.

---

## 11. Reglas de verificación y avance

### Partidas terminadas

Una partida marcada como **Terminada** no cuenta como avance completo.

Solo una partida **Verificada** cuenta como avance completado para el cálculo
del porcentaje.

### Estado No aplica

- Solo un administrador puede marcar una partida como **No aplica**.
- Debe ser una excepción poco frecuente.

### Retroceso de estados

Se permite retroceder una partida desde **Terminada** o **Verificada** a
**En proceso** cuando se detecta un trabajo incorrecto.

El retroceso exige:

- Razón obligatoria.
- Usuario que realizó el cambio.
- Fecha y hora.
- Estado anterior.
- Estado nuevo.
- Registro permanente en el historial.

---

## 12. Ponderación del avance

El avance será ponderado mediante dos categorías generales por partida:

| Categoría | Peso |
| ---------- | ---: |
| Principal  |    2 |
| Secundaria |    1 |

La ponderación representa principalmente el tiempo o volumen de trabajo.
No determina si una partida es prescindible para entregar.

Cada partida tendrá dos atributos independientes:

1. **Peso de avance:** principal o secundaria.
2. **Obligatoria para liberar:** sí o no.

Ejemplo:

| Partida             | Peso | Obligatoria para liberar |
| ------------------- | ---: | ------------------------ |
| Pintura             |    2 | Sí                      |
| Ventanas            |    2 | Sí                      |
| Vanitorio           |    1 | Sí                      |
| Espejo              |    1 | No                       |
| Accesorios de baño |    1 | No                       |
| Limpieza final      |    1 | Sí                      |

Fórmula conceptual:

```text
avance =
  suma de pesos de partidas verificadas
  /
  suma de pesos de partidas aplicables
```

Las partidas terminadas pendientes de verificación no aportan avance completo.

---

## 13. Estado operativo del departamento

El estado debe ser calculado por la aplicación y no ingresado manualmente.

### Sin revisar

El departamento todavía no tiene levantamiento.

### En proceso

Tiene partidas pendientes o en ejecución, pero no presenta un bloqueo formal.

### Bloqueado

Tiene al menos una partida bloqueada con una restricción activa.

### Observado

El departamento queda amarillo si ocurre al menos una de estas situaciones:

1. Tiene partidas secundarias pendientes, pero puede avanzar o entregarse.
2. Tiene detalles estéticos menores.
3. Tiene partidas terminadas pendientes de verificación, sin bloqueos.
4. Tiene una restricción de criticidad baja que no impide avanzar.
5. Está completamente ejecutado, pero mantiene observaciones menores abiertas.

### Liberable

Para ser liberable:

- Todas las partidas obligatorias para liberar deben estar verificadas.
- Puede conservar partidas no obligatorias pendientes.

Si quedan partidas no obligatorias pendientes, el estado visible será:

**Liberable con pendientes**, representado en verde y mostrando la cantidad de
pendientes.

### Verificado

El departamento pasa automáticamente a **Verificado** cuando todas sus partidas
aplicables están verificadas.

No necesita una acción manual adicional sobre el departamento completo.

---

## 14. Criticidad de restricciones

La criticidad se calcula automáticamente para mantener criterios consistentes.

Reglas iniciales:

- **Crítica:** partida obligatoria vencida o muy próxima al hito.
- **Alta:** partida obligatoria bloqueada dentro de plazo.
- **Media:** partida no obligatoria bloqueada que afecta el avance.
- **Baja:** detalle menor sin impacto relevante en avance o entrega.

El administrador puede modificar la criticidad de forma excepcional, con una
justificación obligatoria que quede registrada.

### Alertas por antigüedad

Como las restricciones no tendrán fecha compromiso manual, las alertas se
basarán en días abiertas:

| Criticidad | Alerta desde |
| ---------- | -----------: |
| Crítica   |       1 día |
| Alta       |      3 días |
| Media      |      7 días |
| Baja       |     14 días |

---

## 15. Restricciones al avance

Al marcar una partida como **Bloqueada**, debe registrarse:

- Causa.
- Responsable.
- Comentario opcional.
- Fotografía opcional.
- Fecha y hora automática de creación.
- Usuario que creó el bloqueo.

No se solicitará una fecha compromiso manual.

El sistema registrará automáticamente:

- Fecha de creación.
- Cambios de estado.
- Fecha de término.
- Fecha de verificación.
- Retrocesos.
- Usuario responsable de cada movimiento.

---

## 16. Problemas comunes

La aplicación utilizará un sistema mixto:

- Permitirá crear problemas comunes manualmente.
- Sugerirá agrupaciones por coincidencia de partida, causa y responsable.
- El administrador decidirá si acepta, modifica o ignora la sugerencia.

Reglas:

- Una restricción solo puede pertenecer a un problema común.
- El problema común tendrá fecha general.
- Cada restricción conservará sus fechas individuales de movimientos.
- El problema común se cerrará automáticamente cuando todas sus restricciones
  estén cerradas.

La definición de fecha general deberá revisarse, porque posteriormente se
decidió eliminar la fecha compromiso manual de las restricciones. Puede
interpretarse como fecha objetivo informativa del problema común.

---

## 17. Flujo de carga rápida en terreno

Flujo principal:

```text
avance =
  suma de pesos de partidas verificadas
  /
  suma de pesos de partidas aplicables
```

La interfaz será una tabla compacta con:

| Partida | Estado      | Acción |
| ------- | ----------- | ------- |
| Pintura | En proceso  | Cambiar |
| Ventana | Verificada  | Cambiar |
| Cornisa | No iniciada | Cambiar |

Debe permitir:

- Seleccionar varias partidas del recinto.
- Aplicar el mismo estado en una sola acción.
- Abrir los datos de restricción cuando el estado sea Bloqueada.
- Adaptarse a computador, tablet y teléfono.

---

## 18. Estado inicial de la torre

El levantamiento inicial se realizará dentro de la misma aplicación:

- Piso por piso.
- Departamento por departamento.
- Recinto por recinto.

No se importará inicialmente una planilla externa.

---

## 19. Datos históricos

El problema antiguo registrado en la base:

1. Se revisará manualmente.
2. Si sigue vigente, se convertirá al nuevo modelo.
3. No se eliminará automáticamente.

---

## 20. Dashboard principal

El mapa visual de departamentos será el componente más importante al abrir la
aplicación.

Cada departamento mostrará:

- Número.
- Porcentaje de avance.
- Color del estado.
- Cantidad de bloqueos.

Al seleccionar un departamento se mostrarán:

1. Restricciones críticas.
2. Resumen de avance por recinto.
3. Checklist y acciones de actualización.
4. Historial.

La etapa actual se calculará automáticamente según las partidas verificadas.
El administrador podrá corregirla excepcionalmente con justificación.

---

## 21. Uso y despliegue

- Uso mixto: computador, tablet y teléfono.
- Funcionamiento con conexión a internet.
- Menos de 10 usuarios simultáneos en el piloto.
- SQLite puede utilizarse durante el piloto local.
- Para despliegue web multiusuario se recomienda PostgreSQL.
- Se requiere inicio de sesión con usuario y contraseña.
- Los permisos dependerán del rol.

---

## 22. Exportaciones, fotografías e historial

### Exportaciones

- Excel para análisis.
- PDF para informes.

### Fotografías

Se permitirán fotografías opcionales:

- Al registrar un bloqueo.
- Durante la verificación.

### Historial

Se conservará el mayor historial posible para evaluar el funcionamiento de la
obra:

- Cambios de estado.
- Usuarios.
- Fechas y horas.
- Retrocesos.
- Restricciones.
- Responsables.
- Causas.
- Verificaciones.
- Cambios de criticidad.
- Agrupaciones en problemas comunes.

El historial será permanente y no se sobrescribirá.

---

## 23. Notificaciones

### MVP

Alertas dentro de la aplicación:

- Restricciones envejecidas.
- Bloqueos críticos.
- Casos que superen el límite de días según criticidad.

### Etapa posterior

- Resumen diario por correo electrónico.

No se implementarán inicialmente WhatsApp ni notificaciones push.

---

## 24. Caso operativo de referencia

1. El usuario abre un departamento.
2. Selecciona un recinto.
3. Revisa sus partidas.
4. Marca una partida como Bloqueada.
5. Registra causa, responsable, comentario opcional y fotografía opcional.
6. La aplicación registra automáticamente fecha, hora y usuario.
7. El departamento queda rojo y recalcula su avance.
8. Al resolverse el trabajo, el supervisor marca la partida Terminada.
9. La partida sigue pendiente de verificación y no cuenta como avance completo.
10. El administrador revisa y marca la partida Verificada.
11. La aplicación cierra la restricción y conserva todo el historial.
12. Se recalculan avance, etapa y estado operativo del departamento.

---

## 25. Próximas decisiones pendientes

Antes de completar el producto deben resolverse, al menos:

1. Datos generales de la obra.
2. Usuarios y roles definitivos.
3. Responsables operativos.
4. Confirmación de departamentos.
5. Cargar tipologías y asignación por departamento en la base.
6. Cargar recintos de cada tipología en la base.
7. Revisar y validar en terreno el checklist maestro V1.
8. Cerrar el catálogo definitivo de partidas si aparece alguna excepción.
9. Relación entre partidas y etapas.
10. Clasificación de cada partida:

- Principal o secundaria.
- Obligatoria o no obligatoria para liberar.

---

## 26. Alcance V1 mínima operativa

### Objetivo V1

Dejar Control Obra Pro usable en piloto real para controlar avance por
departamento, recinto y partida, con trazabilidad básica, roles simples y
dashboard operativo.

### Prioridades V1

#### 1. Pantalla Avance por departamento

- Filtrar por departamento.
- Filtrar por recinto.
- Mostrar checklist compacto.
- Permitir seleccionar varias partidas.
- Aplicar estado masivo.
- Agregar comentario único para la actualización.
- Diseñarla para uso rápido en terreno.

#### 2. Historial de cambios de partidas

- Registrar cada cambio de estado.
- Guardar:
  - Estado anterior.
  - Estado nuevo.
  - Usuario.
  - Fecha y hora.
  - Comentario.
  - Departamento.
  - Recinto.
  - Partida.
- No sobrescribir información sin trazabilidad.

#### 3. Regla de avance V1

- Solo las partidas Verificadas cuentan como avance completo oficial.
- Las partidas Terminadas pueden mostrarse como avance declarado, pero no como
  avance oficial.
- No aplica no debe contar como pendiente.
- Bloqueada y Observada no cuentan como avance.

#### 4. Roles y permisos básicos

Supervisor:

- Puede marcar No iniciada, En proceso, Terminada, Observada y Bloqueada.
- Puede agregar comentarios.
- No puede Verificar.

Administrador:

- Puede realizar todas las acciones.
- Puede Verificar.
- Puede retroceder estados.
- Puede modificar configuración.

#### 5. Pesos y obligatoriedad

- Cada partida debe tener:
  - Peso 2: partida principal.
  - Peso 1: partida secundaria.
  - Obligatoria para liberar: Sí/No.
- El avance debe poder calcularse ponderado.
- El estado Liberable debe depender de partidas obligatorias.

#### 6. Dashboard principal V1

- Mostrar avance por departamento.
- Mostrar avance por piso.
- Mostrar cantidad de bloqueos.
- Mostrar cantidad de observaciones.
- Mostrar departamentos liberables.
- Al seleccionar un departamento, mostrar ficha resumen:
  - Porcentaje de avance.
  - Estado operativo.
  - Restricciones activas.
  - Checklist.
  - Historial reciente.

#### 7. Validación de datos en terreno

- Revisar si los checklists reales coinciden con la obra.
- Ajustar partidas que sobren.
- Agregar partidas faltantes.
- Corregir excepciones por tipología.
- Validar que el uso en terreno sea rápido.

#### 8. Exportación Excel

- Exportar avance por departamento.
- Exportar partidas pendientes.
- Exportar bloqueos/restricciones.
- Exportar resumen por piso.
- PDF queda fuera de V1 mínima, salvo que exista tiempo disponible.

#### 9. Fotos

- Quedan como opcional para V1.
- Prioridad secundaria.
- Idealmente asociarlas a Bloqueada, Observada o Verificada.

### Orden de implementación recomendado

1. Mejorar pantalla de avance por departamento/recinto.
2. Crear historial de cambios de partidas.
3. Corregir cálculo de avance oficial.
4. Implementar permisos básicos Administrador/Supervisor.
5. Agregar dashboard con avance, bloqueos y ficha por departamento.
6. Exportación Excel.
7. Fotos si queda tiempo.

### Criterio de cierre V1

La V1 se considera lista cuando se pueda:

- Seleccionar un departamento.
- Seleccionar un recinto.
- Actualizar varias partidas.
- Registrar historial.
- Ver avance oficial según partidas verificadas.
- Ver bloqueos y observaciones.
- Revisar dashboard por departamento/piso.
- Exportar avance a Exce

Documento consolidado con las decisiones funcionales confirmadas para la
aplicación. Será la referencia principal para continuar el desarrollo sin
inventar reglas.

Fecha de consolidación: 25 de junio de 2026.

## Estado del documento

- Los puntos 1 al 10 quedan pendientes de definición.
- Las decisiones desde el punto 11 fueron respondidas y confirmadas.
- El alcance de V1 mínima operativa queda cerrado en el punto 26.
- Si una decisión futura contradice este documento, deberá actualizarse aquí
  antes de modificar la implementación.

---

## 1. Datos generales

**Pendiente.**

- Nombre de la obra:
- Torre o bloque piloto:
- Cantidad de pisos:
- Objetivo principal de la aplicación:
- Quién administrará la información:
- Quién revisará el dashboard:

---

## 2. Usuarios de la aplicación

**Pendiente.**

| Nombre | Rol                        | Etapa o especialidad |
| ------ | -------------------------- | -------------------- |
|        | Administrador / Supervisor |                      |

Pendiente definir:

- Quién puede actualizar partidas.
- Quién puede declarar una partida terminada.
- Usuarios y roles definitivos.

---

## 3. Responsables operativos

**Pendiente.**

| Nombre | Empresa | Cargo o especialidad |
| ------ | ------- | -------------------- |
|        |         |                      |

---

## 4. Departamentos

**Pendiente de confirmación final.**

Distribución actualmente cargada:

| Nivel        | Departamentos              |
| ------------ | -------------------------- |
| Subterráneo | 03, 04, 05, 06, 07         |
| Piso 1       | 13, 14, 15, 16, 17, 18     |
| Piso 2       | 23, 24, 25, 26, 27, 28, 29 |
| Piso 3       | 33, 34, 35, 36, 37, 38, 39 |
| Piso 4       | 43, 44, 45, 46, 47, 48, 49 |
| Piso 5       | 53, 54, 55, 56, 57, 58, 59 |

---

## 5. Tipologías

Definidas para la V1 de Control Obra Pro en Proyecto Montevista.

### Tipología C1

Departamentos:

- 
- 
- 
- 
- 

Recintos:

1. Living - Comedor.
2. Cocina.
3. Dormitorio Principal.
4. Dormitorio 1.
5. Dormitorio 2.
6. Baño 1.
7. Baño 2.
8. Terraza Principal.
9. Terraza Suite.

### Tipología C2

Departamentos:

- 
- 
- 
- 
- 
- 

Recintos:

1. Living - Comedor.
2. Cocina.
3. Dormitorio Principal.
4. Dormitorio 1.
5. Baño 1.
6. Baño 2.
7. Walk-in Closet.
8. Terraza Principal.
9. Terraza Suite.

### Tipología D

Departamentos:

- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 

Recintos:

1. Living - Comedor.
2. Cocina.
3. Dormitorio Principal.
4. Dormitorio 1.
5. Baño 1.
6. Baño 2.
7. Walk-in Closet.
8. Terraza Principal.
9. Terraza Suite.

### Tipología E

Departamentos:

- 
- 
- 
- 
- 
- 
- 
- 
- 
- 
- 

Recintos:

1. Living - Comedor.
2. Cocina.
3. Dormitorio Principal.
4. Dormitorio 1.
5. Baño 1.
6. Baño 2.
7. Walk-in Closet.
8. Terraza Principal.
9. Terraza Suite.

### Tipología F

Departamentos:

- 

Recintos:

1. Living.
2. Cocina.
3. Dormitorio Principal.
4. Dormitorio 1.
5. Baño 1.
6. Baño 2.

---

## 6. Checklist por recinto

Los checklists se construirán por recinto, no por tipología. Las tipologías
solo definen qué recintos contiene cada departamento.

Las partidas representan hitos de avance, no observaciones de calidad. Sus
nombres deben ser genéricos y reutilizables para otros proyectos.

Las partidas deberán almacenarse en la base de datos para que puedan
agregarse, eliminarse o reordenarse sin modificar el código.

Los dormitorios utilizarán un mismo checklist maestro. Las terrazas Principal
y Suite utilizarán un mismo checklist maestro llamado Terraza.

Los baños utilizarán checklists diferenciados por artefacto principal:

- Baño Principal: receptáculo y mampara.
- Baño 1: tina.

### Living - Comedor

1. Tabique.
2. Empaste.
3. Aparejo.
4. Primera mano de pintura.
5. Mano final de pintura.
6. Piso flotante.
7. Guardapolvo.
8. Cornisa.
9. Junquillo.
10. Puerta.
11. Cerradura.
12. Componentes eléctricos.
13. Radiador.

### Cocina

1. Tabique.
2. Cerámica muro.
3. Cerámica piso.
4. Empaste.
5. Aparejo.
6. Primera mano de pintura.
7. Mano final de pintura.
8. Mueble base.
9. Mueble aéreo.
10. Estante, si aplica.
11. Cubierta.
12. Guardapolvo cerámico.
13. Cornisa.
14. Junquillo.
15. Puerta.
16. Cerradura.
17. Lavaplatos.
18. Grifería.
19. Encimera.
20. Horno.
21. Campana.
22. Componentes eléctricos.
23. Radiador.
24. Caldera.

### Dormitorio

Aplica para Dormitorio Principal, Dormitorio 1 y Dormitorio 2.

1. Tabique.
2. Empaste.
3. Aparejo.
4. Primera mano de pintura.
5. Mano final de pintura.
6. Piso flotante.
7. Guardapolvo.
8. Cornisa.
9. Junquillo.
10. Puerta.
11. Cerradura.
12. Closet.
13. Componentes eléctricos.
14. Radiador.

### Walk-in Closet

1. Tabique.
2. Empaste.
3. Aparejo.
4. Primera mano de pintura.
5. Mano final de pintura.
6. Piso flotante.
7. Guardapolvo.
8. Cornisa.
9. Junquillo.
10. Closet.
11. Componentes eléctricos.

### Baño Principal

Baño con receptáculo y mampara.

1. Tabique.
2. Cerámica muro.
3. Cerámica piso.
4. Empaste.
5. Aparejo.
6. Primera mano de pintura.
7. Mano final de pintura.
8. Guardapolvo cerámico.
9. Cornisa.
10. Puerta.
11. Cerradura.
12. Vanitorio.
13. Espejo.
14. Grifería.
15. Receptáculo.
16. Mampara.
17. WC.
18. Accesorios.
19. Componentes eléctricos.

### Baño 1

Baño con tina.

1. Tabique.
2. Cerámica muro.
3. Cerámica piso.
4. Empaste.
5. Aparejo.
6. Primera mano de pintura.
7. Mano final de pintura.
8. Guardapolvo cerámico.
9. Cornisa.
10. Puerta.
11. Cerradura.
12. Vanitorio.
13. Espejo.
14. Grifería.
15. Tina.
16. WC.
17. Accesorios.
18. Componentes eléctricos.

### Terraza

Aplica para Terraza Principal y Terraza Suite.

1. Textura.
2. Piso cerámico.
3. Guardapolvo cerámico.
4. Cielo.
5. Baranda vidriada.
6. Componentes eléctricos.

---

## 7. Catálogo definitivo de partidas

Catálogo provisional disponible en la aplicación:

- Tabiquería.
- Yeso / enlucido.
- Preparación base.
- Pavimento.
- Porcelanato muro.
- Porcelanato piso.
- Fragüe.
- Pintura.
- Muro.
- Cielo.
- Cornisa.
- Ventanas.
- Puerta.
- Muebles.
- Vanitorio.
- Grifería.
- Artefactos.
- Instalaciones.
- Equipamiento.
- Limpieza final.

El catálogo maestro V1 queda compuesto por 7 checklists reutilizables:

1. Living - Comedor.
2. Cocina.
3. Dormitorio.
4. Walk-in Closet.
5. Baño Principal.
6. Baño 1.
7. Terraza.

---

## 8. Etapas de construcción

**Pendiente.**

Orden provisional:

1. Obra gruesa.
2. Tabiquería.
3. Yeso y enlucidos.
4. Pavimentos.
5. Pintura.
6. Muebles y artefactos.
7. Terminación fina.
8. Preentrega.
9. Entregado.

Falta relacionar cada partida con su etapa y supervisor encargado.

---

## 9. Estados de partida

**Pendiente de revisar como catálogo completo.**

Estados provisionales:

- No iniciada.
- En proceso.
- Terminada.
- Bloqueada.
- Verificada.
- No aplica.

---

## 10. Configuración inicial y datos de origen

**Pendiente.**

Incluye cualquier dato de configuración no resuelto en los puntos anteriores.

---

## 11. Reglas de verificación y avance

### Partidas terminadas

Una partida marcada como **Terminada** no cuenta como avance completo.

Solo una partida **Verificada** cuenta como avance completado para el cálculo
del porcentaje.

### Estado No aplica

- Solo un administrador puede marcar una partida como **No aplica**.
- Debe ser una excepción poco frecuente.

### Retroceso de estados

Se permite retroceder una partida desde **Terminada** o **Verificada** a
**En proceso** cuando se detecta un trabajo incorrecto.

El retroceso exige:

- Razón obligatoria.
- Usuario que realizó el cambio.
- Fecha y hora.
- Estado anterior.
- Estado nuevo.
- Registro permanente en el historial.

---

## 12. Ponderación del avance

El avance será ponderado mediante dos categorías generales por partida:

| Categoría | Peso |
| ---------- | ---: |
| Principal  |    2 |
| Secundaria |    1 |

La ponderación representa principalmente el tiempo o volumen de trabajo.
No determina si una partida es prescindible para entregar.

Cada partida tendrá dos atributos independientes:

1. **Peso de avance:** principal o secundaria.
2. **Obligatoria para liberar:** sí o no.

Ejemplo:

| Partida             | Peso | Obligatoria para liberar |
| ------------------- | ---: | ------------------------ |
| Pintura             |    2 | Sí                      |
| Ventanas            |    2 | Sí                      |
| Vanitorio           |    1 | Sí                      |
| Espejo              |    1 | No                       |
| Accesorios de baño |    1 | No                       |
| Limpieza final      |    1 | Sí                      |

Fórmula conceptual:

```text
avance =
  suma de pesos de partidas verificadas
  /
  suma de pesos de partidas aplicables
```

Las partidas terminadas pendientes de verificación no aportan avance completo.

---

## 13. Estado operativo del departamento

El estado debe ser calculado por la aplicación y no ingresado manualmente.

### Sin revisar

El departamento todavía no tiene levantamiento.

### En proceso

Tiene partidas pendientes o en ejecución, pero no presenta un bloqueo formal.

### Bloqueado

Tiene al menos una partida bloqueada con una restricción activa.

### Observado

El departamento queda amarillo si ocurre al menos una de estas situaciones:

1. Tiene partidas secundarias pendientes, pero puede avanzar o entregarse.
2. Tiene detalles estéticos menores.
3. Tiene partidas terminadas pendientes de verificación, sin bloqueos.
4. Tiene una restricción de criticidad baja que no impide avanzar.
5. Está completamente ejecutado, pero mantiene observaciones menores abiertas.

### Liberable

Para ser liberable:

- Todas las partidas obligatorias para liberar deben estar verificadas.
- Puede conservar partidas no obligatorias pendientes.

Si quedan partidas no obligatorias pendientes, el estado visible será:

**Liberable con pendientes**, representado en verde y mostrando la cantidad de
pendientes.

### Verificado

El departamento pasa automáticamente a **Verificado** cuando todas sus partidas
aplicables están verificadas.

No necesita una acción manual adicional sobre el departamento completo.

---

## 14. Criticidad de restricciones

La criticidad se calcula automáticamente para mantener criterios consistentes.

Reglas iniciales:

- **Crítica:** partida obligatoria vencida o muy próxima al hito.
- **Alta:** partida obligatoria bloqueada dentro de plazo.
- **Media:** partida no obligatoria bloqueada que afecta el avance.
- **Baja:** detalle menor sin impacto relevante en avance o entrega.

El administrador puede modificar la criticidad de forma excepcional, con una
justificación obligatoria que quede registrada.

### Alertas por antigüedad

Como las restricciones no tendrán fecha compromiso manual, las alertas se
basarán en días abiertas:

| Criticidad | Alerta desde |
| ---------- | -----------: |
| Crítica   |       1 día |
| Alta       |      3 días |
| Media      |      7 días |
| Baja       |     14 días |

---

## 15. Restricciones al avance

Al marcar una partida como **Bloqueada**, debe registrarse:

- Causa.
- Responsable.
- Comentario opcional.
- Fotografía opcional.
- Fecha y hora automática de creación.
- Usuario que creó el bloqueo.

No se solicitará una fecha compromiso manual.

El sistema registrará automáticamente:

- Fecha de creación.
- Cambios de estado.
- Fecha de término.
- Fecha de verificación.
- Retrocesos.
- Usuario responsable de cada movimiento.

---

## 16. Problemas comunes

La aplicación utilizará un sistema mixto:

- Permitirá crear problemas comunes manualmente.
- Sugerirá agrupaciones por coincidencia de partida, causa y responsable.
- El administrador decidirá si acepta, modifica o ignora la sugerencia.

Reglas:

- Una restricción solo puede pertenecer a un problema común.
- El problema común tendrá fecha general.
- Cada restricción conservará sus fechas individuales de movimientos.
- El problema común se cerrará automáticamente cuando todas sus restricciones
  estén cerradas.

La definición de fecha general deberá revisarse, porque posteriormente se
decidió eliminar la fecha compromiso manual de las restricciones. Puede
interpretarse como fecha objetivo informativa del problema común.

---

## 17. Flujo de carga rápida en terreno

Flujo principal:

```text
Departamento → Recinto → Partidas → seleccionar partidas → aplicar estado
```

La interfaz será una tabla compacta con:

| Partida | Estado      | Acción |
| ------- | ----------- | ------- |
| Pintura | En proceso  | Cambiar |
| Ventana | Verificada  | Cambiar |
| Cornisa | No iniciada | Cambiar |

Debe permitir:

- Seleccionar varias partidas del recinto.
- Aplicar el mismo estado en una sola acción.
- Abrir los datos de restricción cuando el estado sea Bloqueada.
- Adaptarse a computador, tablet y teléfono.

---

## 18. Estado inicial de la torre

El levantamiento inicial se realizará dentro de la misma aplicación:

- Piso por piso.
- Departamento por departamento.
- Recinto por recinto.

No se importará inicialmente una planilla externa.

---

## 19. Datos históricos

El problema antiguo registrado en la base:

1. Se revisará manualmente.
2. Si sigue vigente, se convertirá al nuevo modelo.
3. No se eliminará automáticamente.

---

## 20. Dashboard principal

El mapa visual de departamentos será el componente más importante al abrir la
aplicación.

Cada departamento mostrará:

- Número.
- Porcentaje de avance.
- Color del estado.
- Cantidad de bloqueos.

Al seleccionar un departamento se mostrarán:

1. Restricciones críticas.
2. Resumen de avance por recinto.
3. Checklist y acciones de actualización.
4. Historial.

La etapa actual se calculará automáticamente según las partidas verificadas.
El administrador podrá corregirla excepcionalmente con justificación.

---

## 21. Uso y despliegue

- Uso mixto: computador, tablet y teléfono.
- Funcionamiento con conexión a internet.
- Menos de 10 usuarios simultáneos en el piloto.
- SQLite puede utilizarse durante el piloto local.
- Para despliegue web multiusuario se recomienda PostgreSQL.
- Se requiere inicio de sesión con usuario y contraseña.
- Los permisos dependerán del rol.

---

## 22. Exportaciones, fotografías e historial

### Exportaciones

- Excel para análisis.
- PDF para informes.

### Fotografías

Se permitirán fotografías opcionales:

- Al registrar un bloqueo.
- Durante la verificación.

### Historial

Se conservará el mayor historial posible para evaluar el funcionamiento de la
obra:

- Cambios de estado.
- Usuarios.
- Fechas y horas.
- Retrocesos.
- Restricciones.
- Responsables.
- Causas.
- Verificaciones.
- Cambios de criticidad.
- Agrupaciones en problemas comunes.

El historial será permanente y no se sobrescribirá.

---

## 23. Notificaciones

### MVP

Alertas dentro de la aplicación:

- Restricciones envejecidas.
- Bloqueos críticos.
- Casos que superen el límite de días según criticidad.

### Etapa posterior

- Resumen diario por correo electrónico.

No se implementarán inicialmente WhatsApp ni notificaciones push.

---

## 24. Caso operativo de referencia

1. El usuario abre un departamento.
2. Selecciona un recinto.
3. Revisa sus partidas.
4. Marca una partida como Bloqueada.
5. Registra causa, responsable, comentario opcional y fotografía opcional.
6. La aplicación registra automáticamente fecha, hora y usuario.
7. El departamento queda rojo y recalcula su avance.
8. Al resolverse el trabajo, el supervisor marca la partida Terminada.
9. La partida sigue pendiente de verificación y no cuenta como avance completo.
10. El administrador revisa y marca la partida Verificada.
11. La aplicación cierra la restricción y conserva todo el historial.
12. Se recalculan avance, etapa y estado operativo del departamento.

---

## 25. Próximas decisiones pendientes

Antes de completar el producto deben resolverse, al menos:

1. Datos generales de la obra.
2. Usuarios y roles definitivos.
3. Responsables operativos.
4. Confirmación de departamentos.
5. Cargar tipologías y asignación por departamento en la base.
6. Cargar recintos de cada tipología en la base.
7. Revisar y validar en terreno el checklist maestro V1.
8. Cerrar el catálogo definitivo de partidas si aparece alguna excepción.
9. Relación entre partidas y etapas.
10. Clasificación de cada partida:

- Principal o secundaria.
- Obligatoria o no obligatoria para liberar.

---

## 26. Alcance V1 mínima operativa

### Objetivo V1

Dejar Control Obra Pro usable en piloto real para controlar avance por
departamento, recinto y partida, con trazabilidad básica, roles simples y
dashboard operativo.

### Prioridades V1

#### 1. Pantalla Avance por departamento

- Filtrar por departamento.
- Filtrar por recinto.
- Mostrar checklist compacto.
- Permitir seleccionar varias partidas.
- Aplicar estado masivo.
- Agregar comentario único para la actualización.
- Diseñarla para uso rápido en terreno.

#### 2. Historial de cambios de partidas

- Registrar cada cambio de estado.
- Guardar:
  - Estado anterior.
  - Estado nuevo.
  - Usuario.
  - Fecha y hora.
  - Comentario.
  - Departamento.
  - Recinto.
  - Partida.
- No sobrescribir información sin trazabilidad.

#### 3. Regla de avance V1

- Solo las partidas Verificadas cuentan como avance completo oficial.
- Las partidas Terminadas pueden mostrarse como avance declarado, pero no como
  avance oficial.
- No aplica no debe contar como pendiente.
- Bloqueada y Observada no cuentan como avance.

#### 4. Roles y permisos básicos

Supervisor:

- Puede marcar No iniciada, En proceso, Terminada, Observada y Bloqueada.
- Puede agregar comentarios.
- No puede Verificar.

Administrador:

- Puede realizar todas las acciones.
- Puede Verificar.
- Puede retroceder estados.
- Puede modificar configuración.

#### 5. Pesos y obligatoriedad

- Cada partida debe tener:
  - Peso 2: partida principal.
  - Peso 1: partida secundaria.
  - Obligatoria para liberar: Sí/No.
- El avance debe poder calcularse ponderado.
- El estado Liberable debe depender de partidas obligatorias.

#### 6. Dashboard principal V1

- Mostrar avance por departamento.
- Mostrar avance por piso.
- Mostrar cantidad de bloqueos.
- Mostrar cantidad de observaciones.
- Mostrar departamentos liberables.
- Al seleccionar un departamento, mostrar ficha resumen:
  - Porcentaje de avance.
  - Estado operativo.
  - Restricciones activas.
  - Checklist.
  - Historial reciente.

#### 7. Validación de datos en terreno

- Revisar si los checklists reales coinciden con la obra.
- Ajustar partidas que sobren.
- Agregar partidas faltantes.
- Corregir excepciones por tipología.
- Validar que el uso en terreno sea rápido.

#### 8. Exportación Excel

- Exportar avance por departamento.
- Exportar partidas pendientes.
- Exportar bloqueos/restricciones.
- Exportar resumen por piso.
- PDF queda fuera de V1 mínima, salvo que exista tiempo disponible.

#### 9. Fotos

- Quedan como opcional para V1.
- Prioridad secundaria.
- Idealmente asociarlas a Bloqueada, Observada o Verificada.

### Orden de implementación recomendado

1. Mejorar pantalla de avance por departamento/recinto.
2. Crear historial de cambios de partidas.
3. Corregir cálculo de avance oficial.
4. Implementar permisos básicos Administrador/Supervisor.
5. Agregar dashboard con avance, bloqueos y ficha por departamento.
6. Exportación Excel.
7. Fotos si queda tiempo.

### Criterio de cierre V1

La V1 se considera lista cuando se pueda:

- Seleccionar un departamento.
- Seleccionar un recinto.
- Actualizar varias partidas.
- Registrar historial.
- Ver avance oficial según partidas verificadas.
- Ver bloqueos y observaciones.
- Revisar dashboard por departamento/piso.
- Exportar avance a Excel.
