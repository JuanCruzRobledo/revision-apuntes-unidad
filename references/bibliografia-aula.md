# Bibliografía de los apuntes: se toma de la sección 0 del aula

> **Estado: SIN VERIFICAR contra el aula real.** Esto se escribió a partir de cómo el tutor describe el campus; el aula no estaba
> disponible al implementarlo. La primera vez que se use hay que comprobar cada paso con el aula a la vista y, si algo difiere,
> corregir este archivo. Las partes dudosas están marcadas como **[a confirmar]**.

## Regla
La bibliografía de un **apunte teórico** sale de **fuentes reales**: la sección 0 del aula de la materia. La skill **no la busca en
la web, no la completa y no la inventa**. El TP no lleva bibliografía. Si no se pudo leer la sección 0 o no tiene bibliografía,
el apunte queda **bloqueado por bibliografía** (el PDF no se genera) hasta que el tutor lo resuelva.

## Dónde está
- La URL del aula tiene el **ID del curso**: `.../course/view.php?id=<ID>` (un ID por materia). La **sección 0** es la primera:
  `...?id=<ID>&section=0` o el primer bloque de la página del curso. Es la de **presentación de la materia**; las unidades están
  en otras secciones (por ejemplo, la unidad 7 puede estar en la sección 30). **[a confirmar: formato exacto de la URL]**
- Abajo del todo hay un bloque HTML (un label o página) con un título del tipo **"Qué necesitás para estudiar"** / "Qué necesitas
  saber". Ahí está la bibliografía. **[a confirmar: título exacto y si es un label, una página o un recurso]**

## Cómo leerla (solo lectura)
1. Pedí en la Fase 0 la **URL del aula con el ID del curso** (si el tutor ya dio el link de la unidad, el ID sale de ahí).
2. Leé la sección 0 con la skill `tup-campus-navigator` o con Claude in Chrome (sesión del tutor ya iniciada; **nunca** pidas ni
   escribas credenciales; no edites ni descargues nada). Límites del navegador: `references/flujo-detallado.md`.
3. Ubicá el bloque "Qué necesitás para estudiar", extraé el texto con `textContent` (espacios colapsados) y los enlaces.
4. Copiá **textualmente** las referencias, sin corregir ni completar, a `<trabajo>/fuentes/bibliografia.md` con este formato:
```
# Bibliografía de <materia>
Fuente: sección 0 del aula (curso <ID>), bloque "<título exacto>". Leída el <fecha>.
Estado: pendiente de confirmación del tutor | confirmada por <nombre>

1. <referencia 1 tal como figura en el aula>
2. <referencia 2>
```
5. Mostrásela al tutor junto con el inventario (Fase 1) y esperá su OK. Si no hay acceso al aula, no se encuentra el bloque o no
   trae bibliografía: **no sigas con los apuntes**; avisá y dejá esos documentos como "bloqueado por bibliografía".

## Cómo se usa en cada apunte
- El **corrector** copia al final del `.final.md` la sección `## Bibliografía` con las referencias de `fuentes/bibliografia.md`,
  como lista numerada, **sin agregar ninguna que no esté ahí**.
- El **detector** solo informa: compara la bibliografía que trae el documento con la del aula y reporta lo que difiere (referencias
  que no están en el aula, o del aula que el documento no cita). No propone referencias nuevas.

## Preguntas abiertas (definir con el aula a la vista)
- **[a confirmar]** ¿Cada apunte lleva **toda** la bibliografía de la materia, o solo las referencias pertinentes a su tema? Hasta
  que el tutor lo defina, el corrector pone la lista completa y lo marca con `<!-- REVISAR -->` para que el tutor decida.
- **[a confirmar]** ¿La bibliografía del aula ya viene en **APA 7**? Si no, se transcribe tal cual y se avisa; no se reescribe
  sin que el tutor lo pida, porque cambiar autores, años o ediciones sería inventar.
- **[a confirmar]** ¿La bibliografía es la misma para todas las unidades de la materia? (se asume que sí: una vez por materia).
