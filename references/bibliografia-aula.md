# Bibliografía de los apuntes: se toma de la sección 0 del aula

> **Estado: verificado parcialmente el 2026-10-03** (solo lectura, cursos 74, 81 y 82 de la cohorte Agosto 2026: Programación I, II
> y III). Lo que figura como **[confirmado]** se vio en el aula real. Lo que sigue como **[decide el tutor]** es una decisión pendiente,
> no un dato técnico. Falta probar el flujo completo de punta a punta con un apunte real.

## Regla
La bibliografía de un **apunte teórico** sale de **fuentes reales**: la sección 0 del aula de la materia. La skill **no la busca en
la web, no la completa y no la inventa**. El TP no lleva bibliografía. Si no se pudo leer la sección 0 o no tiene bibliografía,
el apunte queda **bloqueado por bibliografía** (el PDF no se genera) hasta que el tutor lo resuelva.

## Dónde está [confirmado]
- URL de la sección 0: `.../course/view.php?id=<ID>&section=0` (un ID por materia; con `&section=0` el DOM trae solo esa sección).
  Los IDs de la cohorte vigente salen de `aulas` de la skill del campus (Agosto 2026: Prog I = 74, Prog II = 81, Prog III = 82).
- La sección 0 tiene, en orden: foros, la lección "Información importante sobre la materia", a veces una encuesta, un **label** con el
  título **"🧰 ¿QUÉ NECESITÁS PARA ESTUDIAR?"** y el cuestionario inicial. **La posición del label cambia** (4.º en Prog II y III, 5.º
  en Prog I): se lo ubica **por su texto** ("NECESITÁS"), nunca por índice.
- Dentro del label: `H3 "📚 Materiales de Estudio"` > `H4 "I. BIBLIOGRAFÍA"` con una lista `<li>` > `H4 "II. DOCUMENTOS"` (o
  "II. MATERIALES COMPLEMENTARIOS") y, a veces, `H3 "💻 Software que utilizarás"`. **La bibliografía son los `<li>` entre
  "I. BIBLIOGRAFÍA" y el siguiente `H4`/`H3`.**
- En la pantalla el label aparece **plegado** ("Mostrar más"): `get_page_text` o una captura **no traen** la bibliografía. Hay que
  leer el DOM (`textContent` del label) con `javascript_tool`.

## El formato NO es uniforme entre materias [confirmado]
| Materia | Cómo viene la bibliografía |
|---|---|
| Programación II (81) | Referencias en APA 7 (`Deitel, P. J., & Deitel, H. M. (2016). Título (10.ª ed.). Editorial.`) más 2 líneas que no son referencias ("Apuntes de la Cátedra", "Videos del aula virtual") y una lista de reproducción de YouTube con enlace |
| Programación III (82) | Formato propio, sin APA: `📖 Título — Autor (Editorial, Año)`; mezcla libros con tutoriales y documentación web; cada ítem lleva el emoji 📖 |
| Programación I (74) | Prefijo `Libro:` en cada ítem, formatos mezclados (APA parcial y "Autor. Título"), líneas que no son referencias ("Videos del aula virtual", "Back up en caso de links expirados o rotos") y erratas ("ntroduction") |

Consecuencias: **no se puede asumir APA 7**; hay líneas que no son referencias; puede haber erratas; y un enlace puede no estar en
el texto (queda en el `href` del `<a>`).

## Cómo leerla (solo lectura)
1. Pedí en la Fase 0 la **URL del aula con el ID del curso** (si el tutor ya dio el link de la unidad, el ID sale de ahí).
2. Leé la sección 0 con la skill `tup-campus-navigator` o con Claude in Chrome (sesión del tutor ya iniciada; **nunca** pidas ni
   escribas credenciales; no edites ni descargues nada). Esperá 2-3 segundos tras navegar: el DOM carga tarde y a veces `li.activity`
   viene vacío al principio.
3. Con `javascript_tool`, extraé el label (`assets/templates/leer_bibliografia_seccion0.js`, probado en Prog I). **Límites del
   navegador [confirmado]**: la salida se corta cerca de los 1000 caracteres (el script la entrega por tramos: cambiá `DESDE`
   hasta que `siguiente` sea null) y se bloquea ("Cookie/query string data") si contiene una URL con parámetros. El script reemplaza las URL por `[URL]`
   en el texto y devuelve aparte host + ruta de cada enlace; si una referencia depende de la query (por ejemplo una lista de YouTube),
   **pedile al tutor que pegue ese enlace**: no lo adivines.
4. Copiá las referencias a `<trabajo>/fuentes/bibliografia.md` con este formato:
```
# Bibliografía de <materia>
Fuente: sección 0 del aula (curso <ID>), bloque "Materiales de Estudio / I. BIBLIOGRAFÍA". Leída el <fecha>.
Estado: pendiente de confirmación del tutor | confirmada por <nombre>

## Referencias (van al apunte)
1. <referencia tal como figura en el aula, sin emojis decorativos>

## Líneas que no son referencias (no van al apunte; se muestran al tutor)
- Videos del aula virtual
```
5. Mostrásela al tutor junto con el inventario (Fase 1) y esperá su OK, **marcando erratas evidentes sin corregirlas** (por ejemplo
   "ntroduction"). Si no hay acceso al aula, no se encuentra el label o no trae bibliografía: **no sigas con los apuntes**; avisá y
   dejá esos documentos como "bloqueado por bibliografía".

## Cómo se usa en cada apunte
- El **corrector** copia al final del `.final.md` la sección `## Bibliografía` con las referencias de `fuentes/bibliografia.md`
  (solo las de "Referencias"), como lista numerada, **sin agregar ninguna que no esté ahí**. Solo se quitan los emojis decorativos.
- El **detector** solo informa: compara la bibliografía que trae el documento con la del aula y reporta lo que difiere. No propone
  referencias nuevas.

## Decisiones pendientes del tutor [decide el tutor]
1. **Formato**: la plantilla pedía APA 7, pero el aula trae formatos distintos por materia. Mientras no decida, se transcribe
   **tal cual** (sin emojis) y se avisa; convertir a APA 7 implica reordenar autor, año y editorial, y eso lo valida el tutor.
2. **Qué referencias lleva cada apunte**: ¿toda la bibliografía de la materia o solo las pertinentes al tema? Mientras no decida,
   el corrector pone la lista completa y la marca con `<!-- REVISAR -->`.
3. **Líneas que no son referencias** ("Videos del aula virtual", "Apuntes de la Cátedra", "Back up en caso de links..."): por defecto
   no van al apunte.
4. **Erratas** en el aula: se transcriben tal cual y se le avisan al tutor para que las corrija en el campus.
