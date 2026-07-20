# ADR-0010: Expanded file reader system with native program files + vision

## Estado

Propuesta (para implementación en Fase 0.5 — Memoria grafo avanzada)

## Contexto

VNBOT necesita procesar una gran variedad de archivos que un usuario puede subir o referenciar. El usuario solicitó explícitamente:

1. **Ampliar el repertorio de archivos admisibles** a 80+ extensiones
2. **Archivos nativos de programas de desarrollo** (proyectos de IDE, configs, builds)
3. **Archivos editables de editores de video** (Premiere, DaVinci, Final Cut, etc.)
4. **Archivos editables de software de ilustración** (Ibis Paint X, Clip Studio, OpenToonz, GIMP, Illustrator, Photoshop, etc.)
5. **Capacidad de visión** (VLM) para analizar imágenes dentro de documentos y entender lo que el usuario quiere encomendar

Actualmente VNBOT soporta: PDF, Word (.docx), Markdown, texto plano, imágenes (OCR), audio (Whisper), video (yt-dlp+ffmpeg), JSON/CSV/YAML/XML.

## Decisión

### 1. FileReader Registry Architecture

Implementar un registry extensible que detecta la extensión y usa el parser adecuado:

```python
# services/api/app/infrastructure/files/registry.py
FILE_READERS: dict[str, callable] = {}

def register_reader(*extensions: str):
    def decorator(func):
        for ext in extensions:
            FILE_READERS[ext.lower()] = func
        return func
    return decorator

@app.post("/api/v1/files/read")
async def read_file(file: UploadFile):
    ext = file.filename.rsplit('.', 1)[-1].lower()
    reader = FILE_READERS.get(ext)
    if not reader:
        raise HTTPException(415, f"Unsupported file type: .{ext}. Supported: {sorted(FILE_READERS.keys())}")
    content = await reader(file)
    return {"filename": file.filename, "extension": ext, "content": content.text, "metadata": content.metadata}
```

Cada reader devuelve un `FileContent` con: `text` (str), `metadata` (dict), `images` (list[bytes] para VLM).

### 2. Categorías de archivos soportados (80+ extensiones)

#### 2.1. Documentos (12 extensiones)
| Ext | Programa | Librería |
|-----|----------|----------|
| .pdf | PDF | pypdf + pdfplumber |
| .docx | Word 2007+ | python-docx |
| .doc | Word legacy | antiword (subprocess) |
| .odt | OpenDocument Text | odfpy |
| .rtf | Rich Text Format | striprtf |
| .md, .markdown | Markdown | markdown-it-py |
| .txt, .text, .log | Texto plano | nativo |
| .rst | reStructuredText | docutils |
| .adoc | AsciiDoc | asciidoctor (subprocess) |
| .org | Emacs Org Mode | org-ruby (subprocess) |
| .wiki | MediaWiki | mwparserfromhell |
| .tex | LaTeX | pylatexenc |

#### 2.2. Hojas de cálculo (4 extensiones)
| Ext | Programa | Librería |
|-----|----------|----------|
| .xlsx | Excel 2007+ | openpyxl |
| .xls | Excel legacy | xlrd |
| .ods | OpenDocument Spreadsheet | odfpy |
| .csv | CSV | nativo (csv module) |

#### 2.3. Presentaciones (2 extensiones)
| Ext | Programa | Librería |
|-----|----------|----------|
| .pptx | PowerPoint 2007+ | python-pptx |
| .ppt | PowerPoint legacy | antiword (subprocess, limitado) |

#### 2.4. Imágenes (10 extensiones)
| Ext | Programa | Librería |
|-----|----------|----------|
| .png | PNG | Pillow |
| .jpg, .jpeg | JPEG | Pillow |
| .bmp | Bitmap | Pillow |
| .tiff, .tif | TIFF | Pillow |
| .webp | WebP | Pillow |
| .gif | GIF | Pillow |
| .svg | SVG | svglib + reportlab |
| .heic, .heif | HEIC (Apple) | pillow-heif |
| .ico | Icon | Pillow |

**Para imágenes**: además de OCR (tesseract), se envía la imagen al VLM (Vision Language Model) para análisis de contenido — reconocimiento de objetos, escenas, texto, diagramas, UIs, etc.

#### 2.5. Audio (8 extensiones)
| Ext | Formato | Librería |
|-----|---------|----------|
| .mp3 | MP3 | ffmpeg → Whisper |
| .wav | WAV | Whisper nativo |
| .flac | FLAC | ffmpeg → Whisper |
| .ogg | OGG | ffmpeg → Whisper |
| .m4a | M4A | ffmpeg → Whisper |
| .aac | AAC | ffmpeg → Whisper |
| .wma | WMA | ffmpeg → Whisper |
| .opus | Opus | ffmpeg → Whisper |

#### 2.6. Video (5 extensiones)
| Ext | Formato | Librería |
|-----|---------|----------|
| .mp4 | MP4 | yt-dlp + ffmpeg (extraer audio → Whisper) |
| .avi | AVI | yt-dlp + ffmpeg |
| .mov | QuickTime | yt-dlp + ffmpeg |
| .mkv | Matroska | yt-dlp + ffmpeg |
| .webm | WebM | yt-dlp + ffmpeg |

**Para video**: se extraen keyframes (1 cada 10s) y se envían al VLM para análisis visual + transcripción de audio.

#### 2.7. E-books (4 extensiones)
| Ext | Formato | Librería |
|-----|---------|----------|
| .epub | EPUB | ebooklib |
| .mobi | Mobipocket | mobi |
| .azw3 | Kindle KF8 | calibre (subprocess) |
| .pdf | PDF (ya listado) | pypdf |

#### 2.8. Datos estructurados (10 extensiones)
| Ext | Formato | Librería |
|-----|---------|----------|
| .json | JSON | nativo |
| .yaml, .yml | YAML | PyYAML |
| .xml | XML | lxml |
| .toml | TOML | tomllib (stdlib 3.11+) |
| .ini, .cfg, .conf | INI/Config | configparser (stdlib) |
| .parquet | Parquet | pyarrow |
| .feather | Feather | pyarrow |
| .geojson | GeoJSON | json + geopandas |
| .kml | Google Earth KML | pykml |
| .kmz | Google Earth KMZ | zipfile + pykml |

#### 2.9. Código fuente (15+ extensiones)
| Ext | Lenguaje | Parser |
|-----|----------|--------|
| .py | Python | ast (stdlib) + pygments |
| .js, .mjs | JavaScript | tree-sitter-javascript |
| .ts, .tsx | TypeScript | tree-sitter-typescript |
| .jsx | JSX (React) | tree-sitter-javascript |
| .java | Java | tree-sitter-java |
| .c, .h | C | tree-sitter-c |
| .cpp, .hpp, .cc | C++ | tree-sitter-cpp |
| .go | Go | tree-sitter-go |
| .rs | Rust | tree-sitter-rust |
| .rb | Ruby | tree-sitter-ruby |
| .php | PHP | tree-sitter-php |
| .swift | Swift | tree-sitter-swift |
| .kt | Kotlin | tree-sitter-kotlin |
| .scala | Scala | tree-sitter-scala |
| .cs | C# | tree-sitter-c-sharp |
| .css, .scss, .less | CSS/SCSS/Less | texto plano + pygments |
| .html, .htm | HTML | beautifulsoup4 + lxml |
| .sql | SQL | sqlparse |
| .sh, .bash, .zsh | Shell | texto plano |
| .ps1 | PowerShell | texto plano |
| .lua | Lua | texto plano |
| .r | R | texto plano |
| .proto | Protocol Buffers | protobuf |
| .dockerfile | Dockerfile | texto plano |

**Para código**: se extrae estructura (AST), imports, funciones, clases, comentarios. No se ejecuta código (seguridad).

#### 2.10. Archivos comprimidos (5 extensiones)
| Ext | Formato | Librería |
|-----|---------|----------|
| .zip | ZIP | zipfile (stdlib) |
| .tar, .tar.gz, .tgz | Tarball | tarfile (stdlib) |
| .gz | Gzip | gzip (stdlib) |
| .7z | 7-Zip | py7zr |
| .rar | RAR | rarfile |

**Para comprimidos**: se descomprime en memoria, se lee cada archivo interno con su reader correspondiente. Límite: 100MB total, 50 archivos máximo.

#### 2.11. Archivos nativos de desarrollo (NUEVO — solicitado por usuario)

##### 2.11.1. IDE y proyectos de software
| Ext / Archivo | Programa | Método de lectura |
|---------------|----------|-------------------|
| .vscode/ (dir) | VS Code settings | JSON reader recursivo |
| .idea/ (dir) | JetBrains IntelliJ | XML reader recursivo |
| *.xcodeproj/ | Xcode project | plistlib + XML |
| .csproj, .vbproj | .NET project | XML reader |
| .sln | Visual Studio Solution | texto plano |
| Makefile, makefile | Make | texto plano |
| CMakeLists.txt | CMake | texto plano |
| Cargo.toml | Rust Cargo | TOML reader |
| go.mod, go.sum | Go modules | texto plano |
| package.json | Node.js | JSON reader |
| package-lock.json | npm lock | JSON reader |
| pnpm-lock.yaml | pnpm lock | YAML reader |
| pyproject.toml | Python project | TOML reader |
| requirements.txt | pip requirements | texto plano |
| Gemfile, Gemfile.lock | Ruby Bundler | texto plano |
| composer.json | PHP Composer | JSON reader |
| pubspec.yaml | Flutter/Dart | YAML reader |
| build.gradle, build.gradle.kts | Gradle | texto plano |
| pom.xml | Maven | XML reader |
| .env | Environment vars | texto plano (con mask de secrets) |
| Dockerfile | Docker | texto plano |
| docker-compose.yml | Docker Compose | YAML reader |
| .gitignore, .dockerignore | Ignore patterns | texto plano |
| *.ipynb | Jupyter Notebook | nbformat (celdas + outputs) |
| README.md | README | Markdown reader |

##### 2.11.2. Editores de video (proyectos editables)
| Ext | Programa | Método de lectura |
|-----|----------|-------------------|
| .prproj | Adobe Premiere Pro | XML interno (gzip) — extraer timeline, clips, efectos |
| .drp | DaVinci Resolve | Binario propietario — metadata via ffprobe |
| .fcp, .fcpbundle | Final Cut Pro | XML interno — extraer timeline |
| .veg | VEGAS Pro | Binario propietario — metadata limitada |
| .kdenlive | Kdenlive | XML (MLT format) — timeline completo |
| .osp | OpenShot | XML (MLT format) |
| .mlt | MLT framework | XML |
| .aep | After Effects | Binario propietario — metadata limitada |
| .blend (video mode) | Blender (Video Editor) | python-bpy (subprocess) |
| .vpj | VSDC | XML |
| .camproj | Camtasia | XML |
| .imovieproj | iMovie | Plist + XML |

**Estrategia para editores de video propietarios**:
- Archivos XML-based (.kdenlive, .osp, .mlt, .vpj, .camproj): parse directo
- Archivos binarios propietarios (.prproj, .drp, .fcp, .veg, .aep): extraer metadata vía ffprobe de los archivos de media referenciados. El proyecto en sí se guarda como metadata (nombre, duración, resolución, codecs).
- Para .prproj: renombrar a .gz, descomprimir, parsear XML interno
- Para .fcp: es un directorio bundle, leer info.xml dentro

##### 2.11.3. Software de ilustración y diseño (proyectos editables)
| Ext | Programa | Método de lectura |
|-----|----------|-------------------|
| .psd | Adobe Photoshop | psd-tools (capas, texto, imágenes) |
| .ai | Adobe Illustrator | PDF interno (parsear como PDF) |
| .xd | Adobe XD | ZIP con JSON interno (designspec.json) |
| .clip | Clip Studio Paint | ZIP con imágenes internas |
| .lip | Clip Studio (animación) | ZIP |
| .mdp | MediBang Paint | ZIP con XML interno |
| .ibtx | Ibis Paint X | ZIP con JSON interno |
| .kra | Krita | ZIP con maindoc.xml + imágenes |
| .xcf | GIMP | gimpformats (capas + texto) |
| .ora | OpenRaster | ZIP con XML (estándar abierto) |
| .svg | SVG (vectorial) | svglib + reportlab |
| .aseprite | Aseprite | JSON (sprite data + frames) |
| .ase | Aseprite (binario) | Python parser custom |
| .tga | TGA (gráficos) | Pillow |
| .dds | DirectDraw Surface | Pillow + imagecodecs |
| .fbx | Autodesk FBX (3D) | aspose-3d o fbx parser |
| .obj | Wavefront OBJ (3D) | trimesh |
| .glb, .gltf | glTF (3D) | trimesh |
| .blend | Blender (3D) | bpy (subprocess) |
| .sai, .sai2 | Paint Tool SAI | Binario propietario — flatten a PNG + metadata |
| .reb | Rebelle | Binario propietario — flatten a PNG |
| .procreate | Procreate (iPad) | ZIP con imágenes internas |

**Estrategia para ilustración**:
- Archivos ZIP-based (.kra, .ora, .clip, .mdp, .ibtx, .procreate, .aseprite): descomprimir, extraer imagen merged + capas como imágenes individuales, enviar al VLM
- Archivos con librería dedicada (.psd → psd-tools, .xcf → gimpformats, .ai → PDF reader): parse directo de capas + texto
- Archivos binarios propietarios (.sai, .reb): convertir a PNG via subprocess (ImageMagick si disponible) + enviar al VLM
- Archivos 3D (.obj, .glb, .gltf, .fbx): extraer metadata (vértices, materiales, texturas) + render de thumbnail via trimesh
- **Todas las imágenes extraídas se envían al VLM** para análisis de contenido

#### 2.12. Científico y técnico (8 extensiones)
| Ext | Formato | Librería |
|-----|---------|----------|
| .dcm | DICOM (médico) | pydicom |
| .fits, .fit | FITS (astronomía) | astropy |
| .h5, .hdf5 | HDF5 | h5py |
| .nc, .nc4 | NetCDF | netCDF4 |
| .shp, .shx, .dbf | Shapefile | geopandas |
| .mseed | MiniSEED (sismología) | obspy |
| .edf | European Data Format (EEG) | pyedflib |
| .parquet | Parquet (ya listado) | pyarrow |

#### 2.13. Otros (6 extensiones)
| Ext | Formato | Librería |
|-----|---------|----------|
| .sqlite, .db, .sqlite3 | SQLite database | sqlite3 (stdlib) |
| .eml | Email | email (stdlib) |
| .msg | Outlook MSG | extract-msg |
| .pst | Outlook PST | libpst (subprocess) |
| .mbox | Mbox mailbox | mailbox (stdlib) |
| .vcf | vCard | vobject |

### 3. Vision (VLM) Integration

#### 3.1. Cuándo se usa visión

1. **Imágenes dentro de documentos**: PDFs con figuras, PPTX con slides, DOCX con imágenes
2. **Archivos de ilustración**: PSD/KRA/XCF/Clip Studio — extraer capas como imágenes y analizarlas
3. **Capturas de pantalla**: el usuario sube un screenshot para que VNBOT entienda una UI o error
4. **Fotos**: el usuario toma una foto de un documento, pizarra, pantallazo, etc.
5. **Keyframes de video**: frames extraídos cada 10s del video

#### 3.2. VLM Provider

Usar **Z.AI glm-4.6v** (vision model, sin API key) como provider principal:
- Endpoint: `https://api.z.ai/v1/chat/completions`
- Model: `glm-4.6v`
- Input: imagen base64 + prompt de análisis
- Output: descripción estructurada (objetos, texto, colores, composición, contexto)

```python
async def analyze_image(image_bytes: bytes, prompt: str = "Describe esta imagen en detalle") -> str:
    """Send image to VLM for analysis."""
    b64 = base64.b64encode(image_bytes).decode()
    response = await client.post(
        "https://api.z.ai/v1/chat/completions",
        json={
            "model": "glm-4.6v",
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
                ]
            }]
        }
    )
    return response.json()["choices"][0]["message"]["content"]
```

#### 3.3. Prompts de análisis por contexto

| Contexto | Prompt |
|----------|--------|
| Documento escaneado | "Extrae todo el texto de esta imagen. Preserva la estructura." |
| UI screenshot | "Describe la interfaz de usuario. Lista los elementos visibles, botones, campos de texto, y su disposición." |
| Error/pantallazo | "¿Qué error o mensaje se muestra? Describe el problema técnico visible." |
| Ilustración/arte | "Describe la ilustración: estilo, paleta de colores, composición, elementos principales, técnica digital." |
| Diagrama | "Describe el diagrama. Identifica nodos, conexiones, flujo, y tipo (flowchart, mindmap, UML, etc.)." |
| Foto general | "Describe esta imagen en detalle: objetos, personas, escena, colores, contexto, texto visible." |
| Código en imagen | "Extrae el código fuente visible en esta imagen. Preserva indentación y formato." |

#### 3.4. Flujo de procesamiento de archivos

```
Usuario sube archivo
    ↓
FileReader Registry detecta extensión
    ↓
¿Es texto/plano? → Extraer texto directo
    ↓ No
¿Es documento compuesto? (PDF, DOCX, PPTX)
    → Extraer texto + imágenes embebidas
    → Enviar imágenes al VLM
    → Combinar texto + descripciones visuales
    ↓
¿Es archivo de ilustración? (PSD, KRA, XCF, Clip)
    → Extraer capas como imágenes
    → Enviar cada capa al VLM
    → Combinar en descripción estructurada
    ↓
¿Es video?
    → Extraer audio → Whisper (transcripción)
    → Extraer keyframes (1/10s) → VLM (descripción visual)
    → Combinar transcripción + descripciones visuales
    ↓
¿Es código fuente?
    → Parsear AST (estructura)
    → Extraer imports, funciones, clases, comentarios
    → Pygments para syntax highlighting info
    ↓
Crear MemoryNode con:
    - content: texto extraído + descripciones VLM
    - type: según tipo de archivo
    - source_type: "file_upload"
    - metadata: {filename, extension, size, mime_type, pages/layers/frames}
```

### 4. Seguridad

- **Límite de tamaño**: 50MB por archivo, 200MB total por upload
- **Límite de archivos**: 50 archivos por upload comprimido
- **Sanitización**: todo contenido extraído se trata como untrusted data (per ADR-0004)
- **No ejecución**: el código fuente se parsea pero NUNCA se ejecuta
- **Secrets masking**: archivos .env se leen pero los valores se maskan (`***`) antes de guardar como memoria
- **Timeout**: 30s por archivo, 5min por upload completo
- **VLM rate limit**: máximo 20 imágenes por archivo (las adicionales se agrupan)

### 5. Endpoints

```
POST   /api/v1/files/read          — leer archivo (subir + procesar)
POST   /api/v1/files/read-url       — leer archivo desde URL
GET    /api/v1/files/supported      — listar extensiones soportadas
POST   /api/v1/files/analyze-image  — analizar imagen con VLM (directo)
```

### 6. Dependencias a instalar

```toml
# Esfuerzo bajo (instalar y usar)
openpyxl = ">=3.1"           # Excel
xlrd = ">=2.0"               # Excel legacy
odfpy = ">=1.4"              # OpenDocument
striprtf = ">=0.0.22"        # RTF
python-pptx = ">=0.6"        # PowerPoint
ebooklib = ">=0.18"          # EPUB
beautifulsoup4 = ">=4.12"    # HTML
lxml = ">=5.0"               # XML/HTML parser
pillow-heif = ">=0.15"       # HEIC
nbformat = ">=5.9"           # Jupyter
pyarrow = ">=15.0"           # Parquet/Feather
tomli = ">=2.0"              # TOML (Python <3.11)
psd-tools = ">=1.9"          # Photoshop PSD
gimpformats = ">=0.4"        # GIMP XCF
svglib = ">=1.5"             # SVG
reportlab = ">=4.0"          # SVG → PDF (para svglib)
sqlparse = ">=0.5"           # SQL
py7zr = ">=0.20"             # 7-Zip
rarfile = ">=4.1"            # RAR
extract-msg = ">=0.48"       # Outlook MSG
vobject = ">=0.9"            # vCard
docutils = ">=0.20"          # reStructuredText
pylatexenc = ">=2.10"        # LaTeX
trimesh = ">=4.0"            # 3D (OBJ, glTF)
imagecodecs = ">=2024.1"     # DDS

# Esfuerzo medio
tree-sitter = ">=0.22"       # Code parsing (multi-language)
tree-sitter-languages = ">=1.10"
geopandas = ">=0.14"         # GeoJSON/Shapefile
pykml = ">=0.2"              # KML
h5py = ">=3.10"              # HDF5
netCDF4 = ">=1.6"            # NetCDF
astropy = ">=6.0"            # FITS
pydicom = ">=2.4"            # DICOM
mobi = ">=0.3"               # MOBI e-books

# Esfuerzo alto (subprocess o especializado)
# calibre (ebook-convert)    # AZW3
# ImageMagick (convert)      # SAI, Rebelle flatten
# Blender (bpy)              # .blend files
# antiword                   # .doc legacy
# asciidoctor                # AsciiDoc
```

## Consecuencias

- **Positivas**:
  - VNBOT puede procesar prácticamente cualquier archivo que un usuario encuentre en su día a día
  - La visión (VLM) permite entender imágenes, screenshots, ilustraciones, diagramas
  - Archivos de editores de video e ilustración se procesan para extraer metadata + contenido visual
  - El registry es extensible: añadir un nuevo formato es solo registrar un reader
  - Compatible con el ecosistema Hermes (agentskills.io) — el file reader puede ser una skill
- **Negativas**:
  - Muchas dependencias nuevas (~25 paquetes Python)
  - Algunas requieren binarios del sistema (ImageMagick, Blender, calibre, antiword)
  - El VLM tiene coste de API (aunque Z.AI es sin API key, tiene rate limit de 30 RPM)
  - Archivos propietarios binarios (.sai, .veg, .aep) pueden no parsearse completamente
- **Riesgos**:
  - Dependencias pesadas pueden aumentar el tiempo de build de Docker
  - Archivos maliciosos (zip bombs, imágenes enormes) → mitigar con límites de tamaño + timeout
  - VLM puede alucinar contenido no presente → mitigar con prompt engineering + confidence scoring

## Alternativas consideradas

1. **Solo texto (sin visión)** — rechazada; el usuario quiere que VNBOT "observe" imágenes
2. **Usar un servicio externo (Google Vision, AWS Textract)** — rechazada por costo y dependencia
3. **Solo librerías Python puras (sin subprocess)** — rechazada; algunos formatos requieren binarios
4. **No soportar formatos propietarios** — rechazada; el usuario pidió explícitamente editores de video e ilustración

## Implementación

### Fase 0.5 — Sprint 1 (core readers)
- [ ] FileReader registry + endpoint `/files/read`
- [ ] Readers de esfuerzo bajo: Excel, PPTX, ODT, RTF, HTML, EPUB, Jupyter, TOML, INI
- [ ] VLM integration con Z.AI glm-4.6v
- [ ] Endpoint `/files/analyze-image`

### Fase 0.5 — Sprint 2 (ilustración + video)
- [ ] PSD reader (psd-tools)
- [ ] KRA/ORA reader (ZIP-based)
- [ ] XCF reader (gimpformats)
- [ ] Clip Studio / Ibis Paint X / Procreate readers (ZIP-based)
- [ ] Video keyframe extraction + VLM
- [ ] SVG reader

### Fase 0.5 — Sprint 3 (código + científico + nativos)
- [ ] Tree-sitter integration para código fuente
- [ ] ZIP/TAR/7Z/RAR decompress + recursive read
- [ ] GeoJSON/Shapefile/KML readers
- [ ] DICOM/FITS/HDF5/NetCDF readers
- [ ] Proyectos de IDE (.vscode, .idea, package.json, etc.)
- [ ] Proyectos de editores de video (XML-based: .kdenlive, .mlt, .fcp)

### Post-1.0 (formatos propietarios avanzados)
- [ ] Premiere Pro .prproj (gzip + XML)
- [ ] DaVinci Resolve .drp (metadata via ffprobe)
- [ ] After Effects .aep (metadata limitada)
- [ ] Blender .blend (bpy subprocess)
- [ ] 3D formats (.fbx via aspose-3d)
- [ ] SAI/Rebelle (ImageMagick flatten)

## Referencias

- docs/07-MODELO-DATOS-VNBOT.md: FileAsset, Document, AudioAsset entities
- docs/08-SEGURIDAD-Y-PRIVACIDAD-VNBOT.md §11: contenido externo tratado como untrusted
- docs/09-MCP-Y-SKILLS-VNBOT.md: web.fetch skill (Firecrawl)
- vendor/voice/whisper: transcripción de audio
- vendor/video/yt-dlp: descarga/procesamiento de video
- ADR-0004: MCP is protocol, not authorization
- ADR-0007: Mandatory heuristic fallback (si VLM no disponible, solo OCR)
- ADR-0009: Hermes Agent methodology (file reader como skill agentskills.io)
- Z.AI Vision API: https://api.z.ai/v1/chat/completions (model: glm-4.6v)
