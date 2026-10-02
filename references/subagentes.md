# Subagentes: detector y corrector

Un par por actividad. Los prompts base están en `assets/templates/prompt-detector.md` y `prompt-corrector.md`; completá
las llaves `{{...}}` y pegalos como prompt del subagente.

## Por qué dos roles
- El **informe** del detector es un contrato verificable: cada hallazgo tiene ubicación, texto original citado y propuesta.
- El **corrector** trabaja contra ese contrato y contra `CRITERIOS.md`, no contra su propia lectura. Un corrector que también
  audita tiende a justificar lo que ya cambió y a ocultar lo que no pudo arreglar.
- Si un subagente reporta "todo aplicado", vos lo verificás con los scripts (Fase 6): el reporte no es evidencia.

## Cómo lanzarlos
- Usá subagentes que **hereden el contexto de la conversación** (fork) cuando el criterio se construyó charlando con el
  tutor; usá subagentes nuevos con prompt completo cuando `CRITERIOS.md` ya lo recoge todo.
- Piloto con **una** actividad primero. Recién con el OK del tutor, el resto **en paralelo**: cada uno escribe solo en su
  carpeta (`corregidos/Actividad_N/`, `informes/`), así no se pisan.
- Todos leen `CRITERIOS.md` como fuente única. Si lo cambiás a mitad de camino, avisales.
- Dales una **herramienta compartida** ya probada (scripts de esta skill) en lugar de dejar que cada uno escriba la suya.

## Qué esperar de cada uno
**Detector** (solo lectura): informe con (a) resumen ejecutivo con conteos por tipo y severidad y veredicto global,
(b) contraste con lo visto (sobra / falta / contradice), (c) tabla de hallazgos con ID, ubicación (`[P012]` o diapositiva),
tipo, severidad, texto original citado y propuesta de reescritura, (d) estado del cierre formal, (e) preguntas abiertas que
**no** resolvió por su cuenta.

**Corrector**: archivo corregido en `corregidos/Actividad_N/` y registro de cambios (ID → antes/después → aplicado /
parcial / no aplicado y por qué), resultado de la verificación y dudas abiertas. Debe verificar relectura completa,
búsqueda por patrones, campo PAGE, portada, y layout (exportando a PDF si hay Word o LibreOffice; si no, **decirlo**).

## Cuando algo sale mal
- **Subagente cortado** (se cerró la sesión, falló una herramienta): no rehagas desde cero. Retomalo con `SendMessage` y
  revisá primero qué alcanzó a escribir (archivos con fecha reciente, scratchpad, carpeta de salida).
- **Dos subagentes parchean la misma herramienta compartida**: pedí que trabajen sobre una **copia local** del motor y no
  modifiquen el compartido.
- **El corrector se rindió** ("no se puede editar el texto de este PDF"): puede que otra actividad ya haya resuelto ese
  problema (por ejemplo con las fuentes completas). Revisá antes de aceptar un "pendiente".
- **Descargas de red** (fuentes, bibliografía): permitidas para verificar fuentes y obtener fuentes tipográficas de licencia
  abierta, pero avisale al tutor lo que se bajó.

## Qué resolvés vos y qué preguntás
Las dudas que dejan los subagentes se resuelven con la información disponible: el aula, el código real del curso, los
guiones, los archivos de build. Solo preguntale al tutor lo que **no** podés resolver (por ejemplo, un proyecto de código
que no existe en su carpeta, o una decisión de estilo subjetiva).
