# Flujo detallado: inventario del aula y fuente de verdad

## Cómo leer el aula (solo lectura)
Preferí la skill `tup-campus-navigator`. Si no está disponible, Claude in Chrome con la sesión del tutor ya iniciada
(nunca pidas ni escribas credenciales). En ambos casos: **no edites, no subas, no borres, no descargues nada del aula**.

### Con Chrome (límites aprendidos)
- La salida de `javascript_tool` se corta cerca de los 1000 caracteres: devolvé listados compactos, una línea por elemento
  (`idx|tipo|nombre|id`), y pedí por tramos.
- Si el navegador bloquea la salida por contener "datos de cookie/query string", **limpiá los parámetros de las URL**
  antes de mostrarlas (dejá solo host + ruta, o solo el nombre del archivo).
- Los labels de Moodle traen los videos y descripciones: sus `innerText` están llenos de espacios; usá `textContent` con
  los espacios colapsados y extraé los títulos de video de los nodos hoja que contienen "Video N".
- Los IDs de YouTube se sacan del HTML del label (`embed/`, `v=`, `youtu.be/`), no del texto visible.
- Listá los archivos de las carpetas con un `fetch` GET a `mod/folder/view.php?id=...` y leyendo los enlaces
  `pluginfile.php` (solo el nombre decodificado del archivo).
- Para ver adjuntos de práctica/resolución, el nombre aparece en la página de la tarea o en la redirección del recurso.
  No descargues: alcanza con el nombre.

### Sección 0 (bibliografía de los apuntes)
Si hay apuntes para la plantilla, además de la unidad leé la **sección 0** del curso (presentación de la materia): bloque
"Qué necesitás para estudiar". Procedimiento, formato del archivo y puntos a confirmar: `references/bibliografia-aula.md`
(**sin verificar contra el aula real**). Es solo lectura, igual que el resto.

### Qué buscar en cada actividad
Carpeta de apuntes (archivos), cuestionario, práctica (PDF) y resolución (ZIP), videos con duración, infografías,
adjuntos de código. Un apunte puede estar **embebido en un label** (ruta `mod_label/intro/`) y no en una carpeta: es un
caso real y el tutor tiene que decidir si crea la carpeta.

### Qué mostrar al tutor (y esperar OK)
Tabla por actividad: apuntes en el aula vs. archivos locales → coincide / falta / sobra. Marcá duplicados exactos (hash),
sufijos "(1)", numeración inconsistente, actividades sin carpeta, archivos del bloque "Actividad reciente" que no
pertenecen a la unidad (no los confundas con material de la unidad).

## Fuente de verdad de lo visto
1. **Transcripciones reales** (`scripts/transcribir_youtube.py`). Pausa de 20 s o más entre pedidos. Ante el primer
   bloqueo, el script se detiene. **No uses proxies ni reintentes en ráfaga.** Alternativa legítima: que el tutor pegue la
   transcripción desde "Mostrar transcripción" de YouTube.
2. **Guiones** de los videos (suelen estar en la carpeta del tutor). Son más cortos que lo realmente dicho (en la práctica
   el video dura bastante más que el guion): sirven de base, no de verdad exacta. Si solo hay guion, marcalo en el informe
   como "fuente menos fiable" y sé prudente con hallazgos del tipo "esto no se vio".
3. **Descripción de la actividad** en el aula (objetivos, tiempos, temas).

Nivel de detalle: **a grandes rasgos**. El objetivo es saber qué temas cubre cada actividad para detectar contenido que
sobra, falta o contradice; no auditar el video palabra por palabra.

## Señales a reportar
- Numeración vieja de videos en guiones o documentos (por ejemplo "Video 13" en la actividad 5 de una unidad reordenada).
- Un tema con video y práctica pero **sin apunte**: avisá al tutor; puede que exista en otra carpeta o solo en Gamma.
- Contenido del documento que depende de un proyecto de código que no está en la carpeta del tutor: dejalo como
  "contrastado solo con la transcripción".
