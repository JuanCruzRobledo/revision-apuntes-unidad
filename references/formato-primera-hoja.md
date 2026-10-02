# Portada: datos mínimos (lo único estricto)

Por ahora **no hay un formato estándar de documento**: cada materia y cada unidad pueden traer material distinto (Word, PDF,
presentaciones, otros). La skill corrige el contenido y **respeta el formato que el archivo ya tiene**: no lo rehace, no cambia
estilos, fuentes, tablas ni márgenes, y no mueve secciones de lugar. Cuando exista una plantilla oficial, este archivo se
reemplaza por ella.

Lo único que se exige es que la portada (primera hoja o diapositiva) identifique el material y a quien lo auditó:

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
