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
1. Redacción: tercera persona e impersonal con "se"; presente atemporal; voz pasiva solo donde suene natural. Cero segunda
   persona (tú, vos, imperativos) y cero primera persona (vamos a, veremos, nuestro, hemos). Tiempos verbales homogéneos.
   Tono formal universitario, español neutro. {{ESTILO_EXTRA}}
2. Precisión técnica por sobre lo que digan el video o la presentación: si algo es técnicamente incorrecto, se corrige igual.
3. Reglas técnicas de la unidad: {{REGLAS_TECNICAS}}
4. Versiones reales del curso (verificadas en los archivos de build del código de {{CARPETA_CODIGO}}): {{VERSIONES_REALES}}.
   Donde un documento cite otra versión, se actualiza a la real.
5. Se conservan las ampliaciones correctas que no se ven en los videos (no recortar contenido correcto).
6. Consistencia entre documentos: subtítulo bajo el título = {{SUBTITULO: conservar en todos / quitar en todos}};
   numeración del tema = {{NUMERACION_TEMAS}}; nombre de la materia = "{{MATERIA}}"; institución y fecha = {{INSTITUCION_FECHA: no van / van en ...}}.
7. Bibliografía ESPECÍFICA del tema de cada documento (verificada). Reportar si solo hay fuentes genéricas.
8. {{DECISIONES_EXTRA}}

## 2. Formato obligatorio de la primera hoja (único formato)
Materia: {{MATERIA}} / Unidad {{UNIDAD_NUM}}: {{UNIDAD_NOMBRE}} / Tema <N.M>: <tema del documento> /
Revisor de la unidad: {{REVISOR}} / Bibliografía: lista numerada APA 7 de fuentes reales y verificadas ({{FUENTES_BIBLIOGRAFIA}}).
Capítulo solo si se pudo confirmar; si no se verifica el año, "(s. f.)" y avisar. Pie de página con campo PAGE real.
Propiedades del archivo con autor/revisor y fecha de hoy. Ver `references/formato-primera-hoja.md` de la skill.

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
