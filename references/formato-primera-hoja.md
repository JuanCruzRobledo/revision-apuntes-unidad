# Portada y formato: plantilla única (teoría y TP) y datos mínimos (resto del material)

## A. Teoría y TP: plantilla única (`assets/plantilla/`)
Todos los documentos **teóricos (apuntes)** y **TP** de todas las materias salen con la misma plantilla (Markdown -> HTML -> PDF
con Chrome o Edge). El diseño y la estructura **no se rediseñan**: la plantilla se usa tal cual. El resultado final es siempre un PDF.

**Primera hoja** (los datos salen de la Fase 0; el revisor es quien hace la auditoría; no hay autor ni año):
```
Materia: <materia>
UNIDAD <N> · <NOMBRE DE LA UNIDAD>
[ APUNTE TEÓRICO ]  o  [ TRABAJO PRÁCTICO ]
<Título grande: tema del apunte, o título del TP>
Revisor de la unidad: Prof. <Nombre y apellido>
```
El título grande sale una sola vez: si el Markdown trae su propio `# Título`, se descarta. No hay línea "Tema N.M".
Cabecera (logo UTN y nombre de la carrera) en todas las hojas; pie con `Materia` y `Página N de M`.

**Estructura por tipo**
- **Apunte teórico** (`tipo: apunte`): secciones `##` con el desarrollo, código con su explicación, cajas (importante, nota,
  buenas prácticas, analogía), tablas y, al final, `## Bibliografía`.
- **TP** (`tipo: tp`): Objetivos, Consignas (cada `###` es un ejercicio numerado, con `[N puntos]` al final del título),
  Criterios de evaluación y Formato de entrega. **El TP no lleva bibliografía.**

**Bibliografía (solo teoría)**: obligatoria, al final, como lista numerada. **Sale de fuentes reales: la sección 0 del aula de la
materia**, bloque "Qué necesitás para estudiar" (cómo leerla, formato del archivo y preguntas abiertas en
`references/bibliografia-aula.md`; **esa parte está sin verificar contra el aula real**). Nunca se busca en la web ni se inventa. Si
no se pudo leer, no hay bibliografía o el tutor no la confirmó, **el documento no se genera** (`generar.py` se detiene).

**Contenido vs. estilo**: el contenido del tema se respeta SÍ o SÍ (no se quita ni se resume nada; solo se corrigen los errores
que detecta la auditoría). Lo que se unifica es el estilo y la estructura. La portada original del documento (título, materia,
unidad, autor, año) se reemplaza por la primera hoja de la plantilla y eso se registra en el informe de cambios.

**Qué documentos entran**: los que el tutor confirme en la Fase 1 como `apunte` o `tp` (`scripts/clasificar_documento.py` sugiere).
Las **presentaciones** (Gamma o no: PDF apaisado 16:9 con poco texto) **no pasan por la plantilla**. Un PDF generado con Gamma pero
en A4 vertical con texto corrido es un documento y sí pasa.

**Cómo se reconstruye** (ver SKILL.md, Fase 5): fuente -> Markdown (`docx_a_md.py` o `pdf_a_md.py`) -> el detector audita el
Markdown -> el corrector aplica el informe sobre el Markdown -> `assets/plantilla/generar.py` -> PDF. Comprobaciones:
`verificar_fidelidad.py` (no se perdió contenido) y `verificar_plantilla.py` (primera hoja, etiqueta, pie, bibliografía).

## B. Resto del material (presentaciones, Gamma, otros PDF, pptx)
La plantilla **no aplica**. Se corrige el contenido y se **respeta el formato que el archivo ya tiene**: no se rehace, no cambia
estilos, fuentes, tablas ni márgenes, y no se mueven secciones de lugar.

Lo único que se exige a este material es que la portada (primera hoja o diapositiva) identifique el material y a quien lo auditó:

```
Materia: <materia>
Unidad <N>: <nombre de la unidad>
Tema <N.M>: <tema del documento>
Revisor de la unidad: <Prof. Nombre y apellido>
```

- Si el archivo **ya trae** estos datos, no se tocan salvo que sean incorrectos (por ejemplo, materia con otro nombre que el del
  aula) o falte el revisor.
- Si **falta alguno**, se agrega en la portada con el estilo que el archivo ya usa (clonando un párrafo equivalente).
- El **revisor** es la persona que hizo la auditoría. Se pide en la Fase 0 y debe figurar en la portada.
- Los rótulos pueden variar de redacción si el archivo ya los usa distinto ("Asignatura" en lugar de "Materia"): lo que
  importa es que el dato esté.

## Qué NO se decide ni se pregunta
No hay que decidir subtítulo, institución ni fecha en la portada: se deja lo que el archivo ya tenga y no se agrega nada
nuevo. La numeración del tema (`Tema N.M`) solo se completa si falta: **N** es el número de unidad y **M** el orden de la
actividad en el aula. Si el archivo ya trae otra numeración, se respeta y se avisa al tutor si no es coherente entre archivos.

## Bibliografía: control de calidad, no formato
La skill **no mueve ni reformatea** la bibliografía. Si el archivo ya la trae, la revisa:
- Que las referencias sean **reales** y pertinentes al tema (verificá cada una con búsqueda web: autores, título, año, edición,
  editorial o URL).
- **Nunca inventes** una referencia, un capítulo, un año ni una edición. Si no podés verificar el año, no lo completes y avisá.
- Si todos los documentos citan la misma lista genérica por inercia, reportalo.
- Si el archivo **no trae** bibliografía, se informa como observación; agregarla es decisión del tutor.

## Resto del documento (Word)
- **Pie de página** con numeración real (campo `PAGE`) si el documento ya tiene numeración: verificá que no sea texto fijo.
- **Propiedades del archivo**: autor/revisor y fecha de hoy; sin rastros de `python-docx` ni fechas antiguas.
- Conservá el **aspecto actual** (estilos, fuentes, tablas, bloques de código, márgenes): editá sobre una copia, clonando
  párrafos equivalentes; no regeneres el documento desde cero.
- **Trampa conocida**: el párrafo vacío de la portada puede contener el salto de página. Si agregás otro, la página 2 sale en
  blanco. Verificá el layout al terminar.

## Si la unidad no trae documento formal
El Word es opcional. Si el material son solo presentaciones, **ofrecele al tutor** crear el documento formal; si no lo quiere,
los datos mínimos de portada se aplican al material que haya (si es un PDF no editable, el corrector deja el texto exacto para
que el tutor lo incorpore en la herramienta de origen).

## Verificación
`python scripts/verificar_docx.py ARCHIVO.docx --revisor "Prof. Nombre"` comprueba los datos mínimos de portada, el campo PAGE
y los metadatos, y cuenta las referencias detectadas (solo informativo). Es un control mecánico: la lectura y la revisión del
tutor siguen siendo obligatorias.
