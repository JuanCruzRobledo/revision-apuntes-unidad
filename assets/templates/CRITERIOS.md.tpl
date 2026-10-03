# Criterios únicos de corrección: Unidad {{UNIDAD_NUM}} ({{UNIDAD_NOMBRE}}) de {{MATERIA}}

Documento de referencia para TODOS los subagentes. Revisor de la unidad: {{REVISOR}}.
Cada subagente trabaja UNA actividad: el material de esa actividad ({{TIPOS_DE_MATERIAL}}).

## 0. Reglas duras
- NUNCA modificar, mover ni borrar los originales ({{CARPETA_ORIGINALES}}). Siempre trabajar sobre copias.
- No tocar el aula (Moodle): solo lectura; no subir, no borrar, no descargar nada de ella.
- No inventar datos, referencias, capítulos, años, ediciones ni versiones. Si algo es ambiguo o no se puede verificar: NO
  asumirlo; listarlo como duda abierta en el informe.
- Escribir SOLO dentro de {{TRABAJO}}/corregidos/, {{TRABAJO}}/informes/ y el scratchpad.

## 1. Decisiones del tutor (definitivas)
1. Estilo de redacción elegido por el tutor: {{ESTILO: por defecto "tercera persona e impersonal con 'se'; presente atemporal;
   voz pasiva solo donde suene natural; cero segunda persona (tú, vos, imperativos) y cero primera persona (vamos a, veremos,
   nuestro, hemos); tiempos verbales homogéneos; tono formal universitario, español neutro"; o el que indique el tutor}}.
   {{ESTILO_EXTRA}}
   Verificadores: {{VERIFICADORES: con el estilo por defecto, correr normal; con otro estilo, correr con --sin-persona}}.
2. Precisión técnica por sobre lo que digan el video o la presentación: si algo es técnicamente incorrecto, se corrige igual.
3. Reglas técnicas de la unidad (pueden no existir): {{REGLAS_TECNICAS}}
4. Versiones reales del curso, solo si la materia tiene código (verificadas en los archivos de build de {{CARPETA_CODIGO}}):
   {{VERSIONES_REALES}}. Donde un documento cite otra versión, se actualiza a la real.
5. Se conservan las ampliaciones correctas que no se ven en los videos (no recortar contenido correcto).
6. Formato: NO se cambia el formato que cada archivo ya tiene (estilos, fuentes, tablas, márgenes, subtítulos, institución,
   fecha, estructura). Nombre de la materia = "{{MATERIA}}" (el del aula) en la portada.
7. Bibliografía: en apuntes de la plantilla sale de la sección 0 del aula (`fuentes/bibliografia.md`), convertida a APA 7 sin
   agregar ningún dato y confirmada por el tutor; cada apunte lleva las referencias de su tema (si no se puede decidir, la general
   de la materia). En el resto del material, si el archivo la trae se verifica que sea real y específica del tema (no la misma lista
   genérica en todos); no se mueve ni se reformatea. Si no la trae, se informa y decide el tutor.
8. {{DECISIONES_EXTRA}}

## 2. Portada: datos mínimos (lo único estricto)
La portada debe identificar: Materia: {{MATERIA}} / Unidad {{UNIDAD_NUM}}: {{UNIDAD_NOMBRE}} / Tema <N.M>: <tema del documento> /
Revisor de la unidad: {{REVISOR}}. Si el archivo ya los trae, no se tocan salvo que sean incorrectos o falte el revisor; si falta
alguno, se agrega con el estilo del propio archivo. El resto de la hoja se deja como está.
Bibliografía: solo control de calidad ({{FUENTES_BIBLIOGRAFIA}}); capítulo solo si se pudo confirmar; si no se verifica el año,
no completarlo y avisar. Pie con campo PAGE real si el documento ya numera las páginas. Propiedades del archivo con
autor/revisor y fecha de hoy. Ver `references/formato-primera-hoja.md` de la skill.

## 3. Documentos Word: qué revisar y cómo corregir
Conservar el aspecto actual (estilos, tablas, código, márgenes). Editar sobre una copia a nivel de run/XML o clonando
párrafos equivalentes; NO regenerar desde cero. Controles (patrones + lectura COMPLETA): tercera persona; tiempos verbales;
rastros de IA; calidad general; contraste con lo visto (sobra/falta/contradice); corrección técnica contra el código real;
cierre formal. Detalle: `references/criterios-redaccion.md`.
{{BLOQUE_GAMMA}}

## 4. Estructura y nombres de salida
```
{{TRABAJO}}/corregidos/Actividad_N/
    AN-Documento-formal_<Tema-corto>.docx
    AN-1_<Titulo-limpio>.pdf, AN-2_...   (numeración por actividad; sin sufijos "(1)" ni "(2)")
{{TRABAJO}}/informes/<id>_informe.md   (detector)   <id>_cambios.md (corrector)   gamma_AN_cambios.md
```

## 5. Verificación obligatoria antes de terminar
Word: relectura completa; `scripts/verificar_docx.py` = 0 casos de segunda/primera persona, futuros, markdown, emojis y guiones
largos (salvo código y URLs); campo PAGE; primera hoja; propiedades; layout (exportar a PDF si hay Word/LibreOffice; si no hay,
decirlo). PDF: `scripts/verificar_pdf.py`: 0 links a Gamma, marca ausente por píxeles, mismas páginas que el original,
captura visual de las páginas modificadas. Entregar el cambio-log con aplicado / parcial / no aplicado y las dudas abiertas.
**Ningún archivo se declara listo para subir: queda pendiente de la revisión manual del tutor.**
