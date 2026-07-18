# VNBOT Skills Catalog

Catálogo de skills planificadas para VNBOT, organizadas por categoría. Cada skill se documenta con: nombre, descripción, repos de referencia, riesgo y autonomía requerida.

**Principios de skills en VNBOT:**
- Cada skill es una capacidad versionada con manifest YAML (ver [docs/09-MCP-Y-SKILLS-VNBOT.md](../docs/09-MCP-Y-SKILLS-VNBOT.md))
- Las skills no ejecutan código arbitrario, declaran herramientas necesarias
- El policy engine decide si una skill puede ejecutarse, no la skill misma
- Las skills comunitarias deben pasar security review antes de habilitarse

## Estructura

```
skills/
├── README.md                     # Este catálogo
├── ciencias/                     # Skills científicas y matemáticas
├── planificacion/                # Skills de planificación y productividad
├── trading/                      # Skills de análisis financiero
├── documentos/                   # Skills de procesamiento de documentos
├── storytelling/                 # Skills de narrativa y escritura creativa
├── ideacion/                     # Skills de lluvia de ideas y creatividad
├── analisis/                     # Skills de análisis profundo
└── referencia/                   # Skills de referencia y lookup
```

---

## 🧪 ciencias/ — Skills científicas y matemáticas

### `science.math.solve`
**Descripción:** Resolución de problemas matemáticos simbólicos y numéricos.
**Repos de referencia:**
- [sympy/sympy](https://github.com/sympy/sympy) — Álgebra computacional
- [scipy/scipy](https://github.com/scipy/scipy) — Cálculo numérico
- [numpy/numpy](https://github.com/numpy/numpy) — Arrays y operaciones
**Riesgo:** Bajo · **Autonomía:** 2 (internal_actions)

### `science.physics.calculate`
**Descripción:** Cálculos de física (mecánica, electromagnetismo, termodinámica).
**Repos de referencia:**
- [pydy/pydy](https://github.com/pydy/pydy) — Dinámica multibody
- [scipy/scipy](https://github.com/scipy/scipy) — Constantes físicas
**Riesgo:** Bajo · **Autonomía:** 2

### `science.chemistry.lookup`
**Descripción:** Lookup de propiedades químicas, balanceo de ecuaciones.
**Repos de referencia:**
- [mcs07/MolVS](https://github.com/mcs07/MolVS) — Validación de moléculas
- [openbabel/openbabel](https://github.com/openbabel/openbabel) — Química computacional
**Riesgo:** Bajo · **Autonomía:** 1 (propose)

### `science.units.convert`
**Descripción:** Conversión de unidades (SI, imperiales, etc.).
**Repos de referencia:**
- [hgrecco/pint](https://github.com/hgrecco/pint) — Manejo de unidades físicas
**Riesgo:** Bajo · **Autonomía:** 0 (answer_only)

### `science.statistics.analyze`
**Descripción:** Análisis estadístico descriptivo e inferencial.
**Repos de referencia:**
- [statsmodels/statsmodels](https://github.com/statsmodels/statsmodels) — Modelos estadísticos
- [pandas-dev/pandas](https://github.com/pandas-dev/pandas) — Dataframes
**Riesgo:** Bajo · **Autonomía:** 2

---

## 📅 planificacion/ — Skills de planificación y productividad

### `planning.schedule.optimize`
**Descripción:** Optimización de horarios considerando prioridades, deadlines y ventanas de silencio.
**Repos de referencia:**
- [AIM-OD/interval-basic](https://github.com/AIM-OD/interval-basic) — Manejo de intervalos
- [schedule-org/schedule](https://github.com/schedule-org/schedule) — Job scheduling
**Riesgo:** Medio · **Autonomía:** 2

### `planning.task.breakdown`
**Descripción:** Descompone una tarea grande en sub-tareas accionables.
**Repos de referencia:**
- [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) — Testing de prompts
- [microsoft/autogen](https://github.com/microsoft/autogen) — Referencia de descomposición
**Riesgo:** Bajo · **Autonomía:** 1

### `planning.goal.track`
**Descripción:** Tracking de objetivos de largo plazo con milestones.
**Repos de referencia:**
- [Engineering-Managers-Reading-List/emrl](https://github.com/Engineering-Managers-Reading-List/emrl) — Referencia OKRs
**Riesgo:** Bajo · **Autonomía:** 2

### `planning.decision.support`
**Descripción:** Ayuda a tomar decisiones estructuradas (pros/contras, matriz de decisión, SWOT).
**Repos de referencia:**
- [arbox/nlp-with-python](https://github.com/arbox/nlp-with-python) — Referencia NLP
- Implementación propia con LLM + structured output
**Riesgo:** Medio · **Autonomía:** 1

### `planning.pomodoro.run`
**Descripción:** Ejecuta ciclos pomodoro con notificaciones y tracking.
**Repos de referencia:**
- Implementación nativa en scheduler de VNBOT
**Riesgo:** Bajo · **Autonomía:** 3 (external_confirmed)

---

## 💹 trading/ — Skills de análisis financiero (solo análisis, NO ejecución)

### `trading.market.lookup`
**Descripción:** Lookup de precios actuales y datos históricos de mercados.
**Repos de referencia:**
- [ranaroussi/yfinance](https://github.com/ranaroussi/yfinance) — Yahoo Finance API
- [ccxt/ccxt](https://github.com/ccxt/ccxt) — Exchange de cripto unificado
**Riesgo:** Medio · **Autonomía:** 0 (answer_only, read-only)

### `trading.technical.analyze`
**Descripción:** Análisis técnico de gráficos (RSI, MACD, medias móviles).
**Repos de referencia:**
- [twopirllc/pandas-ta](https://github.com/twopirllc/pandas-ta) — Indicadores técnicos
- [mrdbourke/tensorflow-action-trading](https://github.com/mrdbourke/tensorflow-action-trading) — Referencia ML trading
**Riesgo:** Alto · **Autonomía:** 0

### `trading.portfolio.track`
**Descripción:** Tracking de portfolio con cálculos de P&L.
**Repos de referencia:**
- [quantopian/zipline](https://github.com/quantopian/zipline) — Backtesting
- [pmorissette/bt](https://github.com/pmorissette/bt) — Strategy testing
**Riesgo:** Medio · **Autonomía:** 0

### `trading.news.aggregate`
**Descripción:** Agregación de noticias financieras relevantes para activos seguidos.
**Repos de referencia:**
- [deedy5/duckduckgo_search](https://github.com/deedy5/duckduckgo_search) — Búsqueda
- [firecrawl/firecrawl](https://github.com/mendableai/firecrawl) — Scraping
**Riesgo:** Bajo · **Autonomía:** 0

> **⚠️ IMPORTANTE:** VNBOT NO ejecuta trades. El PRD prohíbe explícitamente operaciones financieras en el MVP. Estas skills son solo de análisis e información.

---

## 📄 documentos/ — Skills de procesamiento de documentos

### `doc.pdf.extract`
**Descripción:** Extracción de texto, tablas y metadata de PDFs.
**Repos de referencia:**
- [py-pdf/pypdf](https://github.com/py-pdf/pypdf) — Manipulación PDF pura Python
- [py-pdf/pdfplumber](https://github.com/py-pdf/pdfplumber) — Extracción de tablas
- [pdfminer/pdfminer.six](https://github.com/pdfminer/pdfminer.six) — Parsing robusto
**Riesgo:** Bajo · **Autonomía:** 2

### `doc.pdf.summarize`
**Descripción:** Resumen de PDFs largos (papers, contratos, reportes).
**Repos de referencia:**
- [huggingface/transformers](https://github.com/huggingface/transformers) — Modelos de resumen
- LLM Router propio
**Riesgo:** Medio · **Autonomía:** 1

### `doc.ocr.scan`
**Descripción:** OCR de imágenes escaneadas o fotos de documentos.
**Repos de referencia:**
- [naptha/tesseract.js](https://github.com/naptha/tesseract.js) — OCR en JS
- [madmaze/pytesseract](https://github.com/madmaze/pytesseract) — Wrapper Python Tesseract
- [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) — OCR multilenguaje
**Riesgo:** Medio · **Autonomía:** 2

### `doc.word.parse`
**Descripción:** Parsing y edición de .docx.
**Repos de referencia:**
- [python-openxml/python-docx](https://github.com/python-openxml/python-docx) — Manipulación .docx
**Riesgo:** Bajo · **Autonomía:** 2

### `doc.markdown.render`
**Descripción:** Renderizado de Markdown a HTML/PDF con templates.
**Repos de referencia:**
- [executablebooks/markdown-it-py](https://github.com/executablebooks/markdown-it-py) — Parser Markdown
- [Python-Markdown/markdown](https://github.com/Python-Markdown/markdown) — Markdown a HTML
**Riesgo:** Bajo · **Autonomía:** 2

### `doc.translate`
**Descripción:** Traducción de documentos preservando formato.
**Repos de referencia:**
- [argosopentech/argos-translate](https://github.com/argosopentech/argos-translate) — Traducción local
- [deep-translator/deep-translator](https://github.com/nidhaloff/deep-translator) — Multi-provider
**Riesgo:** Medio · **Autonomía:** 2

---

## 📖 storytelling/ — Skills de narrativa y escritura creativa

### `story.plot.generate`
**Descripción:** Generación de plots narrativos con estructura (3 actos, viaje del héroe).
**Repos de referencia:**
- LLM Router con prompts especializados
- [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) — Testing de prompts
**Riesgo:** Bajo · **Autonomía:** 1

### `story.character.develop`
**Descripción:** Desarrollo de personajes con arcos, motivaciones y voz.
**Repos de referencia:**
- Implementación propia con LLM + structured output
**Riesgo:** Bajo · **Autonomía:** 1

### `story.continue`
**Descripción:** Continúa una historia existente manteniendo coherencia con el contexto.
**Repos de referencia:**
- LLM Router con contexto largo
- Memoria de VNBOT para persistir story bible
**Riesgo:** Bajo · **Autonomía:** 1

### `story.dialogue.write`
**Descripción:** Escritura de diálogos con voces distintivas por personaje.
**Repos de referencia:**
- LLM Router con few-shot prompting
**Riesgo:** Bajo · **Autonomía:** 1

### `story.outline.structure`
**Descripción:** Estructura outlines (beat sheets, sinopsis, tratamientos).
**Repos de referencia:**
- [ saveriorempi/foxtrails-studio-encoder](https://github.com/saveriorempi/foxtrails-studio-encoder) — Referencia estructura
**Riesgo:** Bajo · **Autonomía:** 1

---

## 💡 ideacion/ — Skills de lluvia de ideas y creatividad

### `idea.brainstorm.divergent`
**Descripción:** Brainstorming divergente (cantidad > calidad en primera iteración).
**Repos de referencia:**
- LLM Router con temperature alta
- Implementación propia con técnicas de creatividad (SCAMPER, etc.)
**Riesgo:** Bajo · **Autonomía:** 1

### `idea.brainstorm.convergent`
**Descripción:** Convergencia y agrupación de ideas generadas.
**Repos de referencia:**
- [UKPLab/sentence-transformers](https://github.com/UKPLab/sentence-transformers) — Clustering semántico
- [scikit-learn/sklearn](https://github.com/scikit-learn/scikit) — K-means, DBSCAN
**Riesgo:** Bajo · **Autonomía:** 2

### `idea.mindmap.generate`
**Descripción:** Generación de mapas mentales desde un tema central.
**Repos de referencia:**
- Implementación propia + LLM
- Render con [mermaid-js/mermaid](https://github.com/mermaid-js/mermaid)
**Riesgo:** Bajo · **Autonomía:** 1

### `idea.analogy.find`
**Descripción:** Búsqueda de analogías cross-domain para explicar conceptos.
**Repos de referencia:**
- LLM Router con prompting especializado
- Memoria para persistir analogías exitosas
**Riesgo:** Bajo · **Autonomía:** 1

### `idea.scamper.apply`
**Descripción:** Aplica técnica SCAMPER (Sustituir, Combinar, Adaptar, Modificar, Proponer, Eliminar, Reordenar).
**Repos de referencia:**
- Implementación propia con prompts estructurados
**Riesgo:** Bajo · **Autonomía:** 1

---

## 🔍 analisis/ — Skills de análisis profundo

### `analysis.document.deep`
**Descripción:** Análisis profundo de un documento (argumentos, falacias, sesgos).
**Repos de referencia:**
- LLM Router con chain-of-thought
- [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) — Validación de outputs
**Riesgo:** Medio · **Autonomía:** 1

### `analysis.sentiment.run`
**Descripción:** Análisis de sentimiento de texto (positivo/negativo/neutral + emociones).
**Repos de referencia:**
- [huggingface/transformers](https://github.com/huggingface/transformers) — Modelos pre-entrenados
- [Liebeck/TextalyticsAPI](https://github.com/Liebeck/TextalyticsAPI) — Referencia
**Riesgo:** Bajo · **Autonomía:** 2

### `analysis.network.graph`
**Descripción:** Análisis de redes y grafos (centralidad, comunidades, caminos).
**Repos de referencia:**
- [networkx/networkx](https://github.com/networkx/networkx) — Análisis de grafos
- [igraph/python-igraph](https://github.com/igraph/python-igraph) — Performance
**Riesgo:** Bajo · **Autonomía:** 2

### `analysis.trend.detect`
**Descripción:** Detección de tendencias en series temporales.
**Repos de referencia:**
- [facebook/prophet](https://github.com/facebook/prophet) — Forecasting
- [unit8co/darts](https://github.com/unit8co/darts) — Time series
**Riesgo:** Medio · **Autonomía:** 2

### `analysis.comparative.run`
**Descripción:** Análisis comparativo de dos o más opciones/documents/datasets.
**Repos de referencia:**
- LLM Router con structured output
- [diff-match-patch/diff-match-patch](https://github.com/diff-match-patch/diff-match-patch) — Diffing
**Riesgo:** Medio · **Autonomía:** 1

### `analysis.risk.assess`
**Descripción:** Evaluación de riesgos de una decisión o proyecto.
**Repos de referencia:**
- Implementación propia con frameworks (FMEA, SWOT, PESTLE)
- LLM Router para structured output
**Riesgo:** Alto · **Autonomía:** 1

---

## 📚 referencia/ — Skills de referencia y lookup

### `ref.wikipedia.lookup`
**Descripción:** Lookup de artículos de Wikipedia con resumen.
**Repos de referencia:**
- [goldsmith/Wikipedia](https://github.com/goldsmith/Wikipedia) — API Python
**Riesgo:** Bajo · **Autonomía:** 0

### `ref.dictionary.define`
**Descripción:** Definiciones de palabras, sinónimos, antónimos.
**Repos de referencia:**
- [wordnik/wordnik-python](https://github.com/wordnik/wordnik-python) — API
- [dwyl/english-words](https://github.com/dwyl/english-words) — Dataset offline
**Riesgo:** Bajo · **Autonomía:** 0

### `ref.currency.convert`
**Descripción:** Conversión de monedas con tasas actuales.
**Repos de referencia:**
- [exchangerate-api/exchangerate-api-python](https://github.com/exchangerate-api/exchangerate-api-python)
**Riesgo:** Bajo · **Autonomía:** 0

### `ref.timezone.convert`
**Descripción:** Conversión de zonas horarias.
**Repos de referencia:**
- [pganssle/pytz](https://github.com/pganssle/pytz) — Timezone database
- [mborsetti/zoneinfo](https://github.com/mborsetti/zoneinfo) — Alternativa
**Riesgo:** Bajo · **Autonomía:** 0

### `ref.code.snippet`
**Descripción:** Búsqueda de snippets de código por lenguaje y tarea.
**Repos de referencia:**
- [github/CodeSearchNet](https://github.com/github/CodeSearchNet) — Dataset
- LLM Router para generación
**Riesgo:** Bajo · **Autonomía:** 0

### `ref.recipe.find`
**Descripción:** Búsqueda de recetas por ingredientes.
**Repos de referencia:**
- [hhursev/recipe-scrapers](https://github.com/hhursev/recipe-scrapers) — Scraping de recetas
- [TheMealDB/TheMealDB](https://github.com/TheMealDB/TheMealDB) — API
**Riesgo:** Bajo · **Autonomía:** 0

---

## Skills futuras (post-MVP)

### `code.review` (post-MVP, requiere cuidados especiales)
**Descripción:** Review de código con sugerencias.
**Repos de referencia:**
- [microsoft/pyright](https://github.com/microsoft/pyright) — Type checking
- [tree-sitter/tree-sitter](https://github.com/tree-sitter/tree-sitter) — Parsing universal
**Riesgo:** Alto · **Autonomía:** 1
**Nota:** El usuario solicitó que NO haya creación de código, pero sí análisis/lectura.

### `video.summarize` (post-MVP)
**Descripción:** Resumen de videos usando transcripción + análisis.
**Repos de referencia:**
- vendor/video/yt-dlp + vendor/voice/whisper + LLM
**Riesgo:** Medio · **Autonomía:** 2

### `audio.podcast.summarize` (post-MVP)
**Descripción:** Resumen de podcasts.
**Repos de referencia:**
- vendor/voice/whisper + LLM
**Riesgo:** Medio · **Autonomía:** 2

---

## Estadísticas del catálogo

- **Total skills planificadas:** 38
- **Por riesgo:**
  - Bajo: 22
  - Medio: 12
  - Alto: 4
- **Por autonomía:**
  - 0 (answer_only): 9
  - 1 (propose): 16
  - 2 (internal_actions): 11
  - 3 (external_confirmed): 1
  - 4 (bounded_automation): 0 (no en MVP)
- **Por categoría:**
  - ciencias: 5
  - planificacion: 5
  - trading: 4
  - documentos: 6
  - storytelling: 5
  - ideacion: 5
  - analisis: 6
  - referencia: 6

## Implementación

Las skills se implementarán siguiendo el orden del [Plan de Implementación](../docs/04-PLAN-IMPLEMENTACION-VNBOT.md):

- **Fase 0.7 (Skills y agentes):** Skills iniciales listadas en docs/09 — `memory.save`, `reminder.create`, `list.manage`, `briefing.daily`, `graph.explore`, `mcp.connect`
- **Fase 0.8 (Integraciones):** Skills de `referencia/` y `documentos/`
- **Fase 0.9 (Estabilización):** Skills de `analisis/` y `planificacion/`
- **Post-1.0:** Skills de `trading/`, `storytelling/`, `ideacion/`, `ciencias/`

Cada skill requiere:
1. Manifest YAML (ver [docs/09-MCP-Y-SKILLS-VNBOT.md §13.2](../docs/09-MCP-Y-SKILLS-VNBOT.md))
2. Input/output JSON Schema
3. Tests unitarios
4. Simulación
5. Aprobación de security review si riesgo ≥ medio
