# revision-apuntes-unidad

Skill para revisar y corregir el **material de apuntes de una unidad** de una materia del campus Moodle (documentos
**Word**, **PDF** de presentaciones con o sin **Gamma**, pptx, markdown), con **subagentes detector y corrector** por actividad
y una **revisión manual obligatoria** del tutor antes de subir.

> Ningún archivo está listo para subir hasta que el tutor lo revise a mano y lo confirme, uno por uno.

---

## ¿Qué hace?

Automatiza de punta a punta la auditoría y corrección de una unidad, **excepto subir al aula, que hace siempre el tutor**:

1. **Aviso y preflight**: deja claro que cada archivo se revisa a mano y verifica las dependencias.
2. **Inventario del aula** (solo lectura): qué hay en cada actividad, qué falta y qué sobra frente a la carpeta local.
3. **Fuente de verdad**: transcripciones de videos, guiones y descripción de cada actividad.
4. **Criterios únicos** (`CRITERIOS.md`) que el tutor aprueba y que comparten todos los subagentes.
5. **Piloto con una actividad**, y después **el resto en paralelo**: un **detector** (solo lectura, escribe el informe de
   hallazgos) y un **corrector** (aplica sobre una copia y entrega el archivo corregido y el registro de cambios).
6. **Verificación independiente** con scripts, sin fiarse del reporte de los subagentes.
7. **Compuerta de revisión manual**: casillero por archivo; `ORDEN_DE_SUBIDA.md` solo se genera si el tutor confirmó todo.

**Qué valida**: redacción en **tercera persona**, **tiempos verbales** homogéneos, **rastros de IA**, errores temáticos y técnicos
(contra el código real del curso), formato de **primera hoja** (materia, unidad, tema, revisor y bibliografía **APA 7**
verificada) y, si hay PDF de Gamma, **marca de agua** y texto.

**Qué no hace**: no sube nada al aula, no inventa bibliografía ni versiones, no modifica los originales.

Funciona con cualquier tipo de material de una unidad. Word y PDF de Gamma son los ejemplos: lo específico de Gamma solo se
activa si hay presentaciones de Gamma, y el Word formal es opcional (puede que la unidad ya lo traiga).

---

## Instalación

```bash
npx skills add https://github.com/JuanCruzRobledo/revision-apuntes-unidad
```

La skill queda disponible para tu agente y se carga sola cuando pedís revisar, auditar o corregir los apuntes de una unidad.

### Dependencias (la skill las verifica al empezar con `scripts/preflight.py` y te dice qué instalar)

| Qué | Para qué | Cómo |
|---|---|---|
| **Skill `tup-campus-navigator`** | Leer el aula (solo lectura) | `git clone https://github.com/Group-Active-IA/Skill-Moodle.git ~/.claude/skills/tup-campus-navigator` y `bash ~/.claude/skills/tup-campus-navigator/install.sh` (en Windows, desde Git Bash). Requiere acceso al repo. Alternativa: Claude in Chrome con tu sesión del campus abierta |
| Python 3.10+, PyMuPDF, python-docx, Pillow | Extraer, verificar y editar documentos y PDF | `pip install -r requirements.txt` |
| Microsoft Word o LibreOffice | Revisar el layout de los `.docx` (exportar a PDF) | Recomendado. Sin esto, la revisión visual del Word queda 100 % a cargo del tutor |
| youtube-transcript-api | Transcripciones de videos | Opcional (incluida en `requirements.txt`). Si YouTube bloquea, se trabaja con los guiones |
| Acceso a la web | Verificar la bibliografía | Necesario para la bibliografía; sin esto no se agregan referencias |

---

## Uso

Frases típicas:

- "Revisá los apuntes de la unidad 4 de Programación 1 en el campus y dejalos en tercera persona."
- "Auditá el material de esta unidad: Word y PDF, que no haya rastros de IA y que tengan bibliografía APA."
- "Sacale la marca de agua de Gamma a los PDF y corregí lo que esté mal."

El agente pide los datos de la unidad (materia, unidad, link del aula, carpetas, revisor, fuentes, reglas técnicas), corre el
preflight, inventaría el aula y **espera tu OK en cada compuerta**: inventario, criterios, resultado del piloto y revisión manual.
Al final te entrega `corregidos/Actividad_N/` y, **solo si confirmaste cada archivo**, `ORDEN_DE_SUBIDA.md`.

---

## Estructura

```
revision-apuntes-unidad/
├── SKILL.md                      # flujo y reglas que sigue el agente
├── README.md   LICENSE   requirements.txt   .gitignore
├── scripts/
│   ├── preflight.py              # verifica dependencias y avisa qué instalar
│   ├── extraer_docx.py           # texto del Word con párrafos numerados
│   ├── verificar_docx.py         # patrones, campo PAGE, primera hoja, metadatos
│   ├── verificar_pdf.py          # links y marca de Gamma por píxeles, patrones, cambios vs original
│   ├── transcribir_youtube.py    # transcripciones sin insistir ante bloqueo
│   ├── quitar_marca_gamma.py     # quita el badge "Made with Gamma"
│   ├── editar_pdf_texto.py       # edición de texto en PDF de Gamma (motor 1)
│   ├── gamma_editar.py           # edición de texto en PDF de Gamma (motor 2)
│   ├── comparar_pdf.py           # original vs. editada, apiladas
│   └── compuerta_revision.py     # revisión manual obligatoria y orden de subida
├── references/                   # flujo, criterios, formato, subagentes, Gamma, lecciones
└── assets/
    ├── templates/                # CRITERIOS, prompts de detector y corrector
    └── fonts/                    # fuentes OFL (con su licencia) para editar PDF de Gamma
```

---

## Por qué esta estructura

- **Dos subagentes, no uno**: el informe del detector es un contrato verificable; un corrector que también audita tiende a
  justificar lo que ya cambió.
- **Compuerta técnica y no solo una frase**: `compuerta_revision.py` guarda el hash de cada archivo; si cambia después de
  confirmarlo, la confirmación se invalida, y `orden` se niega a generar el orden de subida mientras falte algo. Los
  subagentes pueden revisar el aspecto visual en parte y los errores en imágenes no se ven por texto.
- **Verificación por píxeles** de la marca de agua: contar imágenes da falsos positivos.
- **Fuentes incluidas**: las fuentes embebidas en los PDF de Gamma son subconjuntos de glifos y no sirven para escribir texto
  nuevo; con las familias completas, el texto editado queda idéntico al original.
- **Un solo `CRITERIOS.md`** compartido: todas las actividades quedan consistentes.

---

## Licencia

Apache-2.0 (ver `LICENSE`). Las fuentes de `assets/fonts/` se distribuyen bajo la SIL Open Font License 1.1, cada una con su
aviso en `OFL-<familia>.txt` (ver `assets/fonts/FONTS.md`).
