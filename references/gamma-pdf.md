# PDF de presentaciones creados con Gamma (opcional)

Solo aplica si el material incluye PDF exportados de Gamma. Si no, saltá este archivo.

## 1. Marca de agua "Made with Gamma"
Es una **imagen** (~138×33 pt) en la esquina inferior derecha de cada página, más un **link** a `gamma.app` en cada página.
```bash
python scripts/quitar_marca_gamma.py ENTRADA.pdf SALIDA.pdf
```
Reemplaza la imagen del badge por una en blanco y borra los links. No toca el texto ni el fondo.
**Verificación**: por **píxeles** en el rectángulo del badge, no contando imágenes (la herramienta deja una imagen vacía, y
una portada con foto oscura da falsos positivos). `scripts/verificar_pdf.py` hace esa medición y marca las páginas a mirar:
una marca real da ~4000 px azul marino por página; una foto de portada es una sola página. Mirá la esquina con tus ojos.

## 2. Corrección de texto en el lugar
Las fuentes embebidas en estos PDF son **subconjuntos** (solo los glifos usados) y no sirven para escribir texto nuevo. Por eso
la skill trae en `assets/fonts/` las familias completas de licencia abierta (SIL OFL) que usa Gamma: Open Sans, PT Sans,
Nunito, Heebo, Instrument Sans, Corben, Crimson Pro, Libre Baskerville, Nobile, Inter y Manrope.
Dos motores (misma idea, distinta comodidad):
- `scripts/editar_pdf_texto.py`: reemplaza párrafos conservando fuente, tamaño, color, línea base, resaltados de código en
  línea, negritas, cursiva y alineación. Opciones por edición: `pagina`, `match`, `nuevo` o `reemplazos`, `modo`, `ancho`,
  `max_lineas`, `alinear`, `cursiva`, `negritas`. Recibe un dict `fuentes` {clave: ruta .ttf}.
- `scripts/gamma_editar.py`: `dump(pdf, [paginas])` lista bloques con su fuente; `aplicar(entrada, salida, ediciones)` con
  modos `span`, `bloque` y `agregar`. Busca las fuentes en `assets/fonts/` por el nombre de la fuente del PDF.
Cada línea visual de Gamma es un bloque de texto independiente: los párrafos se reconstruyen agrupando líneas con el mismo
borde izquierdo, fuente, tamaño y color. Los bordes de las tarjetas no se detectan: usá `max_lineas` si el texto nuevo puede
desbordar una tarjeta.

**Regla de oro: renderizá y MIRÁ la página antes y después de cada edición**, y comparalas por píxeles
(`scripts/comparar_pdf.py ORIG.pdf NUEVO.pdf PREFIJO pág1 pág2 ...` apila original y editada). Solo deben cambiar las
páginas editadas (`verificar_pdf.py --original`). En una corrida real la revisión visual encontró defectos de la primera
versión del motor: resaltados de código mal ubicados, texto achicado, alineación centrada o derecha perdida, cursiva y
negritas perdidas, texto desbordando una tarjeta.

## 3. Imágenes y diagramas con errores
- **Diagramas ráster** (UML, esquemas) con errores: parchear (rectángulo del color exacto del fondo + texto con la fuente más
  parecida) o regenerar el diagrama completo (por ejemplo con PlantUML) y reinsertarlo en la misma posición y tamaño. Si el
  diagrama es un JPEG de baja resolución, el parche se nota a zoom alto: documentalo.
- **Ilustraciones generadas con IA con rótulos deformados** ("Developmentline", "Dapportment"): no son texto editable. No las
  toques: **reportalas** al tutor para que las regenere en Gamma.
- **Fotos de portada con texto incrustado** (por ejemplo un título cortado o en otro idioma): son parte de la imagen original;
  reportalo.
- Si un PDF **no se puede dejar equivalente**, no lo entregues como final: dejá el texto exacto a cambiar por diapositiva
  (número, texto actual, texto corregido) para que el tutor lo corrija en Gamma y lo vuelva a exportar. La exportación vuelve
  a traer la marca de agua: pasala otra vez por `quitar_marca_gamma.py`.

## 4. Si falta un PDF
Si una actividad tiene video y práctica de un tema pero ningún apunte, avisale al tutor: puede que el Gamma exista solo en su
cuenta web. Crearlo es una decisión del tutor.

## 5. Nombres
`A<N>-<k>_<Titulo-limpio>.pdf`, numeración por actividad, sin sufijos "(1)" ni "(2)".
