# VNBOT Vendor Repositories

Repositorios externos clonados como **lógica base** para las capacidades del MVP de VNBOT. Cada repo se incluye como snapshot (sin `.git`) para que el código fuente esté disponible offline y pueda ser auditado, modificado o extendido según los principios de VNBOT.

## Principios de integración

1. **Adaptadores, no dependencias directas** — VNBOT no importa estos repos como librerías; los usa como referencia y los envuelve en adaptadores MCP o skills propias.
2. **MCP primero** — Cuando un repo expone una capacidad, se prefiere envolverlo en un servidor MCP interno antes que importarlo directamente en el dominio.
3. **Policy engine obligatorio** — Toda capacidad expuesta por estos repos pasa por el policy engine de VNBOT antes de ejecutarse.
4. **Defensa contra prompt injection** — Los repos de seguridad (`security/`) protegen las capacidades de los demás repos.

## Estructura

```
vendor/
├── web/                          # Scraping y navegación
│   └── firecrawl/                # mendableai/firecrawl — Scraping estructurado
├── voice/                        # Voz y audio
│   ├── pipecat/                  # pipecat-ai/pipecat — Conversación bidireccional
│   └── whisper/                  # openai/whisper — Transcripción de audio
├── video/                        # Procesamiento de video
│   └── yt-dlp/                   # yt-dlp/yt-dlp — Descarga de video/audio
├── search/                       # Búsqueda web
│   └── duckduckgo_search/        # deedy5/duckduckgo_search — Búsqueda DDG sin API key
├── embeddings/                   # Embeddings locales
│   └── sentence-transformers/    # UKPLab/sentence-transformers — Embeddings especializados
├── security/                     # Defensa contra prompt injection
│   └── rebuff/                   # protectai/rebuff — Detección de prompt injection
├── llm/                          # (reservado) Adaptadores LLM
├── loop/                         # (reservado) Loops y automatización
└── README.md                     # Este archivo
```

## Repos incluidos

### 🌐 web/firecrawl — [mendableai/firecrawl](https://github.com/mendableai/firecrawl)

**Capacidad:** Scraping web estructurado, crawling de sitios, extracción de datos limpios.

**Uso en VNBOT:** Skill `web.scrape` y `web.search_structured` para que los agentes puedan investigar URLs, extraer contenido de artículos, y construir memorias estructuradas desde fuentes web.

**Adaptador MCP previsto:** `mcp.firecrawl.scrape(url)`, `mcp.firecrawl.crawl(url, opts)`, `mcp.firecrawl.search(query)`

**Riesgo:** Medio — el contenido externo se trata como no confiable (ver `security/rebuff`).

---

### 🎙️ voice/pipecat — [pipecat-ai/pipecat](https://github.com/pipecat-ai/pipecat)

**Capacidad:** Voz en tiempo real, conversación bidireccional, pipeline TTS/STT.

**Uso en VNBOT:** Modo de conversación por voz con el agente. Permite que el usuario hable con VNBOT y este responda con voz, no solo texto.

**Adaptador MCP previsto:** `mcp.voice.start_session()`, `mcp.voice.send_audio()`, `mcp.voice.end_session()`

**Riesgo:** Bajo — audio local por defecto, cloud TTS solo con consentimiento.

---

### 🎧 voice/whisper — [openai/whisper](https://github.com/openai/whisper)

**Capacidad:** Transcripción de audio a texto de alta calidad.

**Uso en VNBOT:** Transcripción de notas de voz, transcripción de audio de videos descargados con yt-dlp, y como fallback STT cuando Pipecat no está disponible.

**Adaptador MCP previsto:** `mcp.audio.transcribe(file_ref, model='base')`

**Riesgo:** Bajo — procesamiento local, el audio se elimina después de transcribir según la política de retención.

---

### 🎬 video/yt-dlp — [yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp)

**Capacidad:** Descarga de video/audio de 1000+ plataformas (YouTube, Vimeo, Twitch, etc.).

**Uso en VNBOT:** Skill `video.download` para que el agente pueda descargar video/audio de una URL, extraer el audio, y pasarlo a Whisper para transcripción. Permite "leer" videos como contenido.

**Adaptador MCP previsto:** `mcp.video.download(url, format='audio')`, `mcp.video.extract_audio(url)`

**Riesgo:** Medio — descargar contenido con copyright. VNBOT solo permite uso personal, no redistribución. Se respeta ToS de cada plataforma.

---

### 🔍 search/duckduckgo_search — [deedy5/duckduckgo_search](https://github.com/deedy5/duckduckgo_search)

**Capacidad:** Búsqueda web vía DuckDuckGo sin requerir API key.

**Uso en VNBOT:** Skill `web.search_simple` para búsquedas rápidas. Es el buscador por defecto por no requerir credenciales y respetar privacidad.

**Adaptador MCP previsto:** `mcp.web.search(query, max_results=10)`, `mcp.web.search_news(query)`

**Riesgo:** Bajo — sin credenciales, respeta ToS de DDG, rate limiting propio.

---

### 🧠 embeddings/sentence-transformers — [UKPLab/sentence-transformers](https://github.com/UKPLab/sentence-transformers)

**Capacidad:** Embeddings locales especializados para búsqueda semántica.

**Uso en VNBOT:** Indexación semántica de memorias. Permite que la búsqueda híbrida (textual + semántica) funcione completamente offline sin enviar datos a proveedores externos.

**Adaptador MCP previsto:** `mcp.memory.embed(text)`, `mcp.memory.search_semantic(query, top_k=10)`

**Riesgo:** Bajo — procesamiento 100% local.

---

### 🛡️ security/rebuff — [protectai/rebuff](https://github.com/protectai/rebuff)

**Capacidad:** Detección de prompt injection en inputs del usuario y contenido externo.

**Uso en VNBOT:** Capa de defensa para todo contenido que entra al agente: emails, páginas web scrapedas con Firecrawl, transcripciones de Whisper, contenido de videos. Detecta intentos de inyección antes de que lleguen al LLM.

**Adaptador MCP previsto:** `mcp.security.scan_prompt(text)` → `{injection_detected: bool, confidence: float}`

**Riesgo:** Bajo — es una defensa, no una capacidad activa.

---

## Repos recomendados pero NO incluidos (instalar vía pip/cargo/npm)

Estos repos son demasiado grandes o son binarios, se instalan como dependencias en lugar de clonarse:

| Repo | Razón | Instalación |
|------|-------|-------------|
| `ollama/ollama` | Binario Go | `curl -fsSL https://ollama.com/install.sh \| sh` |
| `ggerganov/llama.cpp` | C++ muy grande | `git clone` solo si se necesita compilación local |
| `huggingface/transformers` | Muy grande, pip mejor | `pip install transformers` |
| `langchain-ai/langgraph` | Dependencia pip | `pip install langgraph` |
| `NVIDIA/NeMo-Guardrails` | Muy grande, complejo | `pip install nemoguardrails` |
| `FFmpeg/FFmpeg` | Binario | `apt install ffmpeg` / `brew install ffmpeg` |
| `chroma-core/chroma` | pip mejor | `pip install chromadb` |
| `qdrant/qdrant` | Binario Rust | Docker: `docker pull qdrant/qdrant` |

## Mantenimiento

- **Actualización:** Los snapshots se actualizan manualmente cuando hay un release significativo en el repo upstream.
- **Patches:** Cualquier modificación a un repo vendor se documenta en `vendor/PATCHES.md` (pendiente de crear).
- **Licencias:** Cada repo mantiene su licencia original. Ver `LICENSE` dentro de cada carpeta.
- **Atribución:** El README de VNBOT y el archivo `THIRD_PARTY_NOTICES.md` (pendiente) listan todos los repos incluidos.

## Próximos repos a integrar (post-MVP)

- `posthog/py-recapture` — Screenshots de páginas
- `rhasspy/wyoming-piper` — TTS local offline
- `NVIDIA/NeMo-Guardrails` — Guardrails más completos
- `meta-llama/llama-guard` — Clasificador de contenido unsafe
- `microsoft/presidio` — PII detection/redaction
- `temporalio/temporal-python` — Workflows durables para agentes autónomos
- `langchain-ai/langgraph` — State machines para loops de agentes
- `searxng/searxng` — Metabuscador self-hosteable
