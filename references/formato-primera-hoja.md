# Formato obligatorio del documento: primera hoja y bibliografía

Es el **único** formato. La primera hoja debe contener esta información, con los datos reales de la unidad:

```
Materia: <materia>
Unidad <N>: <nombre de la unidad>
Tema <N.M>: <tema del documento>
Revisor de la unidad: <Prof. Nombre y apellido>
Bibliografía:
1. Apellido, N. (Año). Título (n.ª ed.). Editorial. Cap. X: nombre del capítulo.
2. ...
3. ...
```

Ejemplo del formato (los datos son ilustrativos; reemplazar siempre por los reales y verificados):

```
Materia: Paradigmas de Programación
Unidad 4: Paradigma lógico
Tema 4.2: Listas y recursión en Prolog
Revisor de la unidad: Prof. [Nombre y apellido]
Bibliografía:
1. Bratko, I. (2012). Prolog Programming for Artificial Intelligence (4.ª ed.). Pearson. Cap. 3: Lists, operators, arithmetic.
2. Clocksin, W. F. y Mellish, C. S. (2003). Programming in Prolog: Using the ISO Standard (5.ª ed.). Springer. Cap. 3 y 7.
3. Sterling, L. y Shapiro, E. (1994). The Art of Prolog (2.ª ed.). MIT Press. Cap. 3: Recursive programming.
```

## Reglas de la bibliografía
- Formato **APA 7**, lista **numerada**, fuentes reales y pertinentes al tema (libros, especificaciones, documentación oficial).
- **Verificá cada referencia con búsqueda web**: autores, título, año, edición, editorial (o URL para documentación en línea).
- El **capítulo solo si lo pudiste confirmar**. Si no, omitilo. Si no podés verificar el año, usá "(s. f.)" y avisá.
- **Nunca inventes** una referencia, un capítulo, un año ni una edición. Si no hay fuente verificable, decile al tutor.
- Cada documento cita fuentes pertinentes a **su tema**, no la misma lista para todos por inercia.

## Resto del documento
- **Pie de página** con numeración real (campo `PAGE`, no texto fijo). La primera hoja puede ir sin número.
- **Propiedades del archivo**: autor/revisor, título coherente, fecha de hoy; sin `python-docx` ni fechas antiguas.
- Conservá el **aspecto actual** del documento (estilos, fuentes, tablas, bloques de código, márgenes): editá sobre una
  copia, clonando párrafos equivalentes; no regeneres el documento desde cero.
- **Trampa conocida**: el párrafo vacío de la portada ya contiene el salto de página. Si agregás otro salto, la página 2 sale
  en blanco. Verificá el layout al terminar.

## Si la unidad no trae documento formal
El Word es opcional. Si el material de la unidad son solo presentaciones, **ofrecele al tutor** crear el documento formal;
si no lo quiere, el formato de primera hoja se aplica al material que sí haya (si es un PDF no editable, el corrector deja
el texto exacto para que el tutor lo incorpore en la herramienta de origen).

## Verificación
`python scripts/verificar_docx.py ARCHIVO.docx --revisor "Prof. Nombre"` comprueba la primera hoja, el campo PAGE, los
metadatos y la bibliografía numerada. Es un control mecánico: la lectura y la revisión del tutor siguen siendo obligatorias.

## Consistencia entre documentos (decidir una vez, en CRITERIOS.md)
- **Subtítulo** bajo el título: el formato no lo incluye. Decidí con el tutor si se conserva en todos o se quita en todos.
- **Numeración del tema** (`Tema N.M`): confirmá el criterio (por ejemplo, un tema por actividad: 8.1, 8.2, ...).
- **Nombre de la materia**: usá el del aula (por ejemplo "Programación III") en todos, aunque el documento viejo diga otra cosa.
- **Institución y fecha**: no forman parte del formato; si el tutor las quiere, se definen dónde van antes de empezar.
- **Bibliografía específica del tema**: cada documento cita fuentes pertinentes a lo que explica. Si repetís la misma lista en
  todos, reportalo.

