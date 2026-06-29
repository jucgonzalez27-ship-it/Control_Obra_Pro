# Control Obra Pro - Documentación

Estado: DEFINIDO

Este índice ordena la documentación funcional y de implementación de Control Obra Pro V1.

## Estructura

- `00_PRODUCTO.md`: visión del producto, foco operativo y límites de alcance.
- `01_REGLAS_PARA_CODEX.md`: reglas obligatorias para que Codex implemente sin inventar.
- `02_ESTADO_V1.md`: estado consolidado de V1, implementado, pendiente y fuera de alcance.
- `03_MODELO_FUNCIONAL/`: reglas funcionales del producto.
- `04_CONFIGURACION/`: configuración funcional de tipologías, recintos, partidas, pesos, especialidades y dependencias.
- `05_SPRINTS/`: trabajo ordenado por sprint.
- `06_BACKLOG/`: temas futuros o fuera de V1.
- `07_DECISIONES/`: decisiones funcionales congeladas o pendientes.

## Estados De Documentos

- DEFINIDO: contenido aprobado para guiar implementación.
- PENDIENTE: requiere definición funcional antes de implementar.
- CONGELADO: no modificar sin autorización explícita.
- FUTURO: fuera de V1 o para versiones posteriores.

## Documentos Congelados

- `01_REGLAS_PARA_CODEX.md`
- `07_DECISIONES/DEC_001_Dependencias_Criticas.md`
- `07_DECISIONES/DEC_002_Especialidades.md`
- `07_DECISIONES/DEC_003_Pesos.md`
- `07_DECISIONES/DEC_004_Centro_de_Comando.md`
- `07_DECISIONES/DEC_005_Filosofia_Verificacion_Liberacion.md`
- `07_DECISIONES/DEC_011_Orden_Operativo_Recintos.md`
- `05_SPRINTS/Sprint_04_UX_Centro_de_Comando.md`

## Documentos Pendientes

- `05_SPRINTS/Sprint_02_Inspeccion_Terreno.md`
- `05_SPRINTS/Sprint_03_Cierre_Config_V1.md`
- `06_BACKLOG/V1_1.md`
- Cualquier sección marcada como `PENDIENTE DE DEFINICIÓN`.

## Dónde Debe Mirar Codex Antes De Implementar

1. `01_REGLAS_PARA_CODEX.md`
2. `02_ESTADO_V1.md`
3. Documento funcional específico en `03_MODELO_FUNCIONAL/`
4. Documento de configuración específico en `04_CONFIGURACION/`
5. Decisión relacionada en `07_DECISIONES/`

## Qué No Debe Modificar Sin Autorización

- Reglas de negocio.
- Estados existentes.
- Flujo de avance.
- Reglas de liberación.
- Dependencias críticas.
- Pesos operativos.
- Especialidades.
- Alcance V1.
- Documentos marcados como CONGELADO.

Si falta información funcional, Codex debe detenerse y documentar: `PENDIENTE DE DEFINICIÓN`.
