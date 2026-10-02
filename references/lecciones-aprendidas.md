# Lecciones aprendidas (de una corrida real de 5 actividades)

Leelas ante cualquier tropiezo. Cada una costó tiempo la primera vez.

1. **YouTube bloquea la IP** si se piden muchas transcripciones seguidas (`RequestBlocked`). Pausa larga entre pedidos y, al
   primer bloqueo, parar. Intentar leer los subtítulos desde la página con JS puede colgar la pestaña; el panel "Mostrar
   transcripción" no siempre carga. No uses proxies. Los guiones del tutor cubren el hueco.
2. **El guion no es lo dicho en el video**: en la práctica el video dura bastante más (a veces el doble) y el vocabulario
   compartido ronda 55–80 %. Útil como base, no como verdad exacta.
3. **La marca de agua se mide por píxeles.** La herramienta deja una imagen en blanco en lugar de borrarla, así que contar
   imágenes da falsos positivos; las portadas con foto oscura también. Medí el rectángulo del badge y mirá la esquina.
4. **Las fuentes embebidas en PDF de Gamma son subconjuntos**: no se puede escribir texto nuevo con ellas. Hay que usar las
   familias completas (OFL). Un subagente que "se rindió" por esto dejó pendiente un PDF que otro resolvió después.
5. **Los hallazgos de "segunda persona" tienen muchos falsos positivos** ("usa", "considera" en tercera persona). Leelos en
   contexto antes de reportarlos.
6. **El párrafo vacío de la portada de un Word ya contiene el salto de página**; agregar otro deja la página 2 en blanco.
7. **Un reporte de subagente no es evidencia.** Verificá con los scripts y mirando las páginas. Los subagentes admitieron
   revisión visual parcial y detectaron errores propios solo al mirar el resultado.
8. **Sin Word ni LibreOffice no hay revisión de layout automática**: decilo explícitamente en lugar de afirmar que "se ve
   bien". Es parte de por qué la revisión manual del tutor es obligatoria.
9. **Sesión cortada**: los subagentes en segundo plano pueden cortarse al cerrar la sesión. Retomalos con `SendMessage` y
   revisá qué dejaron escrito.
10. **Errores técnicos que los videos repiten** (valores atribuidos a la propiedad equivocada, nombres de columna distintos del
    código real, dueño de la relación invertido): el documento se corrige con precisión técnica aunque el video diga otra cosa;
    el desajuste con el video se le avisa al tutor.
11. **Versiones y namespaces**: verificalos en los archivos de build y en los `persistence.xml`/configuración del código real,
    no los asumas. Algunos videos mezclan convenciones viejas y nuevas.
12. **Ilustraciones de IA con rótulos deformados** y **diagramas JPEG de baja resolución** no se arreglan por texto: reportalos.
13. **El bloque "Actividad reciente" del campus** puede mostrar archivos que no son de la unidad: no los confundas.
14. **El tutor puede tener los apuntes embebidos en un label** y no en una carpeta; hay que crear la carpeta al subir.
15. **[En pausa hasta que exista la plantilla oficial]** Dos formatos de primera hoja en circulación: esta lección nació cuando
    había un formato único y se rehacían las portadas. Hoy la skill respeta el formato de cada archivo y solo exige los datos
    mínimos de portada (`references/formato-primera-hoja.md`). Si conviven formatos distintos, avisale al tutor y no los unifiques.
16. **Descargas de red de los subagentes** (fuentes, páginas): avisale al tutor qué se bajó y por qué.
17. **Los subagentes no deben decidir por su cuenta el subtítulo ni otros detalles de portada.** En una corrida, cuatro de cinco
    subagentes conservaron el subtítulo y uno lo eliminó: los documentos quedaron inconsistentes. Con la regla vigente (se
    respeta el formato de cada archivo) la consigna es simple y vale para todos: no se agrega ni se quita nada de la portada
    salvo los datos mínimos. Cuando llegue la plantilla oficial, este punto se decide ahí, una vez, en CRITERIOS.md.
18. **La numeración de los temas ("Tema 8.2") era una suposición** si el formato no la define. Hoy solo se completa cuando
    falta, con una regla fija: N = unidad, M = orden de la actividad en el aula (sale del inventario de la Fase 1). Si el archivo
    ya trae otra numeración, se respeta y se avisa si no es coherente entre archivos.
19. **La bibliografía por inercia se repite.** Si los subagentes reutilizan las mismas fuentes genéricas en todos los
    documentos (por ejemplo la especificación y la documentación del producto), no son pertinentes al tema de cada uno.
    Pedí en el corrector una bibliografía **específica del tema** (verificada); si solo hay fuentes genéricas, reportalo.
20. **Exportar un .docx a PDF con Word falla con rutas cortas tipo `C:\USERS\<USUARIO~1>`** (el carácter `~`). Usá una ruta
    simple sin `~` para la exportación.
21. **El verificador no debe tratar "todo" como marcador de plantilla**: `TODO` solo cuenta en mayúsculas (corregido en
    `verificar_docx.py`). Un patrón con `re.I` puede dar falsos positivos en español.
22. **Si por algún motivo cambia la estructura del documento, el número de páginas puede variar** (por ejemplo, al sacar una
    página que solo tenía la bibliografía): verificá las páginas antes y después y que no quede una hoja en blanco. Con la regla
    actual no se mueve la bibliografía, así que no debería pasar.
23. **Conservá siempre la versión anterior** (`corregidos/_version_anterior/`) cuando se rehace una parte de un documento ya
    corregido: el tutor puede querer volver atrás.
24. **Exportá los Word a PDF con `scripts/word_a_pdf.py`** y revisá todas las páginas (hoja de contactos), no solo la 1 y la 2:
    los subagentes solo habían mirado esas dos. El script resuelve las rutas cortas con `~`, compara las páginas del PDF con las que
    informa Word y avisa de páginas en blanco. El tamaño de página sale del Word (los generados con python-docx suelen ser Letter y
    no A4): si el tutor necesita A4, hay que cambiarlo en el Word antes de exportar.
25. **Revisá los METADATOS de los commits antes del primer push, no solo los archivos.** En una publicación real el email del autor
    (el de la configuración global de git) quedó visible en un repo público —API, `commit/<sha>` y `.patch`— y borrarlo exigió
    reescribir el historial y finalmente recrear el repo. Configurá el email `ID+usuario@users.noreply.github.com` ANTES de commitear
    y corré `scripts/escaneo_privacidad.py`. Un push forzado publica en el feed de eventos el SHA viejo (`before`), así que reescribir
    el historial de un repo público no alcanza: hay que recrear el repo.

