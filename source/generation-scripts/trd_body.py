#!/usr/bin/env python3
"""
VNBOT TRD — Body PDF generator (ReportLab)
Genera el cuerpo del TRD con TOC, todas las secciones, tablas, bloques de código y contenido rico.
"""
import sys, os, hashlib
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, Image, Flowable, HRFlowable, Preformatted
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# ===== Font registration =====
FONT_DIR = '/usr/share/fonts'
pdfmetrics.registerFont(TTFont('NotoSerifSC', f'{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Regular.ttf'))
pdfmetrics.registerFont(TTFont('NotoSerifSC-Bold', f'{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Bold.ttf'))
registerFontFamily('NotoSerifSC', normal='NotoSerifSC', bold='NotoSerifSC-Bold')

pdfmetrics.registerFont(TTFont('NotoSansSC', f'{FONT_DIR}/truetype/chinese/SarasaMonoSC-SemiBold.ttf'))
pdfmetrics.registerFont(TTFont('NotoSansSC-Bold', f'{FONT_DIR}/truetype/chinese/SarasaMonoSC-Bold.ttf'))
registerFontFamily('NotoSansSC', normal='NotoSansSC', bold='NotoSansSC-Bold')

pdfmetrics.registerFont(TTFont('Mono', f'{FONT_DIR}/truetype/dejavu/DejaVuSansMono.ttf'))
pdfmetrics.registerFont(TTFont('Mono-Bold', f'{FONT_DIR}/truetype/dejavu/DejaVuSansMono-Bold.ttf'))
registerFontFamily('Mono', normal='Mono', bold='Mono-Bold')

# ===== Palette (minimal mode, auto-generated for TRD) =====
PAGE_BG       = colors.HexColor('#FFFFFF')
SECTION_BG    = colors.HexColor('#eff1f1')
CARD_BG       = colors.HexColor('#f4f6f7')
TABLE_STRIPE  = colors.HexColor('#edeff0')
HEADER_FILL   = colors.HexColor('#1F2937')  # VNBOT dark navy
COVER_BLOCK   = colors.HexColor('#3f5864')
BORDER        = colors.HexColor('#b3bfc6')
ICON          = colors.HexColor('#346983')
ACCENT        = colors.HexColor('#0E7490')  # darker cyan for print
ACCENT_2      = colors.HexColor('#7152cb')
TEXT_PRIMARY  = colors.HexColor('#111827')
TEXT_MUTED    = colors.HexColor('#6B7280')
SEM_SUCCESS   = colors.HexColor('#047857')
SEM_WARNING   = colors.HexColor('#B45309')
SEM_ERROR     = colors.HexColor('#B91C1C')
SEM_INFO      = colors.HexColor('#4e769e')

CODE_BG       = colors.HexColor('#0F172A')
CODE_TEXT     = colors.HexColor('#E5F1FF')
CODE_COMMENT  = colors.HexColor('#64748B')
CODE_KEYWORD  = colors.HexColor('#22D3EE')

# ===== Styles =====
styles = getSampleStyleSheet()

style_h1 = ParagraphStyle('H1', parent=styles['Heading1'],
    fontName='NotoSansSC-Bold', fontSize=22, leading=28,
    textColor=HEADER_FILL, spaceBefore=18, spaceAfter=14,
    keepWithNext=True, alignment=TA_LEFT)

style_h2 = ParagraphStyle('H2', parent=styles['Heading2'],
    fontName='NotoSansSC-Bold', fontSize=15, leading=21,
    textColor=ACCENT, spaceBefore=14, spaceAfter=10,
    keepWithNext=True, alignment=TA_LEFT)

style_h3 = ParagraphStyle('H3', parent=styles['Heading3'],
    fontName='NotoSansSC-Bold', fontSize=12, leading=17,
    textColor=TEXT_PRIMARY, spaceBefore=10, spaceAfter=6,
    keepWithNext=True, alignment=TA_LEFT)

style_body = ParagraphStyle('Body', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=10.5, leading=16,
    textColor=TEXT_PRIMARY, spaceBefore=0, spaceAfter=8,
    alignment=TA_JUSTIFY, firstLineIndent=0)

style_body_left = ParagraphStyle('BodyLeft', parent=style_body,
    alignment=TA_LEFT)

style_bullet = ParagraphStyle('Bullet', parent=style_body,
    leftIndent=20, bulletIndent=8, spaceAfter=4, alignment=TA_LEFT,
    bulletFontName='NotoSerifSC', bulletFontSize=10.5)

style_quote = ParagraphStyle('Quote', parent=style_body,
    fontName='NotoSerifSC', fontSize=11, leading=17,
    textColor=TEXT_PRIMARY, leftIndent=24, rightIndent=24,
    spaceBefore=10, spaceAfter=10, alignment=TA_LEFT,
    backColor=CARD_BG)

style_code = ParagraphStyle('Code', parent=styles['Code'],
    fontName='Mono', fontSize=8.5, leading=12,
    textColor=CODE_TEXT, backColor=CODE_BG,
    leftIndent=12, rightIndent=12, spaceBefore=6, spaceAfter=6,
    borderColor=HEADER_FILL, borderWidth=0, borderPadding=10,
    alignment=TA_LEFT)

style_table_header = ParagraphStyle('TableHeader',
    fontName='NotoSansSC-Bold', fontSize=9, leading=12,
    textColor=colors.white, alignment=TA_LEFT)

style_table_cell = ParagraphStyle('TableCell',
    fontName='NotoSerifSC', fontSize=9, leading=12,
    textColor=TEXT_PRIMARY, alignment=TA_LEFT)

style_table_cell_mono = ParagraphStyle('TableCellMono',
    fontName='Mono', fontSize=8.5, leading=12,
    textColor=ACCENT, alignment=TA_LEFT)

style_toc_title = ParagraphStyle('TocTitle',
    fontName='NotoSansSC-Bold', fontSize=20, leading=26,
    textColor=HEADER_FILL, spaceAfter=18, alignment=TA_LEFT)

toc_level0 = ParagraphStyle('TocL0',
    fontName='NotoSansSC-Bold', fontSize=11, leading=18,
    textColor=TEXT_PRIMARY, leftIndent=0, spaceBefore=4, spaceAfter=2)

toc_level1 = ParagraphStyle('TocL1',
    fontName='NotoSerifSC', fontSize=10, leading=16,
    textColor=TEXT_MUTED, leftIndent=18, spaceBefore=2, spaceAfter=2)

# ===== TocDocTemplate =====
class TocDocTemplate(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if hasattr(flowable, 'bookmark_name'):
            level = getattr(flowable, 'bookmark_level', 0)
            text = getattr(flowable, 'bookmark_text', '')
            key = getattr(flowable, 'bookmark_key', '')
            self.notify('TOCEntry', (level, text, self.page, key))

def add_heading(text, style, level=0, story=None):
    key = f'h_{hashlib.md5(text.encode()).hexdigest()[:8]}'
    p = Paragraph(f'<a name="{key}"/>{text}', style)
    p.bookmark_name = key
    p.bookmark_level = level
    p.bookmark_text = text
    p.bookmark_key = key
    if story is not None:
        story.append(p)
    return p

# ===== Helpers =====
def p(text, style=None):
    return Paragraph(text, style or style_body)

def bullet_list(items, style=None):
    s = style or style_bullet
    return [Paragraph(item, s, bulletText='•') for item in items]

def numbered_list(items, style=None):
    s = style or style_body_left
    return [Paragraph(f'<b>{i:02d}.</b> {item}', s) for i, item in enumerate(items, 1)]

def make_table(data, col_widths=None, header=True):
    if col_widths is None:
        col_widths = [None] * len(data[0])
    wrapped = []
    for i, row in enumerate(data):
        wrapped_row = []
        for j, cell in enumerate(row):
            if isinstance(cell, Paragraph) or isinstance(cell, Flowable):
                wrapped_row.append(cell)
            else:
                text = str(cell)
                if i == 0 and header:
                    wrapped_row.append(Paragraph(text, style_table_header))
                else:
                    if j == 0 and text and (text[0].isupper() and '-' in text):
                        wrapped_row.append(Paragraph(text, style_table_cell_mono))
                    else:
                        wrapped_row.append(Paragraph(text, style_table_cell))
        wrapped.append(wrapped_row)

    t = Table(wrapped, colWidths=col_widths, repeatRows=1 if header else 0)
    style_cmds = [
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('GRID', (0,0), (-1,-1), 0.4, BORDER),
    ]
    if header:
        style_cmds.extend([
            ('BACKGROUND', (0,0), (-1,0), HEADER_FILL),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'NotoSansSC-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('TOPPADDING', (0,0), (-1,0), 7),
            ('BOTTOMPADDING', (0,0), (-1,0), 7),
        ])
        for i in range(1, len(data)):
            if i % 2 == 0:
                style_cmds.append(('BACKGROUND', (0,i), (-1,i), TABLE_ROW_ODD if False else TABLE_STRIPE))
    t.setStyle(TableStyle(style_cmds))
    return t

def callout(text, color=None):
    bg = CARD_BG
    border_color = color or ACCENT
    para = Paragraph(text, ParagraphStyle('Callout',
        fontName='NotoSerifSC', fontSize=10.5, leading=15,
        textColor=TEXT_PRIMARY, alignment=TA_LEFT))
    t = Table([[para]], colWidths=[170*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg),
        ('LINEBEFORE', (0,0), (0,-1), 3, border_color),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    return t

def code_block(code_text):
    """Render a code block with dark background and monospace font."""
    # Escape HTML special chars
    escaped = code_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # Preserve whitespace with <br/> and &nbsp;
    lines = escaped.split('\n')
    html_lines = []
    for line in lines:
        if not line.strip():
            html_lines.append('&nbsp;')
        else:
            # Replace leading spaces with &nbsp;
            stripped = line.lstrip(' ')
            leading = len(line) - len(stripped)
            html_lines.append('&nbsp;' * leading + stripped)
    html = '<br/>'.join(html_lines)
    return Preformatted(html, style_code)

# ===== Page decoration =====
def page_decoration(canv, doc):
    canv.saveState()
    canv.setFont('Mono', 8)
    canv.setFillColor(TEXT_MUTED)
    page_num = canv.getPageNumber()
    canv.drawString(20*mm, 12*mm, 'VNBOT // TRD v1.0.0-draft')
    canv.drawRightString(190*mm, 12*mm, f'{page_num}')
    canv.setStrokeColor(BORDER)
    canv.setLineWidth(0.4)
    canv.line(20*mm, 15*mm, 190*mm, 15*mm)
    if page_num > 1:
        canv.setFont('Mono', 7.5)
        canv.setFillColor(TEXT_MUTED)
        canv.drawString(20*mm, 285*mm, 'VNBOT — Technical Requirements Document')
        canv.drawRightString(190*mm, 285*mm, '02-TRD-VNBOT.md')
        canv.line(20*mm, 283*mm, 190*mm, 283*mm)
    canv.restoreState()

# ===== Build story =====
story = []

# --- TOC ---
story.append(Paragraph('Tabla de Contenidos', style_toc_title))
story.append(HRFlowable(width='100%', thickness=1, color=ACCENT, spaceAfter=14))
toc = TableOfContents()
toc.levelStyles = [toc_level0, toc_level1]
story.append(toc)
story.append(PageBreak())

# ===== Section 1: Propósito y alcance =====
add_heading('1. Propósito y alcance', style_h1, level=0, story=story)
story.append(p(
    'Este documento define los requisitos técnicos, restricciones, decisiones de arquitectura '
    'y criterios operativos para construir VNBOT como una plataforma multiplataforma de '
    'memoria personal, recordatorios y mini-agentes. El TRD traduce los objetivos de producto '
    'del PRD a una arquitectura ejecutable y verificable.'
))
story.append(p('El TRD especifica los siguientes dominios técnicos:'))
story.extend(bullet_list([
    'Capas del sistema y separación de responsabilidades.',
    'Aplicaciones cliente (web/PWA, APK, desktop, CLI).',
    'Servicios backend (API, worker, scheduler, MCP gateway).',
    'Persistencia (SQLite, PostgreSQL, pgvector, object storage).',
    'Procesamiento asíncrono (jobs, colas, reintentos, dead-letter).',
    'Multi-LLM con router, fallback y presupuestos.',
    'MCP interno y externo con policy engine.',
    'Pipeline de audio (captura, transcripción, retención).',
    'Memoria de grafo con procedencia, confianza y benchmarks.',
    'Caching multinivel con invalidación explícita.',
    'Seguridad técnica (auth, cifrado, SSRF, CSP).',
    'Observabilidad con OpenTelemetry desde la primera versión.',
    'Docker y orquestación para self-hosting.',
    'GitHub Pages (demo) y GitHub Releases (artefactos).',
    'Estrategia de escalabilidad progresiva.',
]))
story.append(p(
    'El TRD no sustituye el esquema detallado de endpoints, tablas y eventos del Esquema '
    'Backend, ni el detalle visual del Diseño UI/UX. Es el documento puente entre el "qué" '
    '(PRD) y el "cómo detallado" (Esquema Backend + Plan de Implementación).'
))

# ===== Section 2: Principios técnicos =====
add_heading('2. Principios técnicos', style_h1, level=0, story=story)
story.append(p(
    'Siete principios técnicos guían todas las decisiones de arquitectura. Cada principio es '
    'deliberado y existe porque sin él VNBOT se volvería frágil, opaco o inseguro. Ningún '
    'principio es opcional: si una implementación los viola, debe revisarse antes de merger.'
))

add_heading('2.1. Separación de responsabilidades', style_h2, level=1, story=story)
story.append(p(
    'La interfaz no debe contener las reglas críticas de negocio. El frontend puede presentar '
    'y solicitar operaciones, pero la validación final de fechas, permisos, herramientas, '
    'cuotas y persistencia debe estar en una capa de dominio compartida o en el backend. '
    'Esta separación garantiza que un cliente comprometido no pueda eludir las reglas.'
))
story.append(code_block(
    'Cliente\n'
    '  ↓ solicita\n'
    'API\n'
    '  ↓ valida autenticación y schema\n'
    'Dominio\n'
    '  ↓ aplica reglas\n'
    'Persistencia / Cola\n'
    '  ↓ ejecuta\n'
    'Worker / Integración'
))

add_heading('2.2. El LLM no es una fuente de verdad', style_h2, level=1, story=story)
story.append(p('El modelo de lenguaje puede realizar las siguientes tareas de interpretación:'))
story.extend(bullet_list([
    'Clasificar intención del usuario.',
    'Extraer campos estructurados (fechas, entidades, parámetros).',
    'Proponer una herramienta o skill adecuada.',
    'Resumir conversaciones o memorias.',
    'Recuperar contexto relevante para la operación en curso.',
]))
story.append(p('Sin embargo, el modelo no debe decidir sin validación en los siguientes casos:'))
story.extend(bullet_list([
    'Una fecha final ambigua que requiere confirmación del usuario.',
    'El permiso de leer información sensible de otro workspace.',
    'La autorización de actuar en nombre de un tercero.',
    'El envío de mensajes a contactos externos.',
    'La eliminación de datos del usuario.',
    'La ejecución de código arbitrario en el sistema del usuario.',
]))

add_heading('2.3. Local-first, no local-only obligatorio', style_h2, level=1, story=story)
story.append(p(
    'VNBOT debe poder ejecutarse localmente, pero también debe soportar un servidor privado '
    'y, opcionalmente, proveedores externos. La arquitectura debe permitir que el usuario '
    'elija el nivel de privacidad que necesita sin reescribir el núcleo del producto. Los '
    'tres modos (Local Estricto, Servidor Privado, LLM Externo) comparten el mismo dominio '
    'y solo difieren en la infraestructura activa.'
))

add_heading('2.4. Degradación controlada', style_h2, level=1, story=story)
story.append(p(
    'Si falla un proveedor o servicio, VNBOT debe degradarse con claridad y comunicar el '
    'estado al usuario. La degradación nunca debe ser silenciosa ni fingir capacidades que '
    'no están disponibles. Cada dependencia tiene un fallback explícito:'
))
deg_data = [
    ['Dependencia caída', 'Fallback', 'Comunicación al usuario'],
    ['Sin LLM', 'Heurística local con regex y parsing', 'Banner amber: "Usando modo local"'],
    ['Sin internet', 'Cola local con idempotency keys', 'Badge OFFLINE visible'],
    ['Sin vector store', 'Búsqueda textual full-text', 'Resultado sin ranking semántico'],
    ['Sin MCP externo', 'Memoria interna continúa operativa', 'Integración marcada degradada'],
    ['Sin worker', 'API informa job pendiente', 'No simula éxito, muestra "En cola"'],
]
story.append(make_table(deg_data, col_widths=[45*mm, 65*mm, 60*mm]))

add_heading('2.5. Operaciones idempotentes', style_h2, level=1, story=story)
story.append(p(
    'Cualquier operación que cree, envíe, modifique o elimine datos debe poder reintentarse '
    'sin duplicar efectos. Cada operación lleva un idempotency_key único que el backend '
    'verifica antes de ejecutar. Si la misma key llega dos veces, la segunda llamada retorna '
    'el resultado original sin volver a ejecutar el efecto. Esto es crítico para recordatorios '
    'recurrentes y para recuperación tras fallos de red.'
))

add_heading('2.6. Todo dato sensible tiene alcance', style_h2, level=1, story=story)
story.append(p(
    'Las memorias, archivos, agentes y herramientas pertenecen a un usuario y/o workspace. '
    'No existen consultas globales implícitas. Toda query debe especificar el alcance '
    '(user_id, workspace_id) y el backend debe validar que el solicitante tiene permiso '
    'sobre ese alcance. Esta regla previene filtraciones accidentales entre usuarios.'
))

add_heading('2.7. Observabilidad como requisito no funcional', style_h2, level=1, story=story)
story.append(p(
    'La observabilidad no es un "nice-to-have" post-launch. VNBOT debe poder diagnosticar '
    'por qué un recordatorio no se disparó, por qué una búsqueda fue lenta o por qué un MCP '
    'falló, sin acceso al contenido del usuario. Los traces, métricas y logs se implementan '
    'con OpenTelemetry desde la primera versión, no se añaden después.'
))

# ===== Section 3: Arquitectura de alto nivel =====
add_heading('3. Arquitectura de alto nivel', style_h1, level=0, story=story)
story.append(p(
    'La arquitectura de VNBOT sigue un patrón de capas con separación clara entre clientes, '
    'API, dominio, persistencia e integraciones. Cada capa tiene responsabilidades exclusivas '
    'y se comunica con las adyacentes mediante contratos explícitos (schemas Pydantic, '
    'eventos tipados, interfaces de dominio).'
))
story.append(code_block(
    '┌──────────────────────────────────────────────────────────┐\n'
    '│                     CLIENTES VNBOT                       │\n'
    '│  Web/PWA       Android APK       Desktop       CLI       │\n'
    '│  React         Capacitor         Tauri        Python/Rust│\n'
    '└─────────────┬───────────────┬─────────────┬─────────────┘\n'
    '              │ HTTPS/WebSocket/Local IPC\n'
    '              ▼\n'
    '┌──────────────────────────────────────────────────────────┐\n'
    '│                         API VNBOT                         │\n'
    '│ Auth · Chat · Memory · Graph · Reminders · Agents · API  │\n'
    '└──────────────┬───────────────┬──────────────┬─────────────┘\n'
    '               │               │              │\n'
    '               ▼               ▼              ▼\n'
    '        Domain services     Queue         MCP Gateway\n'
    '        Validation          Redis         Policy engine\n'
    '        Authorization       Jobs          External tools\n'
    '               │               │              │\n'
    '               ▼               ▼              ▼\n'
    '      SQLite/PostgreSQL   Workers       Calendar/Email/etc.\n'
    '      pgvector/index      Scheduler     Graphify/MCP servers\n'
    '               │\n'
    '               ▼\n'
    '          Object Storage\n'
    '       Audio · Files · Backups'
))

# ===== Section 4: Perfiles de instalación =====
add_heading('4. Arquitectura por perfiles de instalación', style_h1, level=0, story=story)
story.append(p(
    'VNBOT define cuatro perfiles de instalación con conjuntos de componentes distintos. Cada '
    'perfil corresponde a un caso de uso real y no requiere componentes innecesarios. La '
    'selección del perfil se hace durante el onboarding y determina qué servicios se activan.'
))

add_heading('4.1. Perfil Demo — GitHub Pages', style_h2, level=1, story=story)
story.append(p(
    'Muestra la experiencia de VNBOT sin necesidad de backend ni credenciales reales. Está '
    'pensado para evaluación inicial del producto y para documentación interactiva.'
))
story.extend(bullet_list([
    'React/Vite compilado como sitio estático.',
    'Datos ficticios en fixtures JSON.',
    'Chat mock con respuestas pre-grabadas.',
    'Grafo de ejemplo con 12-20 nodos.',
    'Mascotas y estados visuales completos.',
    'Documentación y guías integradas.',
]))
story.append(p('GitHub Pages no ejecuta los siguientes componentes:'))
story.extend(bullet_list([
    'API privada.',
    'Worker.',
    'Scheduler persistente.',
    'LLM local.',
    'Base de datos servidor.',
    'Secretos.',
]))
story.append(callout(
    'La demo no debe pedir API keys reales ni almacenar información privada. Todas las '
    'respuestas de la demo deben provenir de fixtures o de un modo sandbox explícito.',
    color=SEM_WARNING
))

add_heading('4.2. Perfil Local — una persona', style_h2, level=1, story=story)
story.append(p(
    'Adecuado para desktop, terminal y usuarios que no desean un servidor. Toda la '
    'infraestructura corre en el dispositivo del usuario.'
))
story.append(code_block(
    'vnbot-client\n'
    'vnbot-local-api\n'
    'SQLite\n'
    'worker embebido o proceso local\n'
    'LLM local opcional (Ollama)\n'
    'filesystem cifrado'
))

add_heading('4.3. Perfil Personal Server', style_h2, level=1, story=story)
story.append(p(
    'Adecuado para sincronizar varios dispositivos de una persona o una familia pequeña. El '
    'servidor corre en una máquina propia (VPS, NAS, mini-PC).'
))
story.append(code_block(
    'vnbot-api\n'
    'vnbot-worker\n'
    'vnbot-scheduler\n'
    'PostgreSQL\n'
    'Redis\n'
    'MinIO/S3'
))

add_heading('4.4. Perfil Full', style_h2, level=1, story=story)
story.append(p(
    'Adecuado para equipos, comunidades o servidores con varios workspaces. Incluye todos '
    'los componentes con escalado horizontal.'
))
story.append(code_block(
    'vnbot-api x N\n'
    'vnbot-worker x N\n'
    'vnbot-scheduler x 1 o con locks\n'
    'vnbot-mcp-gateway\n'
    'postgres\n'
    'redis\n'
    'minio\n'
    'ollama opcional\n'
    'observabilidad (otel collector, prometheus, grafana)'
))

# ===== Section 5: Stack tecnológico =====
add_heading('5. Stack tecnológico propuesto', style_h1, level=0, story=story)

add_heading('5.1. Frontend web/PWA', style_h2, level=1, story=story)
story.append(p('Stack recomendado para el frontend web/PWA:'))
story.extend(bullet_list([
    '<b>React</b> como librería base.',
    '<b>TypeScript</b> en modo estricto.',
    '<b>Vite</b> como bundler y dev server.',
    '<b>TanStack Query</b> para datos remotos y cache de UI.',
    '<b>Zustand</b> solo para estado de interfaz y sesión local controlada.',
    '<b>IndexedDB</b> mediante <b>Dexie</b> para datos locales.',
    '<b>CSS/Tailwind</b> con tokens propios de VNBOT.',
    '<b>Canvas/WebGL</b> opcional para el grafo de memoria.',
]))
story.append(p(
    'La aplicación necesita ser estática para GitHub Pages, empaquetable para Capacitor y '
    'reutilizable dentro de Tauri. Un frontend desacoplado reduce la dependencia de un '
    'servidor Next.js ejecutándose permanentemente y simplifica el despliegue multiplataforma.'
))

add_heading('5.2. Backend', style_h2, level=1, story=story)
story.append(p('Stack recomendado para el backend:'))
story.extend(bullet_list([
    '<b>Python 3.12+</b> como lenguaje principal.',
    '<b>FastAPI</b> como framework web.',
    '<b>Pydantic v2</b> para validación de schemas.',
    '<b>SQLAlchemy 2</b> como ORM con soporte async.',
    '<b>Alembic</b> para migraciones de schema.',
    '<b>Uvicorn/Gunicorn</b> según el despliegue.',
]))
story.append(p(
    'Python facilita el procesamiento de audio, la integración con Whisper, los modelos '
    'locales, los workers de IA, las librerías de extracción y el prototipado de memoria y '
    'grafos. Si el equipo decide operar completamente en TypeScript, la alternativa es '
    'NestJS o Fastify con Drizzle. No se recomienda mantener dos backends principales en '
    'lenguajes distintos para las mismas reglas de negocio.'
))

add_heading('5.3. Base de datos', style_h2, level=1, story=story)
story.append(p('VNBOT soporta dos motores de base de datos según el perfil de instalación:'))
db_data = [
    ['Motor', 'Uso principal', 'Ventajas'],
    ['SQLite', 'Modo local, desktop, instalaciones personales, tests, desarrollo', 'Sin servidor, file-based, transaccional, ampliamente soportado'],
    ['PostgreSQL', 'Servidor, multiusuario, workers concurrentes, pgvector, RLS', ['Escalado horizontal, full-text search nativa, extensions ecosystem']],
]
# Fix the list inside cell - convert to string
db_data[2][2] = 'Escalado horizontal, full-text search nativa, extensions ecosystem'
story.append(make_table(db_data, col_widths=[30*mm, 80*mm, 60*mm]))
story.append(Spacer(1, 6))
story.append(callout(
    'Regla: ambas implementaciones deben cumplir una interfaz de almacenamiento común. No '
    'se debe escribir lógica de negocio específica para PostgreSQL en el núcleo del dominio.',
    color=ACCENT
))

add_heading('5.4. Cola y jobs', style_h2, level=1, story=story)
story.append(p('Sistema de cola y jobs para procesamiento asíncrono:'))
story.extend(bullet_list([
    '<b>Redis</b> para cola, locks distribuidos y rate limiting.',
    '<b>Dramatiq</b> o <b>Celery</b> para workers.',
    '<b>Scheduler separado</b> de la API para evitar duplicación.',
    '<b>Dead-letter queue</b> para jobs fallidos persistentes.',
    '<b>Backoff exponencial</b> en reintentos.',
]))
story.append(p(
    'Para una instalación local mínima, puede existir un modo sin Redis basado en una tabla '
    'SQLite de jobs, pero este modo no debe presentarse como equivalente a una arquitectura '
    'distribuida. Es una alternativa simplificada con límites documentados.'
))

add_heading('5.5. Almacenamiento de objetos', style_h2, level=1, story=story)
story.append(p('Almacenamiento de objetos para archivos binarios:'))
story.extend(bullet_list([
    '<b>MinIO</b> en self-hosting (compatible con S3).',
    '<b>S3 compatible</b> en instalaciones administradas.',
    '<b>Filesystem local</b> para modo single-user.',
]))
story.append(p('Se utiliza para:'))
story.extend(bullet_list([
    'Audios capturados.',
    'Imágenes y documentos adjuntos.',
    'Backups cifrados.',
    'Assets descargables si el proyecto los distribuye.',
]))

# ===== Section 6: Clientes y plataformas =====
add_heading('6. Clientes y plataformas', style_h1, level=0, story=story)
story.append(p(
    'VNBOT se distribuye en cuatro clientes con contratos API comunes. La reducción de '
    'superficie temprana es deliberada: el MVP prioriza Web/PWA y añade los demás clientes '
    'solo cuando la sync strategy está probada.'
))

add_heading('6.1. Web/PWA', style_h2, level=1, story=story)
story.append(p('El cliente web/PWA debe proporcionar:'))
story.extend(bullet_list([
    'Chat con captura de texto y audio.',
    'Panel Hoy con recordatorios y accesos rápidos.',
    'Vista de Memoria y Grafo.',
    'Gestión de Agentes y Skills.',
    'Configuración completa.',
    'Captura de audio mediante permiso explícito.',
    'Notificaciones web cuando el navegador lo permita.',
    'Modo offline básico con IndexedDB.',
]))

add_heading('6.2. Android APK', style_h2, level=1, story=story)
story.append(p('Primera estrategia: <b>Capacitor</b>. Permite empaquetar la PWA y añadir capacidades nativas:'))
story.extend(bullet_list([
    'Notificaciones locales.',
    'Micrófono.',
    'Filesystem.',
    'Estado de red.',
    'Deep links.',
    'Biometría en una fase posterior.',
]))
story.append(p('Limitaciones conocidas:'))
story.extend(bullet_list([
    'Tareas en segundo plano pueden estar limitadas por Android.',
    'La entrega de notificaciones depende de permisos y optimización de batería.',
    'La transcripción local puede consumir mucho almacenamiento y RAM.',
    'Se debe validar la compatibilidad con dispositivos de gama baja.',
]))
story.append(callout(
    'Requisito: el backend seguirá siendo la fuente de verdad para recordatorios sincronizados. '
    'El APK puede mantener recordatorios locales, pero no debe depender exclusivamente de un '
    'proceso que Android pueda suspender.',
    color=SEM_WARNING
))

add_heading('6.3. Desktop', style_h2, level=1, story=story)
story.append(p('Primera estrategia: <b>Tauri</b>. Ofrece ventajas significativas sobre Electron:'))
story.extend(bullet_list([
    'Menor consumo de memoria que Electron.',
    'Integración con filesystem local.',
    'Notificaciones nativas del SO.',
    'Posibilidad de usar SQLite local embebido.',
    'Empaquetado para Windows, macOS y Linux.',
]))
story.append(p('Electron como alternativa si:'))
story.extend(bullet_list([
    'Se requieren módulos Node difíciles de integrar en Tauri.',
    'Se necesita un ecosistema de plugins desktop más amplio.',
    'El coste de memoria no es una prioridad.',
]))
story.append(p(
    'No se deben mantener Tauri y Electron como productos paralelos en la primera versión. '
    'La elección inicial es Tauri y solo se migra a Electron si hay requisitos técnicos '
    'que lo justifiquen explícitamente.'
))

add_heading('6.4. CLI', style_h2, level=1, story=story)
story.append(p('La CLI debe servir para operaciones de administración y captura rápida:'))
story.append(code_block(
    'vnbot init\n'
    'vnbot doctor\n'
    'vnbot health\n'
    'vnbot add "revisar presupuesto mañana"\n'
    'vnbot search "wifi"\n'
    'vnbot reminders list\n'
    'vnbot backup create\n'
    'vnbot backup restore ./backup.vnbot.zip\n'
    'vnbot migrate\n'
    'vnbot mcp list'
))
story.append(p(
    'La CLI no debe pedir que el usuario pegue secretos en argumentos visibles del historial '
    'del shell. Debe aceptar variables de entorno seguras, prompt interactivo o archivos de '
    'configuración con permisos restrictivos (0600).'
))

add_heading('6.5. Reducción de superficie temprana', style_h2, level=1, story=story)
story.append(p(
    'El TRD original diseña cuatro clientes desde el inicio. Para acelerar el MVP se aplica '
    'una estrategia de liberación progresiva:'
))
story.extend(bullet_list([
    '<b>0.1:</b> Solo Web/PWA. Es el cliente con mayor alcance y menor fricción.',
    '<b>0.2:</b> Se añade soporte Docker para autoalojamiento (es deployment, no un cliente nuevo).',
    '<b>0.3:</b> Se evalúa APK (Capacitor) y Desktop (Tauri) después de tener la sync strategy probada.',
    '<b>CLI:</b> Se implementa como wrapper sobre la API HTTP desde 0.1. Un script vnbot que hace curl a localhost es suficiente para empezar.',
]))
story.append(callout(
    'No se diseñan adapters de plataforma ni abstracciones prematuras hasta que exista al '
    'menos un cliente funcional. Premature abstraction es más costosa que refactor posterior.',
    color=ACCENT
))

# ===== Section 7: Capas de software =====
add_heading('7. Capas de software', style_h1, level=0, story=story)
story.append(p(
    'VNBOT sigue una arquitectura en cuatro capas con responsabilidades exclusivas. Cada capa '
    'se comunica solo con las adyacentes mediante contratos explícitos. Esta separación es '
    'lo que permite intercambiar implementaciones (PostgreSQL por SQLite, OpenAI por Ollama) '
    'sin reescribir el dominio.'
))

capas_data = [
    ['Capa', 'Responsabilidades', 'No debe hacer'],
    ['Presentación', 'Renderizar vistas, recibir interacción, mostrar estado, gestionar cache de UI, mostrar errores comprensibles', 'Ejecutar reglas críticas de autorización o validación de negocio'],
    ['Aplicación', 'Coordinar casos de uso, crear operaciones, enviar jobs, resolver confirmaciones, coordinar transacciones, exponer comandos y queries', 'Contener reglas de dominio puras (delegar al dominio)'],
    ['Dominio', 'Reglas de recordatorios, estados de memoria, reglas de recurrencia, entidades y relaciones, políticas de riesgo, idempotencia, validaciones de negocio', 'Depender de infraestructura concreta (SQL, Redis, proveedor LLM específico)'],
    ['Infraestructura', 'SQL, Redis, LLM providers, MCP transports, filesystem, S3/MinIO, notificaciones, audio', 'Contener lógica de negocio (solo adaptadores)'],
]
story.append(make_table(capas_data, col_widths=[28*mm, 80*mm, 62*mm]))

# ===== Section 8: Módulos técnicos =====
add_heading('8. Módulos técnicos', style_h1, level=0, story=story)
story.append(p(
    'El backend de VNBOT se organiza en ocho módulos técnicos con responsabilidades '
    'delimitadas. Cada módulo tiene su propia interfaz, tests y documentación. Los módulos '
    'se comunican mediante eventos y comandos tipados, no mediante llamadas directas '
    'acopladas.'
))

modulos_data = [
    ['Módulo', 'Responsabilidades clave'],
    ['Auth y sesión', 'Registro local opcional, login, sesiones revocables, cookies HttpOnly, Argon2id, MFA posterior, diferenciación entre sesión de cuenta y desbloqueo de bóveda.'],
    ['Chat Orchestrator', 'Normalización, clasificación, recuperación de contexto, selección de skill, extracción estructurada, validación, confirmación, ejecución, auditoría.'],
    ['Memory Engine', 'Nodos, aristas, procedencia, confianza, sensibilidad, expiración, búsqueda textual, búsqueda vectorial, búsqueda por relaciones, correcciones y contradicciones.'],
    ['Reminder Engine', 'Reglas de recurrencia, ocurrencias concretas, zona horaria, ventanas de silencio, prioridad, canales, reintentos, idempotencia, delivery log.'],
    ['LLM Router', 'Adaptadores por proveedor, modelos locales, fallback, circuit breaker, presupuesto, conteo de tokens, selección por tarea, política de datos.'],
    ['MCP Gateway', 'Registro de servidores, transportes stdio y Streamable HTTP, descubrimiento de tools/resources, scopes, policy engine, timeouts, auditoría, healthcheck.'],
    ['Audio Pipeline', 'Captura, carga, normalización, transcripción, revisión, extracción, retención/borrado.'],
    ['Notification Service', 'Canales: web, desktop, Android, email (posterior), Telegram (posterior). Cada canal con estado de entrega y reintentos independientes.'],
]
story.append(make_table(modulos_data, col_widths=[35*mm, 135*mm]))

# ===== Section 9: Flujo técnico de una instrucción =====
add_heading('9. Flujo técnico de una instrucción', style_h1, level=0, story=story)
story.append(p(
    'Cada instrucción del usuario atraviesa 16 pasos técnicos desde que llega al cliente '
    'hasta que se audita el resultado. Este flujo es el corazón operativo de VNBOT y debe '
    'cumplirse sin atajos. Cualquier omisión de un paso es un bug arquitectónico.'
))
story.append(code_block(
    '1. Cliente envía mensaje\n'
    '2. API valida sesión y tamaño\n'
    '3. Se crea operation_id\n'
    '4. Se guarda mensaje de entrada con política de retención\n'
    '5. Router clasifica intención\n'
    '6. Se recupera contexto mínimo autorizado\n'
    '7. LLM o heurística produce JSON\n'
    '8. Pydantic valida el JSON\n'
    '9. Policy engine calcula riesgo\n'
    '10. Si falta dato → NEEDS_CLARIFICATION\n'
    '11. Si requiere aprobación → WAITING_CONFIRMATION\n'
    '12. Si está autorizado → crea comando\n'
    '13. Dominio ejecuta o encola job\n'
    '14. Worker realiza integración si corresponde\n'
    '15. Resultado se audita\n'
    '16. Cliente recibe estado final'
))

add_heading('9.1. Estados de operación', style_h2, level=1, story=story)
story.append(p(
    'Cada operación pasa por una máquina de 11 estados. Las transiciones son explícitas y '
    'auditables. Una operación no debe pasar directamente de una respuesta textual del LLM '
    'a un efecto externo irreversible.'
))
story.append(code_block(
    'RECEIVED\n'
    'CLASSIFYING\n'
    'NEEDS_CLARIFICATION\n'
    'PROPOSED\n'
    'WAITING_CONFIRMATION\n'
    'QUEUED\n'
    'EXECUTING\n'
    'SUCCEEDED\n'
    'RETRYING\n'
    'FAILED\n'
    'CANCELLED'
))

# ===== Section 10: Memoria y grafo =====
add_heading('10. Memoria y grafo', style_h1, level=0, story=story)

add_heading('10.1. Implementación MVP', style_h2, level=1, story=story)
story.append(p('La implementación inicial del Memory Engine usa:'))
story.extend(bullet_list([
    'Tablas <b>memory_nodes</b> y <b>memory_edges</b>.',
    '<b>PostgreSQL + pgvector</b> en servidor.',
    '<b>SQLite + índice local</b> en instalación personal.',
    'Profundidad máxima visible configurable.',
    '<b>Top-K</b> por relevancia.',
    'Procedencia obligatoria.',
    'Confianza separada de importancia.',
]))

add_heading('10.2. Tipos de nodos', style_h2, level=1, story=story)
story.append(p('El Memory Engine reconoce 11 tipos de nodos:'))
story.append(code_block(
    'person\n'
    'place\n'
    'project\n'
    'task\n'
    'reminder\n'
    'event\n'
    'preference\n'
    'note\n'
    'document\n'
    'conversation\n'
    'agent'
))

add_heading('10.3. Tipos de relaciones', style_h2, level=1, story=story)
story.append(p('Las aristas del grafo pueden ser de 11 tipos:'))
story.append(code_block(
    'KNOWS\n'
    'WORKS_ON\n'
    'RELATED_TO\n'
    'DEPENDS_ON\n'
    'REMINDER_FOR\n'
    'HAPPENS_AT\n'
    'PREFERS\n'
    'SUPERSEDES\n'
    'CONTRADICTS\n'
    'DERIVED_FROM\n'
    'ASSIGNED_TO'
))

add_heading('10.4. Graphify', style_h2, level=1, story=story)
story.append(p(
    'Graphify será un adaptador opcional para información estructural de repositorios y '
    'otros datos compatibles. No reemplaza el Memory Engine personal. VNBOT debe poder:'
))
story.extend(bullet_list([
    'Conectarse mediante MCP.',
    'Mostrar estado y scopes.',
    'Consultar datos autorizados.',
    'Crear referencias cruzadas.',
    'Mantener separadas las memorias personales y las de código.',
]))

add_heading('10.5. Benchmarks de rendimiento del grafo', style_h2, level=1, story=story)
story.append(p(
    'VNBOT debe definir objetivos de rendimiento para la memoria de grafo antes de la fase '
    'de implementación (0.4/0.5). Sin benchmarks, no se puede medir regresiones ni decidir '
    'cuándo una optimización es necesaria.'
))

add_heading('10.5.1. Escenario de referencia', style_h3, level=2, story=story)
bench_esc = [
    ['Parámetro', 'Valor objetivo'],
    ['Nodos totales', '5,000'],
    ['Edges totales', '10,000'],
    ['Profundidad máxima de consulta', '3'],
    ['Top-K por consulta', '20'],
]
story.append(make_table(bench_esc, col_widths=[90*mm, 80*mm]))

add_heading('10.5.2. Latencia objetivo (P95)', style_h3, level=2, story=story)
bench_lat = [
    ['Operación', 'Local (SQLite)', 'Servidor (PostgreSQL)'],
    ['Crear nodo', '< 50ms', '< 30ms'],
    ['Crear edge', '< 50ms', '< 30ms'],
    ['Búsqueda textual (full-text)', '< 100ms', '< 80ms'],
    ['Búsqueda semántica (vector)', '< 200ms', '< 100ms'],
    ['Subgrafo (profundidad 2, 20 nodos)', '< 300ms', '< 150ms'],
    ['Subgrafo (profundidad 3, 50 nodos)', '< 500ms', '< 250ms'],
    ['Recorrido con filtro de confianza', '< 400ms', '< 200ms'],
    ['Invalidación por borrado', '< 200ms', '< 100ms'],
]
story.append(make_table(bench_lat, col_widths=[80*mm, 45*mm, 45*mm]))

add_heading('10.5.3. Métricas de escala', style_h3, level=2, story=story)
story.extend(bullet_list([
    'El sistema debe degradar graciosamente (paginación, límite de profundidad) si una consulta excede los umbrales.',
    'Nunca cargar el grafo completo en memoria del cliente.',
    'Implementar EXPLAIN ANALYZE o equivalente en tests de integración para detectar regresiones de queries.',
    'Benchmark automatizado en CI para las operaciones P0.',
]))

add_heading('10.5.4. Criterios de aceptación', style_h3, level=2, story=story)
story.extend(bullet_list([
    'Los benchmarks se ejecutan en CI como parte del pipeline.',
    'Cualquier commit que degrade P95 en más de 20% en una operación P0 debe ser revisado.',
    'Los resultados se publican en cada release notes.',
]))

# ===== Section 11: Multi-LLM =====
add_heading('11. Multi-LLM', style_h1, level=0, story=story)

add_heading('11.1. Interfaz común', style_h2, level=1, story=story)
story.append(p(
    'Todos los proveedores LLM implementan una interfaz común. Esto permite cambiar de '
    'proveedor sin tocar el dominio y añadir nuevos adaptadores sin romper los existentes.'
))
story.append(code_block(
    'class LLMProvider(Protocol):\n'
    '    async def generate(\n'
    '        self,\n'
    '        messages: list[Message],\n'
    '        tools: list[ToolSchema] | None,\n'
    '        response_schema: dict | None,\n'
    '    ) -> LLMResponse: ...\n'
    '\n'
    '    async def embed(self, texts: list[str]) -> list[list[float]]: ...'
))

add_heading('11.2. Categorías de modelos', style_h2, level=1, story=story)
story.append(p('Cada tarea usa el modelo más adecuado según su naturaleza:'))
llm_cat = [
    ['Tarea', 'Preferencia de modelo'],
    ['Intención sencilla', 'Modelo pequeño/local'],
    ['Extracción JSON', 'Modelo con structured output'],
    ['Resumen', 'Modelo económico'],
    ['Planificación', 'Modelo avanzado'],
    ['Datos sensibles', 'Modelo local'],
    ['Embeddings', 'Modelo local especializado'],
    ['Audio', 'Whisper / whisper.cpp'],
]
story.append(make_table(llm_cat, col_widths=[60*mm, 110*mm]))

add_heading('11.3. Fallback', style_h2, level=1, story=story)
story.append(p(
    'Si el proveedor principal falla, el router sigue una cadena de fallback explícita. '
    'Cada degradación debe comunicarse al usuario para que sepa que la calidad o capacidad '
    'se redujo.'
))
story.append(code_block(
    'Proveedor principal\n'
    '  ↓ falla temporal\n'
    'Proveedor secundario\n'
    '  ↓ no disponible\n'
    'Modelo local\n'
    '  ↓ no disponible\n'
    'Heurística'
))

add_heading('11.4. Seguridad de claves', style_h2, level=1, story=story)
story.extend(bullet_list([
    'No guardar claves en localStorage del navegador.',
    'Usar secret store del servidor o keychain del sistema en desktop/mobile.',
    'Redactar valores de claves en logs automáticamente.',
    'Permitir claves por usuario o workspace.',
    'Separar clave de embedding, chat y herramienta.',
    'Revocar y rotar claves sin recompilar.',
]))

add_heading('11.5. Presupuesto', style_h2, level=1, story=story)
story.append(p('Cada usuario/workspace/agente puede tener límites de presupuesto:'))
story.extend(bullet_list([
    'Máximo de tokens por periodo.',
    'Coste mensual estimado.',
    'Máximo de llamadas por minuto.',
    'Máximo de tool calls por operación.',
    'Proveedores permitidos.',
]))

# ===== Section 12: MCP =====
add_heading('12. MCP', style_h1, level=0, story=story)

add_heading('12.1. Función', style_h2, level=1, story=story)
story.append(p(
    'MCP será el sistema de expansión de VNBOT. Permitirá conectar herramientas y recursos '
    'de forma estandarizada sin acoplar el núcleo a cada servicio. MCP es el equivalente a '
    'un sistema de plugins con permisos granulares y auditoría.'
))

add_heading('12.2. MCP interno', style_h2, level=1, story=story)
story.append(p('Herramientas controladas por VNBOT (siempre disponibles):'))
story.append(code_block(
    'memory_search\n'
    'memory_create\n'
    'memory_update\n'
    'memory_forget\n'
    'memory_link\n'
    'graph_expand\n'
    'reminder_create\n'
    'reminder_complete\n'
    'reminder_snooze\n'
    'list_manage\n'
    'briefing_generate'
))

add_heading('12.3. MCP externo', style_h2, level=1, story=story)
story.append(p('Conectores posibles mediante servidores MCP externos:'))
story.extend(bullet_list([
    'Graphify (repos de código).',
    'Calendarios (Google, ICS, CalDAV).',
    'Email (Gmail, IMAP).',
    'Filesystem (carpetas locales).',
    'Web/search.',
    'Notas (Obsidian, Notion).',
    'Mensajería oficial (Telegram, WhatsApp Business).',
]))

add_heading('12.4. Seguridad', style_h2, level=1, story=story)
story.append(p(
    'MCP no concede autorización automáticamente. El gateway valida 10 dimensiones antes '
    'de ejecutar cualquier tool call externo:'
))
story.extend(bullet_list([
    'Servidor confiable (allowlist).',
    'Usuario autenticado.',
    'Workspace válido.',
    'Agente con permiso.',
    'Herramienta habilitada.',
    'Scope aprobado.',
    'Riesgo calculado.',
    'Confirmación del usuario si es alto riesgo.',
    'Presupuesto disponible.',
    'Timeout configurado.',
]))

add_heading('12.5. Transportes', style_h2, level=1, story=story)
story.extend(bullet_list([
    '<b>stdio</b>: servidores locales (ejecutable en misma máquina).',
    '<b>Streamable HTTP</b>: servidores remotos (HTTPS con auth).',
    '<b>SSE</b>: solo cuando sea necesario por compatibilidad con servidores legacy.',
]))

add_heading('12.6. Tool result', style_h2, level=1, story=story)
story.append(p('Toda herramienta debe devolver resultado estructurado para auditoría:'))
story.append(code_block(
    '{\n'
    '  "ok": true,\n'
    '  "tool": "calendar.create_event",\n'
    '  "data": {},\n'
    '  "source": "google-calendar",\n'
    '  "operation_id": "op_123",\n'
    '  "warnings": []\n'
    '}'
))

# ===== Section 13: Skills y agentes =====
add_heading('13. Skills y agentes', style_h1, level=0, story=story)

add_heading('13.1. Skill', style_h2, level=1, story=story)
story.append(p('Una skill es una capacidad versionada que define:'))
story.extend(bullet_list([
    'Objetivo.',
    'Entrada esperada.',
    'Salida producida.',
    'Herramientas que puede usar.',
    'Memoria permitida.',
    'Riesgo calculado.',
    'Confirmación requerida o no.',
    'Límites de uso.',
]))

add_heading('13.2. Agente', style_h2, level=1, story=story)
story.append(p('Un agente combina los siguientes elementos:'))
story.extend(bullet_list([
    'Prompt de sistema.',
    'Modelo LLM asignado.',
    'Skills habilitadas.',
    'Herramientas disponibles.',
    'Scopes de memoria accesible.',
    'Nivel de autonomía (0-4).',
    'Presupuesto.',
    'Mascota visual asignada.',
]))

add_heading('13.3. Niveles de autonomía', style_h2, level=1, story=story)
story.append(p('Los agentes tienen 5 niveles de autonomía creciente:'))
story.append(code_block(
    '0 — Solo responder\n'
    '1 — Proponer\n'
    '2 — Ejecutar acciones internas\n'
    '3 — Usar integraciones con confirmación\n'
    '4 — Automatizar reglas explícitas y limitadas'
))

add_heading('13.4. Aislamiento', style_h2, level=1, story=story)
story.append(p(
    'Cada agente debe tener un contexto mínimo. No debe recibir todas las memorias del '
    'usuario por defecto. El sistema debe recuperar solamente el contexto necesario para '
    'la skill activa. Este principio de mínimo contexto reduce el riesgo de filtración '
    'de información sensible a proveedores LLM externos y mejora el rendimiento.'
))

# ===== Section 14: Procesamiento asíncrono =====
add_heading('14. Procesamiento asíncrono', style_h1, level=0, story=story)

add_heading('14.1. Operaciones asíncronas', style_h2, level=1, story=story)
story.append(p('Las siguientes operaciones se procesan de forma asíncrona mediante jobs:'))
story.extend(bullet_list([
    'Audio (transcripción).',
    'OCR (extracción de texto de imágenes).',
    'Embeddings (vectorización de memorias).',
    'Consolidación (merge de memorias duplicadas).',
    'Briefings (resúmenes diarios/semanales).',
    'Sincronización MCP.',
    'Notificaciones (delivery multi-canal).',
    'Backups (exportación cifrada).',
    'Importaciones grandes.',
    'Reindexación.',
]))

add_heading('14.2. Job mínimo', style_h2, level=1, story=story)
story.append(p('Estructura mínima de un job en cola:'))
story.append(code_block(
    '{\n'
    '  "id": "job_123",\n'
    '  "type": "send_reminder",\n'
    '  "status": "pending",\n'
    '  "workspace_id": "ws_123",\n'
    '  "idempotency_key": "reminder_1_occurrence_20260717",\n'
    '  "attempt": 0,\n'
    '  "max_attempts": 5,\n'
    '  "priority": "normal",\n'
    '  "created_at": "..."\n'
    '}'
))

add_heading('14.3. Reintentos', style_h2, level=1, story=story)
story.append(p('Política de reintentos según tipo de error:'))
retry_data = [
    ['Tipo de error', 'Acción'],
    ['Error de red', 'Retry con backoff exponencial'],
    ['Error de autenticación', 'Failed y pedir reconexión al usuario'],
    ['Entrada inválida', 'Failed no retryable'],
    ['Rate limit (429)', 'Retry con Retry-After header'],
    ['Proveedor caído', 'Circuit breaker abierto, fallback a secundario'],
    ['Acción externa ambigua', 'No retry automático, marcar NEEDS_CLARIFICATION'],
]
story.append(make_table(retry_data, col_widths=[60*mm, 110*mm]))

add_heading('14.4. Scheduler', style_h2, level=1, story=story)
story.append(p(
    'Debe existir un scheduler dedicado o un sistema de locks. No se debe iniciar un cron '
    'completo dentro de cada réplica de API porque causaría duplicación de ejecuciones.'
))
story.append(callout(
    'Para el MVP se recomienda: Scheduler único + Redis locks + workers. Esto evita '
    'duplicación sin introducir complejidad de orquestación prematura.',
    color=ACCENT
))

# ===== Section 15: Cache =====
add_heading('15. Cache', style_h1, level=0, story=story)

add_heading('15.1. Capas', style_h2, level=1, story=story)
story.append(p('VNBOT implementa cinco capas de cache con responsabilidades distintas:'))
story.append(code_block(
    'UI cache       TanStack Query\n'
    'Local cache    IndexedDB/SQLite\n'
    'Server cache   Redis\n'
    'Search index   FTS/pgvector\n'
    'Asset cache    Service Worker/CDN local'
))

add_heading('15.2. Cache permitido', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Catálogo de modelos LLM.',
    'Schemas MCP.',
    'Configuración no secreta.',
    'Resultados de búsqueda con TTL.',
    'Embeddings derivados mediante hash seguro.',
    'Resúmenes compactos.',
    'Estados de healthcheck de corta duración.',
]))

add_heading('15.3. Cache prohibido sin protección', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Plaintext sensible.',
    'API keys.',
    'Tokens.',
    'Audio original.',
    'Respuestas completas con secretos.',
]))

add_heading('15.4. Invalidación', style_h2, level=1, story=story)
story.append(p('Toda modificación de memoria debe invalidar en cascada:'))
story.extend(bullet_list([
    'Búsqueda relacionada.',
    'Grafo del workspace.',
    'Embedding anterior.',
    'Resúmenes dependientes.',
    'Cache del cliente.',
]))

# ===== Section 16: Seguridad técnica =====
add_heading('16. Seguridad técnica', style_h1, level=0, story=story)

add_heading('16.1. Autenticación', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Argon2id para hashing de contraseñas.',
    'Sesiones rotatorias con refresh token.',
    'Cookies seguras (HttpOnly, Secure, SameSite).',
    'Revocación server-side de sesiones.',
    'MFA posterior al MVP.',
    'WebAuthn posterior al MVP.',
]))

add_heading('16.2. Autorización', style_h2, level=1, story=story)
story.append(p(
    'El backend debe comprobar user_id, workspace_id, agente, skill y herramienta en cada '
    'operación. No confiar únicamente en IDs enviados por el cliente. Toda autorización se '
    'verifica contra el estado del servidor, no contra claims del cliente.'
))

add_heading('16.3. Protección de frontend', style_h2, level=1, story=story)
story.extend(bullet_list([
    'CSP estricta.',
    'Sanitización de Markdown/HTML.',
    'No usar dangerouslySetInnerHTML sin sanitizar.',
    'No guardar secretos en localStorage.',
    'Validar MIME, tamaño y extensión de archivos.',
    'Protección contra XSS y CSRF.',
]))

add_heading('16.4. Protección de backend', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Rate limiting por IP, usuario y endpoint.',
    'Validación Pydantic en todos los payloads.',
    'SSRF protection para webhooks y MCP salientes.',
    'Timeouts en todas las llamadas externas.',
    'Límites de payload.',
    'Protección contra replay.',
    'Logs sin contenido sensible.',
    'Dependencias fijadas y escaneadas en CI.',
]))

add_heading('16.5. Cifrado', style_h2, level=1, story=story)
story.extend(bullet_list([
    'AES-256-GCM o XChaCha20-Poly1305 para datos en reposo.',
    'Argon2id para derivación de secretos derivados de contraseña.',
    'Salt e IV únicos por operación.',
    'Envelope encryption para backups.',
    'Versionado del formato cifrado.',
    'Rotación documentada.',
]))

add_heading('16.6. Significado de zero-knowledge', style_h2, level=1, story=story)
story.append(p('VNBOT debe documentar tres escenarios sin ambigüedad:'))
story.extend(bullet_list([
    'El modo local estricto puede mantener plaintext fuera de terceros.',
    'El servidor privado puede procesar plaintext según su configuración.',
    'Un LLM externo puede recibir contexto. En este caso no se debe prometer zero-knowledge total.',
]))

# ===== Section 17: Healthcheck y observabilidad =====
add_heading('17. Healthcheck y observabilidad', style_h1, level=0, story=story)

add_heading('17.1. Endpoints', style_h2, level=1, story=story)
story.append(p('Endpoints de healthcheck expuestos por la API:'))
story.append(code_block(
    'GET /health/live\n'
    'GET /health/ready\n'
    'GET /health/dependencies\n'
    'GET /metrics'
))

add_heading('17.2. live', style_h2, level=1, story=story)
story.append(p(
    'Comprueba que el proceso responde. No debe marcar como fallido un proveedor opcional. '
    'Es el check más ligero, usado para saber si el contenedor está vivo.'
))

add_heading('17.3. ready', style_h2, level=1, story=story)
story.append(p('Comprueba que el servicio está listo para recibir tráfico:'))
story.extend(bullet_list([
    'Base de datos conectada.',
    'Migraciones aplicadas.',
    'Cola accesible.',
    'Configuración mínima presente.',
    'Capacidad de escribir un job de prueba, si corresponde.',
]))

add_heading('17.4. dependencies', style_h2, level=1, story=story)
story.append(p(
    'Debe devolver estado resumido, latencia y versión de cada dependencia, nunca secretos. '
    'Usado para diagnóstico por administradores y por el CLI vnbot doctor.'
))

add_heading('17.5. Métricas', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Latencia de API (P50/P95/P99).',
    'Latencia de LLM por proveedor.',
    'Tokens y coste agregado.',
    'Jobs pendientes y jobs fallidos.',
    'Entregas de recordatorios.',
    'Errores de MCP.',
    'Cache hits/misses.',
    'Memoria y CPU del worker.',
    'Uso de almacenamiento.',
]))

add_heading('17.6. Tracing', style_h2, level=1, story=story)
story.append(p('Cada operación debe tener identificadores de trazabilidad:'))
story.extend(bullet_list([
    '<b>trace_id</b>: sigue la operación a través de todas las capas.',
    '<b>operation_id</b>: identificador único de la operación de negocio.',
    '<b>job_id</b>: si es asíncrona.',
    'Usuario/workspace anonimizado o interno.',
]))
story.append(callout(
    'Nunca se debe incluir el contenido completo de una memoria en una traza por defecto. '
    'Los traces son metadatos operativos, no registros de contenido.',
    color=SEM_WARNING
))

# ===== Section 18: Docker y orquestación =====
add_heading('18. Docker y orquestación', style_h1, level=0, story=story)

add_heading('18.1. Docker Compose local', style_h2, level=1, story=story)
story.append(p('El proyecto debe incluir los siguientes archivos para despliegue local:'))
story.extend(bullet_list([
    '<b>docker-compose.local.yml</b>: perfil Local.',
    '<b>docker-compose.server.yml</b>: perfil Personal Server.',
    '<b>.env.example</b>: variables de entorno documentadas.',
    '<b>Healthchecks</b> en cada servicio.',
    '<b>Volúmenes explícitos</b> para datos persistentes.',
    '<b>Migración inicial</b> automatizada.',
    '<b>Backup documentado</b> con script de restore.',
]))

add_heading('18.2. Orden de inicio', style_h2, level=1, story=story)
story.append(p('El orden de inicio de servicios respeta dependencias:'))
story.append(code_block(
    'PostgreSQL/SQLite\n'
    '  ↓\n'
    'Redis\n'
    '  ↓\n'
    'Migraciones\n'
    '  ↓\n'
    'API\n'
    '  ↓\n'
    'Worker\n'
    '  ↓\n'
    'Scheduler\n'
    '  ↓\n'
    'MCP Gateway'
))

add_heading('18.3. Seguridad de contenedores', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Usuario no root en todos los contenedores.',
    'Imagen mínima (Alpine o distroless cuando sea viable).',
    'Dependencias fijadas por hash.',
    'Filesystem read-only cuando sea viable.',
    'Secrets por Docker secrets o secret manager, no en variables de entorno.',
    'No exponer Redis públicamente.',
    'No exponer PostgreSQL públicamente por defecto.',
    'Red interna entre servicios.',
]))

add_heading('18.4. Kubernetes posterior', style_h2, level=1, story=story)
story.append(p('No es requisito del MVP. Si se incorpora, debe incluir:'))
story.extend(bullet_list([
    'Deployment separado de API y workers.',
    'CronJob o scheduler con locks distribuidos.',
    'Secrets de Kubernetes.',
    'Probes live/ready.',
    'HPA por CPU y cola.',
    'Persistent Volumes.',
    'Network Policies.',
    'Pod Security.',
]))

# ===== Section 19: GitHub Pages y Releases =====
add_heading('19. GitHub Pages y Releases', style_h1, level=0, story=story)

add_heading('19.1. GitHub Pages', style_h2, level=1, story=story)
story.append(p('Build estático para la demo y documentación:'))
story.extend(bullet_list([
    'Vite como bundler.',
    'Fixtures JSON para datos ficticios.',
    'Service Worker opcional para offline.',
    'Base path configurable.',
    'GitHub Actions para deploy automático.',
    'Sin secretos.',
    'Sin datos reales.',
]))

add_heading('19.2. Releases', style_h2, level=1, story=story)
story.append(p('Artefactos previstos por release:'))
story.append(code_block(
    'VNBOT-Setup-x64.exe\n'
    'VNBOT-linux.AppImage\n'
    'VNBOT-linux.deb\n'
    'VNBOT-macos.dmg\n'
    'VNBOT-android.apk\n'
    'checksums.txt\n'
    'SBOM.spdx.json\n'
    'release-notes.md'
))
story.append(p('Cada release debe incluir:'))
story.extend(bullet_list([
    'Versión semántica.',
    'Cambios (changelog).',
    'Migraciones requeridas.',
    'Compatibilidad con versiones anteriores.',
    'Checksums verificables.',
    'Firma cuando sea posible.',
    'Advertencias de seguridad.',
    'Assets y licencias correspondientes.',
]))

# ===== Section 20: Compatibilidad y versionado =====
add_heading('20. Compatibilidad y versionado', style_h1, level=0, story=story)

add_heading('20.1. API', style_h2, level=1, story=story)
story.append(p(
    'Usar /api/v1. Los cambios incompatibles requieren /api/v2 o una migración documentada. '
    'La política de versionado sigue semver: patch para fixes, minor para features '
    'compatibles, major para breaking changes.'
))

add_heading('20.2. Formato de exportación', style_h2, level=1, story=story)
story.append(p(
    'El formato de exportación debe tener schema_version, manifest, checksums y metadata de '
    'cifrado. El sistema debe conservar importadores para al menos una versión anterior '
    'para permitir migraciones graduales.'
))

add_heading('20.3. Skills', style_h2, level=1, story=story)
story.append(p(
    'Cada skill tiene versión semántica. Un agente debe declarar la versión usada para '
    'facilitar reproducibilidad y rollback.'
))

add_heading('20.4. MCP', style_h2, level=1, story=story)
story.append(p('Para cada servidor MCP conectado se debe guardar:'))
story.extend(bullet_list([
    'Versión del protocolo negociada.',
    'Nombre y versión del servidor.',
    'Capabilities declaradas.',
    'Fecha del último handshake.',
    'Scopes aprobados.',
]))

# ===== Section 21: Pruebas técnicas =====
add_heading('21. Pruebas técnicas', style_h1, level=0, story=story)

add_heading('21.1. Unitarias', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Resolución de fechas.',
    'Recurrencias.',
    'Idempotencia.',
    'Políticas de riesgo.',
    'Validación de schemas.',
    'Cifrado/descifrado.',
    'Parser heurístico.',
    'Permisos.',
]))

add_heading('21.2. Integración', style_h2, level=1, story=story)
story.extend(bullet_list([
    'API + base de datos.',
    'API + Redis.',
    'Worker + scheduler.',
    'Notificaciones.',
    'LLM mock.',
    'MCP mock.',
    'Import/export.',
]))

add_heading('21.3. E2E', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Onboarding.',
    'Crear recordatorio.',
    'Reiniciar worker.',
    'Reintentar delivery.',
    'Editar memoria.',
    'Eliminar memoria.',
    'Modo offline.',
    'APK.',
    'Desktop.',
]))

add_heading('21.4. Seguridad', style_h2, level=1, story=story)
story.extend(bullet_list([
    'SAST (Semgrep).',
    'DAST (OWASP ZAP).',
    'Escaneo de dependencias (npm audit, pip-audit).',
    'Secret scanning (Gitleaks).',
    'Pruebas XSS/CSRF.',
    'SSRF.',
    'Autorización entre workspaces.',
    'Replay de webhooks.',
    'MCP malicioso simulado.',
]))

add_heading('21.5. Carga', style_h2, level=1, story=story)
story.append(p('Escenarios de carga para validar escalabilidad:'))
story.extend(bullet_list([
    '10.000 memorias por workspace.',
    '1.000 recordatorios activos.',
    '100 ocurrencias simultáneas.',
    '100 jobs concurrentes en servidor de prueba.',
    '100 nodos visibles sin degradar interacción.',
]))

# ===== Section 22: Estructura de repositorio =====
add_heading('22. Estructura de repositorio propuesta', style_h1, level=0, story=story)
story.append(p(
    'El repositorio sigue una estructura monorepo con separación clara entre aplicaciones, '
    'servicios, paquetes compartidos y assets. Esta organización facilita el desarrollo '
    'multiplataforma sin duplicar lógica de negocio.'
))
story.append(code_block(
    'vnbot/\n'
    '├── apps/\n'
    '│   ├── web/\n'
    '│   ├── desktop/\n'
    '│   ├── android/\n'
    '│   └── cli/\n'
    '├── services/\n'
    '│   ├── api/\n'
    '│   ├── worker/\n'
    '│   ├── scheduler/\n'
    '│   └── mcp-gateway/\n'
    '├── packages/\n'
    '│   ├── domain/\n'
    '│   ├── schemas/\n'
    '│   ├── ui/\n'
    '│   ├── graph-ui/\n'
    '│   ├── auth/\n'
    '│   └── connectors/\n'
    '├── skills/\n'
    '├── docs/\n'
    '├── infra/\n'
    '│   ├── docker/\n'
    '│   ├── migrations/\n'
    '│   └── monitoring/\n'
    '├── assets/\n'
    '│   ├── mascot/\n'
    '│   ├── sprites/\n'
    '│   └── licenses/\n'
    '├── tests/\n'
    '├── .github/\n'
    '├── LICENSE\n'
    '├── SECURITY.md\n'
    '├── CONTRIBUTING.md\n'
    '└── README.md'
))

# ===== Section 23: Requisitos de documentación técnica =====
add_heading('23. Requisitos de documentación técnica', style_h1, level=0, story=story)
story.append(p('Cada módulo debe tener documentación completa:'))
story.extend(bullet_list([
    'README.',
    'Dependencias.',
    'Variables de entorno.',
    'Comandos de desarrollo.',
    'Healthcheck.',
    'Pruebas.',
    'Limitaciones.',
    'Política de datos.',
    'Licencia de dependencias relevantes.',
]))
story.append(p('Cada integración debe documentar:'))
story.extend(bullet_list([
    'API oficial utilizada.',
    'Scopes solicitados.',
    'Datos que lee.',
    'Datos que escribe.',
    'Límites de frecuencia.',
    'Método de revocación.',
    'Fallback.',
    'Riesgos y ToS.',
]))

# ===== Section 24: Decisiones técnicas definitivas =====
add_heading('24. Decisiones técnicas definitivas para la siguiente fase', style_h1, level=0, story=story)
story.append(p('16 decisiones cerradas que guían la implementación:'))
story.extend(numbered_list([
    'Frontend desacoplado con React/Vite.',
    'FastAPI como backend de referencia.',
    'SQLAlchemy/Alembic para SQLite y PostgreSQL.',
    'IndexedDB para PWA; SQLite para local/desktop.',
    'Redis + worker en servidor.',
    'Scheduler separado con idempotencia.',
    'Tauri para desktop.',
    'Capacitor para el primer APK.',
    'GitHub Pages únicamente para demo/documentación.',
    'MCP mediante gateway con policy engine.',
    'Graphify como integración opcional.',
    'Heurística como fallback obligatorio.',
    'No almacenar API keys en localStorage.',
    'No usar node-cron como scheduler distribuido.',
    'No usar Map in-memory como rate limit de producción.',
    'No afirmar zero-knowledge donde exista procesamiento cloud.',
]))

# ===== Section 25: Criterios de aprobación del TRD =====
add_heading('25. Criterios de aprobación del TRD', style_h1, level=0, story=story)
story.append(p('El TRD se considera aprobado cuando el equipo pueda responder afirmativamente a las 12 preguntas:'))
story.extend(numbered_list([
    '¿Se puede ejecutar VNBOT localmente sin servicios cloud?',
    '¿Se puede desplegar en Docker con una ruta clara de backup?',
    '¿El mismo dominio funciona en web, APK y desktop?',
    '¿Los recordatorios sobreviven reinicios y reintentos?',
    '¿La arquitectura separa API, workers y scheduler?',
    '¿Los agentes tienen permisos explícitos?',
    '¿MCP está aislado del dominio crítico?',
    '¿Se puede sustituir el proveedor LLM?',
    '¿El usuario puede exportar y eliminar sus datos?',
    '¿El sistema tiene healthchecks y logs útiles sin filtrar contenido privado?',
    '¿La demo de GitHub Pages funciona sin backend?',
    '¿Los assets y dependencias tienen una estrategia de licencia clara?',
]))

# ===== Section 26: Conclusión =====
add_heading('26. Conclusión', style_h1, level=0, story=story)
story.append(p(
    'VNBOT requiere una arquitectura modular porque combina memoria, recordatorios, IA, '
    'audio, agentes, MCP y distribución multiplataforma. El riesgo principal no es que la '
    'tecnología sea insuficiente; es construir demasiadas capacidades dentro de un único '
    'proceso y una única interfaz sin separar responsabilidades.'
))
story.append(p('La arquitectura propuesta prioriza:'))
story.extend(bullet_list([
    'Un núcleo de dominio pequeño.',
    'Persistencia intercambiable.',
    'Workers durables.',
    'Scheduler confiable.',
    'Proveedores LLM reemplazables.',
    'MCP controlado por políticas.',
    'Clientes multiplataforma con contratos comunes.',
    'Distribución reproducible.',
    'Observabilidad sin invadir la privacidad.',
]))
story.append(callout(
    'El modelo interpreta, el dominio valida, el worker ejecuta y la auditoría explica lo ocurrido.',
    color=ACCENT
))
story.append(p(
    'Con esta separación, VNBOT puede crecer desde una instalación local individual hasta '
    'una plataforma autoalojable con múltiples agentes e integraciones sin sacrificar '
    'control, seguridad ni mantenibilidad.'
))

# ===== Section 27: Estrategia de testing =====
add_heading('27. Estrategia de testing', style_h1, level=0, story=story)
story.append(p(
    'VNBOT requiere una estrategia de testing definida desde el día uno. La cobertura '
    'mínima varía por capa según su criticidad y estabilidad.'
))

add_heading('27.1. Tipos de tests por capa', style_h2, level=1, story=story)
testing_data = [
    ['Capa', 'Tipo', 'Cobertura mínima', 'Herramienta'],
    ['Dominio (memoria, recordatorios, grafo)', 'Unit', '80%', 'Vitest / pytest'],
    ['API endpoints', 'Integration', '70%', 'Supertest / httpx'],
    ['LLM Router', 'Unit + Contract', '60%', 'Vitest + mocks'],
    ['MCP Gateway', 'Contract', '80%', 'Pact / custom'],
    ['Workers / Scheduler', 'Integration', '60%', 'pytest + fixtures'],
    ['Frontend (Web/PWA)', 'Unit + Component', '60%', 'Vitest + Testing Library'],
    ['E2E', 'E2E', 'Flujos críticos', 'Playwright'],
    ['Seguridad', 'SAST/DAST', 'N/A', 'Semgrep + OWASP ZAP'],
]
story.append(make_table(testing_data, col_widths=[55*mm, 30*mm, 30*mm, 55*mm]))

add_heading('27.2. Tests obligatorios por PR', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Todos los tests unitarios pasan.',
    'Tests de integración de módulos afectados pasan.',
    'Linter y typecheck sin errores.',
    'Sin violaciones de seguridad en Semgrep.',
    'Sin secretos en Gitleaks.',
]))

add_heading('27.3. Tests obligatorios por release', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Suite E2E completa pasa.',
    'Benchmarks del grafo no degradan más de 20%.',
    'Accesibilidad (axe-core) sin violaciones AA críticas.',
    'Dependencias auditadas (npm audit / pip-audit).',
]))

# ===== Section 28: Observabilidad =====
add_heading('28. Observabilidad', style_h1, level=0, story=story)

add_heading('28.1. Estándar', style_h2, level=1, story=story)
story.append(p(
    'VNBOT usa OpenTelemetry como estándar de observabilidad. Todos los servicios deben '
    'emitir tres tipos de señales:'
))
story.extend(bullet_list([
    '<b>Traces:</b> para seguir una operación a través de las capas (cliente → API → dominio → storage → LLM/MCP).',
    '<b>Metrics:</b> contadores, histograms y gauges por módulo.',
    '<b>Logs:</b> estructurados en JSON con correlation ID.',
]))

add_heading('28.2. Instrumentación mínima por módulo', style_h2, level=1, story=story)
otel_data = [
    ['Módulo', 'Spans obligatorios', 'Métricas obligatorias'],
    ['API', 'Cada endpoint', 'Latencia P50/P95/P99, error rate, request count'],
    ['Dominio', 'Cada operación de negocio', 'Duración, éxito/fallo'],
    ['LLM Router', 'Cada llamada a LLM', 'Tokens in/out, latencia, coste, provider'],
    ['MCP Gateway', 'Cada tool call', 'Latencia, éxito/fallo, tool name'],
    ['Workers', 'Cada job', 'Duración, reintentos, fallos'],
    ['Scheduler', 'Cada tick', 'Jobs ejecutados, jobs encolados'],
    ['Storage', 'Cada query lenta (>100ms)', 'Query duration, connection pool'],
]
story.append(make_table(otel_data, col_widths=[32*mm, 50*mm, 88*mm]))

add_heading('28.3. Dashboards', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Por release: dashboard con métricas clave del sistema.',
    'Por módulo: vista detallada de spans y métricas.',
    'Alertas: definidas a partir de v0.2 para el modo servidor.',
]))

add_heading('28.4. No recopilar contenido privado', style_h2, level=1, story=story)
story.append(callout(
    'Los traces y logs nunca deben incluir el contenido de memorias, mensajes de chat, ni '
    'datos personales. Solo se registran metadatos operativos (IDs, duraciones, estados, '
    'tipos). Esta regla es no negociable y se valida automáticamente en CI con scanners de '
    'PII en logs.',
    color=SEM_WARNING
))

# ===== Build PDF =====
output_body = '/home/z/my-project/scripts/trd_body.pdf'
doc = TocDocTemplate(
    output_body,
    pagesize=A4,
    leftMargin=20*mm,
    rightMargin=20*mm,
    topMargin=22*mm,
    bottomMargin=22*mm,
    title='VNBOT — Technical Requirements Document',
    author='VNBOT Project',
    subject='TRD v1.0.0-draft — Arquitectura técnica, stack y criterios operativos',
    creator='Z.ai',
)
doc.multiBuild(story, onFirstPage=page_decoration, onLaterPages=page_decoration)
print(f'Body PDF generated: {output_body}')
print(f'Size: {os.path.getsize(output_body) / 1024:.1f} KB')
