# Bibliografía de los apuntes: se lee de la sección 0 del aula y se pasa a APA 7

> **La skill no trae ninguna bibliografía guardada.** Cada persona, en cada corrida, la lee del aula de **su** materia y la
> convierte. Así sigue funcionando aunque el aula cambie de un año a otro: lo que sigue es un **procedimiento con alternativas**,
> no una lista de referencias. Estructura validada en el campus TUP (cohorte Agosto 2026) el 2026-10-03; puede cambiar.

## Regla
La bibliografía de un **apunte teórico** sale de **fuentes reales**: la sección 0 del aula de la materia. La skill **no la busca en
la web, no la completa y no la inventa**. Todas las bibliografías salen en **APA 7**, aunque el aula las tenga en otro formato
(decisión del tutor). El TP no lleva bibliografía. Si no se pudo leer la sección 0, no tiene bibliografía o alguna referencia
queda incompleta, los apuntes que la necesiten quedan **bloqueados por bibliografía** (el PDF no se genera) hasta que el tutor lo
resuelva en el campus.

## Procedimiento (una vez por materia; lo hace quien corre la skill)
1. **ID del curso.** Se pide en la Fase 0 la URL del aula (`.../course/view.php?id=<ID>`). Con la skill `tup-campus-navigator`,
   `aulas` lista los cursos del tutor. No se guardan IDs fijos: cambian con la cohorte.
2. **Abrir la sección 0**: `.../course/view.php?id=<ID>&section=0` (el DOM trae solo esa sección). Con Claude in Chrome, la sesión
   del tutor ya iniciada (**nunca** pidas ni escribas credenciales; solo lectura, no edites ni descargues). Esperá 2-3 segundos: el
   DOM carga tarde y `li.activity` puede venir vacío al principio.
3. **Ubicar el bloque, por contenido y no por posición** (la posición cambia entre materias y puede cambiar con los años):
   a. el label cuyo texto contiene **"NECESITÁS PARA ESTUDIAR"** (así estaba en 2026), y dentro, el encabezado **"BIBLIOGRAFÍA"**;
   b. si no aparece, cualquier bloque de la sección 0 con un encabezado que contenga "BIBLIOGRAF";
   c. si tampoco, **listá los títulos de las actividades de la sección 0 y preguntale al tutor dónde está**. Nunca adivines ni la
      busques en la web.
   El bloque suele estar **plegado** en pantalla ("Mostrar más"): `get_page_text` o una captura **no lo traen**; hay que leer el DOM.
4. **Leerlo**: `assets/templates/leer_bibliografia_seccion0.js` con `javascript_tool`. Límites del navegador: la salida se corta
   cerca de los 1000 caracteres (el script entrega por tramos: `DESDE`/`CUANTAS`, seguí hasta `siguiente=null`) y se **bloquea** si
   el texto trae una URL con parámetros ("Cookie/query string data"): las URL se reemplazan por `[URL]` y si aun así se bloquea,
   bajá `CUANTAS` o dejá `ENLACES=false`. Un enlace que importe (por ejemplo una lista de YouTube) **pedíselo al tutor**; no lo adivines.
5. **Transcribir** a `<trabajo>/fuentes/bibliografia.md` (formato abajo), **textual y sin emojis decorativos**, separando las líneas
   que no son referencias ("Videos del aula virtual", "Apuntes de la Cátedra", "Back up en caso de links...") y **sin corregir erratas**
   (se avisan al tutor).
6. **Convertir a APA 7** (reglas abajo) y correr `python scripts/verificar_bibliografia.py apa <trabajo>/fuentes/bibliografia.md`.
7. **Mostrarle al tutor la tabla original -> APA 7** (con las incompletas y las erratas) junto con el inventario y esperar su OK.
   Recién entonces el estado pasa a `confirmada por <nombre>`. Los formatos del aula difieren entre materias y los datos pueden
   faltar: **el tutor confirma siempre**.

## Formato de `fuentes/bibliografia.md`
```
# Bibliografía de <materia>
Fuente: sección 0 del aula (curso <ID>), bloque "<título del bloque>". Leída el <fecha>.
Estado: pendiente de confirmación del tutor | confirmada por <nombre>

## Referencias (original)
1. <referencia tal como figura en el aula, sin emojis>
2. ...

## Referencias (APA 7)
1. <misma referencia en APA 7>      (misma numeración y orden que arriba)
2. [INCOMPLETA: falta título]

## Líneas que no son referencias (no van al apunte)
- Videos del aula virtual
```

## Reglas de la conversión a APA 7 (en español)
- **Solo se reordena y se da formato a datos que ya están en el original.** Nunca se agrega un autor, un año, una editorial, una
  edición, un capítulo, una ciudad ni un enlace. `verificar_bibliografia.py apa` falla si aparece un dato que no estaba.
- **Libro**: `Apellido, I. (Año). *Título* (n.ª ed.). Editorial.` Varios autores: `Apellido, I., & Apellido, I. (Año).` (el último con
  `&`). La inicial sale del nombre de pila **si figura en el original**. La edición solo si figura.
- **Sin fecha**: `(s. f.)`. Es válido en APA 7 y no inventa nada.
- **Página web, tutorial o documentación**: `Autor u organización. (Año). *Título*. Sitio. URL`, solo con los datos presentes. Si el
  autor es el propio sitio (por ejemplo, "Baeldung"), va como autor.
- **Video o lista de reproducción**: `Autor. (Año). *Título* [Lista de reproducción]. YouTube. URL`, solo con lo que figura.
- **Incompleta**: si falta el **autor** o el **título** (o la **editorial** de un libro), no se completa: se escribe
  `[INCOMPLETA: falta <dato>]` en la lista APA. Esa referencia **bloquea** los apuntes que la usen hasta que el tutor la complete en
  el campus y se vuelva a leer.
- Las erratas del aula se transcriben tal cual en la lista original y se avisan; en APA se transcriben igual (no se "arreglan").

## Qué referencias lleva cada apunte (decisión del tutor: las del tema; si no, la general de la materia)
- El **corrector** elige, de la lista APA 7 **confirmada**, las referencias que correspondan al **tema específico** del apunte
  (por título y alcance, por ejemplo un libro de Java para un apunte de interfaces), y **escribe en el informe de cambios por qué**
  eligió cada una. **Solo elige de esa lista**: nunca agrega una fuente que no esté en el aula.
- Si no puede decidir con criterio, pone la **lista general** de la materia. En ambos casos marca la sección con
  `<!-- REVISAR: selección de referencias -->` para que el tutor la revise en la compuerta.
- Copia las referencias **textualmente** de la lista APA 7 como lista numerada, sin ninguna incompleta.
- Comprobación: `python scripts/verificar_bibliografia.py uso <final.md> <trabajo>/fuentes/bibliografia.md` (cada referencia del
  apunte tiene que estar en la lista APA 7 y no ser incompleta).
- El **detector** solo informa lo que difiere entre la bibliografía que trae el documento y la del aula. No propone fuentes nuevas.

## Variaciones que se vieron (solo como ejemplo de por qué el tutor confirma; pueden haber cambiado)
En 2026, entre tres materias del mismo campus: una en APA 7 más líneas que no son referencias; otra con `📖 Título — Autor
(Editorial, Año)`, sin APA y mezclando libros con tutoriales web; y otra con prefijo `Libro:`, formatos mezclados, una errata y un
paréntesis sin cerrar. Por eso no se asume el formato.
