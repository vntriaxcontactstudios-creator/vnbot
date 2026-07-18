#!/usr/bin/env python3
"""
VNBOT Esquema Backend — Body PDF generator (ReportLab)
Genera el cuerpo del Esquema Backend con TOC, 40 secciones, tablas, bloques de código y endpoints.
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

# ===== Palette (minimal, VNBOT-consistent) =====
PAGE_BG       = colors.HexColor('#FFFFFF')
SECTION_BG    = colors.HexColor('#eff1f1')
CARD_BG       = colors.HexColor('#f4f6f7')
TABLE_STRIPE  = colors.HexColor('#edeff0')
HEADER_FILL   = colors.HexColor('#1F2937')
BORDER        = colors.HexColor('#b3bfc6')
ACCENT        = colors.HexColor('#0E7490')
ACCENT_2      = colors.HexColor('#7152cb')
TEXT_PRIMARY  = colors.HexColor('#111827')
TEXT_MUTED    = colors.HexColor('#6B7280')
SEM_SUCCESS   = colors.HexColor('#047857')
SEM_WARNING   = colors.HexColor('#B45309')
SEM_ERROR     = colors.HexColor('#B91C1C')
SEM_INFO      = colors.HexColor('#4e769e')

CODE_BG       = colors.HexColor('#0F172A')
CODE_TEXT     = colors.HexColor('#E5F1FF')

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

style_body_left = ParagraphStyle('BodyLeft', parent=style_body, alignment=TA_LEFT)

style_bullet = ParagraphStyle('Bullet', parent=style_body,
    leftIndent=20, bulletIndent=8, spaceAfter=4, alignment=TA_LEFT,
    bulletFontName='NotoSerifSC', bulletFontSize=10.5)

style_endpoint = ParagraphStyle('Endpoint', parent=style_body,
    fontName='Mono', fontSize=10, leading=14,
    textColor=ACCENT, spaceBefore=6, spaceAfter=6,
    backColor=CARD_BG, leftIndent=12, rightIndent=12,
    borderPadding=6, alignment=TA_LEFT)

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
                style_cmds.append(('BACKGROUND', (0,i), (-1,i), TABLE_STRIPE))
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

def endpoint(text):
    """Highlight an HTTP endpoint signature."""
    return Paragraph(text, style_endpoint)

def code_block(code_text):
    escaped = code_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    lines = escaped.split('\n')
    html_lines = []
    for line in lines:
        if not line.strip():
            html_lines.append('&nbsp;')
        else:
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
    canv.drawString(20*mm, 12*mm, 'VNBOT // BACKEND v1.0.0-draft')
    canv.drawRightString(190*mm, 12*mm, f'{page_num}')
    canv.setStrokeColor(BORDER)
    canv.setLineWidth(0.4)
    canv.line(20*mm, 15*mm, 190*mm, 15*mm)
    if page_num > 1:
        canv.setFont('Mono', 7.5)
        canv.setFillColor(TEXT_MUTED)
        canv.drawString(20*mm, 285*mm, 'VNBOT — Esquema Backend')
        canv.drawRightString(190*mm, 285*mm, '03-ESQUEMA-BACKEND-VNBOT.md')
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

# ===== 1. Propósito =====
add_heading('1. Propósito', style_h1, level=0, story=story)
story.append(p(
    'Este documento especifica la estructura del backend de VNBOT: servicios, módulos, '
    'entidades, API, eventos, trabajos asíncronos, scheduler, memoria, grafo, agentes, MCP, '
    'notificaciones, archivos, healthchecks, errores y reglas de seguridad. Es la referencia '
    'detallada que falta entre el TRD (decisión técnica) y la implementación concreta de código.'
))
story.append(p('El backend debe soportar cuatro formas de ejecución, cada una con componentes distintos:'))
story.extend(bullet_list([
    '<b>Local:</b> un usuario, SQLite y servicios mínimos.',
    '<b>Servidor personal:</b> varios dispositivos, PostgreSQL, Redis y workers.',
    '<b>Servidor multiusuario:</b> workspaces aislados y servicios replicables.',
    '<b>Modo híbrido:</b> datos locales con sincronización opcional.',
]))
story.append(callout(
    'El cliente solicita. La API autentica y valida. El dominio decide. La cola ejecuta '
    'trabajos durables. Las integraciones actúan con permisos. La auditoría registra el resultado.',
    color=ACCENT
))

# ===== 2. Objetivos del backend =====
add_heading('2. Objetivos del backend', style_h1, level=0, story=story)

add_heading('2.1. Objetivos funcionales', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Gestionar usuarios, sesiones y workspaces.',
    'Procesar mensajes de chat.',
    'Interpretar intenciones mediante LLM o heurística.',
    'Guardar memorias y relaciones.',
    'Consultar el grafo personal.',
    'Crear recordatorios persistentes.',
    'Ejecutar notificaciones sin duplicados.',
    'Procesar audio y archivos de forma asíncrona.',
    'Gestionar agentes y skills.',
    'Conectar herramientas MCP.',
    'Maintener auditoría de acciones.',
    'Exportar e importar datos.',
    'Exponer healthchecks.',
]))

add_heading('2.2. Objetivos operativos', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Poder reiniciar API y workers sin perder trabajos confirmados.',
    'Permitir reintentos seguros.',
    'Poder sustituir SQLite por PostgreSQL.',
    'Poder reemplazar Redis por una implementación local limitada.',
    'Poder añadir proveedores LLM sin cambiar la lógica de dominio.',
    'Poder añadir integraciones como plugins/adaptadores.',
    'Poder ejecutar la aplicación en Docker.',
]))

add_heading('2.3. No objetivos del backend inicial', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Ejecutar código arbitrario del usuario.',
    'Automatización financiera.',
    'Scraping de cuentas personales.',
    'Escucha permanente del micrófono.',
    'Acceso universal al filesystem.',
    'Envío automático de mensajes a terceros sin consentimiento.',
    'Orquestación multiagente totalmente autónoma.',
]))

# ===== 3. Arquitectura de servicios =====
add_heading('3. Arquitectura de servicios', style_h1, level=0, story=story)

add_heading('3.1. Vista general', style_h2, level=1, story=story)
story.append(p(
    'La arquitectura del backend separa la API stateless de los workers durables y del '
    'scheduler idempotente. Esta separación permite reiniciar cualquier componente sin perder '
    'trabajos confirmados y permite escalar horizontalmente solo los componentes que lo necesiten.'
))
story.append(code_block(
    '                    ┌───────────────────┐\n'
    '                    │ Web / APK / Tauri │\n'
    '                    │       / CLI       │\n'
    '                    └─────────┬─────────┘\n'
    '                              │ HTTPS / WebSocket / IPC\n'
    '                              ▼\n'
    '┌─────────────────────────────────────────────────────────────┐\n'
    '│                         VNBOT API                           │\n'
    '│ Auth · Chat · Memory · Graph · Reminders · Agents · Admin   │\n'
    '└──────┬───────────────┬───────────────┬──────────────────────┘\n'
    '       │               │               │\n'
    '       ▼               ▼               ▼\n'
    '┌────────────┐  ┌──────────────┐  ┌─────────────────┐\n'
    '│ PostgreSQL │  │ Redis / Queue│  │ Object Storage  │\n'
    '│ SQLite     │  │ locks/cache  │  │ MinIO / S3      │\n'
    '└────────────┘  └──────┬───────┘  └─────────────────┘\n'
    '                       │\n'
    '              ┌────────▼────────┐\n'
    '              │ Worker/Scheduler │\n'
    '              │ audio · jobs ·   │\n'
    '              │ reminders · sync │\n'
    '              └────────┬─────────┘\n'
    '                       │\n'
    '             ┌─────────▼─────────┐\n'
    '             │ MCP Gateway / LLM │\n'
    '             │ Router / Channels │\n'
    '             └───────────────────┘'
))

add_heading('3.2. Servicios del MVP', style_h2, level=1, story=story)
serv_data = [
    ['Servicio', 'Responsabilidad'],
    ['vnbot-api', 'Servicio HTTP principal. Gestiona autenticación, comandos, consultas, confirmaciones, memoria, recordatorios y administración.'],
    ['vnbot-worker', 'Procesa tareas largas o reintentables: audio, embeddings, notificaciones, consolidación, backups y sincronización.'],
    ['vnbot-scheduler', 'Calcula qué ocurrencias de recordatorios deben encolarse. Debe ejecutarse como instancia única o usar locks distribuidos.'],
    ['vnbot-mcp-gateway', 'Gestiona servidores MCP externos, schemas, scopes, timeouts, policy engine y auditoría.'],
]
story.append(make_table(serv_data, col_widths=[40*mm, 130*mm]))
story.append(Spacer(1, 8))
story.append(p(
    'En una instalación local estos servicios pueden ejecutarse dentro de un proceso '
    'supervisado, pero deben mantener límites de módulos claros para permitir la separación '
    'cuando se mueva a servidor.'
))

add_heading('3.3. Servicios posteriores', style_h2, level=1, story=story)
story.extend(bullet_list([
    'notification-service dedicado.',
    'transcription-service separado si se necesita GPU.',
    'embedding-service local.',
    'sync-service multi-dispositivo.',
    'community-plugin-registry.',
    'observability-stack.',
]))
story.append(callout(
    'No se deben extraer microservicios únicamente por moda. La separación se hará cuando '
    'exista una necesidad de escalado, seguridad o aislamiento real.',
    color=SEM_WARNING
))

# ===== 4. Estructura de módulos del API =====
add_heading('4. Estructura de módulos del API', style_h1, level=0, story=story)
story.append(p(
    'El servicio API se organiza en una arquitectura hexagonal con separación clara entre '
    'capas. La regla de dependencias es estricta: el dominio nunca debe importar frameworks '
    'de infraestructura.'
))
story.append(code_block(
    'services/api/\n'
    '├── app/\n'
    '│   ├── main.py\n'
    '│   ├── config.py\n'
    '│   ├── dependencies.py\n'
    '│   ├── middleware/\n'
    '│   │   ├── auth.py\n'
    '│   │   ├── request_id.py\n'
    '│   │   ├── rate_limit.py\n'
    '│   │   └── error_handler.py\n'
    '│   ├── api/\n'
    '│   │   └── v1/\n'
    '│   │       ├── auth.py\n'
    '│   │       ├── chat.py\n'
    '│   │       ├── memories.py\n'
    '│   │       ├── graph.py\n'
    '│   │       ├── reminders.py\n'
    '│   │       ├── agents.py\n'
    '│   │       ├── skills.py\n'
    '│   │       ├── integrations.py\n'
    '│   │       ├── audio.py\n'
    '│   │       ├── files.py\n'
    '│   │       ├── exports.py\n'
    '│   │       └── health.py\n'
    '│   ├── domain/\n'
    '│   │   ├── memories/\n'
    '│   │   ├── reminders/\n'
    '│   │   ├── agents/\n'
    '│   │   ├── operations/\n'
    '│   │   └── policies/\n'
    '│   ├── application/\n'
    '│   │   ├── commands/\n'
    '│   │   ├── queries/\n'
    '│   │   └── services/\n'
    '│   ├── infrastructure/\n'
    '│   │   ├── db/\n'
    '│   │   ├── queue/\n'
    '│   │   ├── llm/\n'
    '│   │   ├── mcp/\n'
    '│   │   ├── storage/\n'
    '│   │   └── notifications/\n'
    '│   └── schemas/\n'
    '├── migrations/\n'
    '└── tests/'
))

add_heading('4.1. Regla de dependencias', style_h2, level=1, story=story)
story.append(code_block(
    'api → application → domain\n'
    'infrastructure → application/domain ports'
))
story.append(callout(
    'El dominio no debe importar FastAPI, Redis, SQLAlchemy, proveedores LLM ni SDKs externos. '
    'Esta regla protege el núcleo de cambios de infraestructura.',
    color=ACCENT
))

# ===== 5. Contextos de dominio =====
add_heading('5. Contextos de dominio', style_h1, level=0, story=story)
story.append(p(
    'El dominio se divide en 7 contextos delimitados siguiendo Domain-Driven Design. Cada '
    'contexto tiene sus propias entidades, reglas y repositorios. Los contextos se comunican '
    'mediante eventos y comandos tipados, no mediante llamadas directas acopladas.'
))

ctx_data = [
    ['Contexto', 'Gestiona'],
    ['Identity', 'Usuarios, sesiones, workspaces, roles, MFA posterior, recuperación de cuenta.'],
    ['Memory', 'Memorias, nodos, aristas, procedencia, confianza, sensibilidad, expiración, correcciones, borrado.'],
    ['Reminder', 'Recordatorios, reglas de recurrencia, ocurrencias, canales, estados de entrega, posponer/completar/cancelar.'],
    ['Agent', 'Agentes, prompts, modelos, skills, presupuestos, nivel de autonomía, herramientas y permisos.'],
    ['Operation', 'Ciclo de vida de toda acción iniciada por usuario o agente.'],
    ['Integration', 'Integraciones, OAuth, tokens, scopes, healthchecks, revocación.'],
    ['File', 'Audios, imágenes, documentos, retención, cifrado, referencias a memorias.'],
]
story.append(make_table(ctx_data, col_widths=[35*mm, 135*mm]))

# ===== 6. Identidad, usuarios y workspaces =====
add_heading('6. Identidad, usuarios y workspaces', style_h1, level=0, story=story)

add_heading('6.1. Usuario', style_h2, level=1, story=story)
story.append(code_block(
    'User\n'
    '- id\n'
    '- email nullable en modo local\n'
    '- display_name\n'
    '- password_hash nullable\n'
    '- timezone\n'
    '- locale\n'
    '- status\n'
    '- created_at\n'
    '- updated_at'
))

add_heading('6.2. Workspace', style_h2, level=1, story=story)
story.append(p(
    'Un workspace separa contextos y permisos. Permite que un usuario tenga espacios '
    'distintos para Personal, Trabajo, Estudio, Familia o Proyecto VNBOT sin mezclar datos.'
))
story.append(code_block(
    'Workspace\n'
    '- id\n'
    '- owner_user_id\n'
    '- name\n'
    '- type\n'
    '- settings_json\n'
    '- created_at\n'
    '- updated_at'
))

add_heading('6.3. Roles', style_h2, level=1, story=story)
story.extend(bullet_list([
    '<b>owner</b> — propietario del workspace, control total.',
    '<b>admin</b> — administración sin poder eliminar el workspace.',
    '<b>member</b> — uso completo de memoria y recordatorios.',
    '<b>viewer</b> — solo lectura.',
]))
story.append(p(
    'El modo personal puede utilizar solo owner, pero el modelo debe permitir expansión '
    'para workspaces compartidos futuros.'
))

add_heading('6.4. Autorización', style_h2, level=1, story=story)
story.append(callout(
    'Cada endpoint debe obtener el workspace desde la sesión y verificar que el recurso '
    'pertenece a dicho workspace. Nunca se debe aceptar solamente un workspace_id enviado '
    'por el cliente.',
    color=SEM_WARNING
))

# ===== 7. Modelo de operaciones =====
add_heading('7. Modelo de operaciones', style_h1, level=0, story=story)

add_heading('7.1. Propósito', style_h2, level=1, story=story)
story.append(p(
    'Una operación representa una intención completa: crear un recordatorio, guardar una '
    'memoria, ejecutar una herramienta o procesar audio. El modelo de operaciones da '
    'trazabilidad completa de cada acción del usuario y del agente.'
))
story.append(code_block(
    'Operation\n'
    '- id\n'
    '- workspace_id\n'
    '- user_id\n'
    '- agent_id nullable\n'
    '- type\n'
    '- status\n'
    '- input_ref\n'
    '- output_ref\n'
    '- risk_level\n'
    '- requires_confirmation\n'
    '- confirmed_at\n'
    '- created_at\n'
    '- updated_at\n'
    '- expires_at'
))

add_heading('7.2. Estados', style_h2, level=1, story=story)
story.append(p('Cada operación pasa por una máquina de 12 estados:'))
story.append(code_block(
    'RECEIVED\n'
    'CLASSIFYING\n'
    'PROPOSED\n'
    'NEEDS_CLARIFICATION\n'
    'WAITING_CONFIRMATION\n'
    'QUEUED\n'
    'EXECUTING\n'
    'SUCCEEDED\n'
    'RETRYING\n'
    'FAILED\n'
    'CANCELLED\n'
    'EXPIRED'
))

add_heading('7.3. Idempotencia', style_h2, level=1, story=story)
story.append(p('Cada comando mutable acepta Idempotency-Key:'))
story.append(endpoint('POST /api/v1/reminders'))
story.append(endpoint('Idempotency-Key: reminder-create-9f43'))
story.append(p(
    'La API debe guardar el resultado asociado a la clave durante un periodo definido. Si '
    'llega la misma operación, devuelve el resultado original en lugar de crear otro recurso. '
    'Esto es crítico para reintentos tras fallos de red y para evitar duplicados en '
    'recordatorios recurrentes.'
))

add_heading('7.4. Expiración', style_h2, level=1, story=story)
story.append(p(
    'Las propuestas de confirmación deben caducar. Una acción confirmada demasiado tarde '
    'debe volver a validarse, especialmente si contiene una fecha, precio, disponibilidad o '
    'permiso externo. La expiración protege al usuario de confirmar operaciones con contexto '
    'obsoleto.'
))

# ===== 8. API pública versionada =====
add_heading('8. API pública versionada', style_h1, level=0, story=story)
story.append(endpoint('Base: /api/v1'))
story.append(p('Formato general de respuesta exitosa:'))
story.append(code_block(
    '{\n'
    '  "data": {},\n'
    '  "meta": {\n'
    '    "request_id": "req_123",\n'
    '    "operation_id": "op_123"\n'
    '  }\n'
    '}'
))
story.append(p('Formato general de error:'))
story.append(code_block(
    '{\n'
    '  "error": {\n'
    '    "code": "REMINDER_AMBIGUOUS_TIME",\n'
    '    "message": "Falta la hora del recordatorio",\n'
    '    "details": {\n'
    '      "field": "due_at"\n'
    '    },\n'
    '    "retryable": false,\n'
    '    "request_id": "req_123"\n'
    '  }\n'
    '}'
))

# ===== 9. Endpoints de autenticación =====
add_heading('9. Endpoints de autenticación', style_h1, level=0, story=story)

story.append(endpoint('POST /auth/register'))
story.append(p('Crea una cuenta en un servidor remoto. Entrada:'))
story.append(code_block(
    '{\n'
    '  "email": "usuario@example.com",\n'
    '  "password": "...",\n'
    '  "display_name": "Usuario"\n'
    '}'
))
story.append(p('Requisitos:'))
story.extend(bullet_list([
    'Validar email.',
    'Aplicar rate limit.',
    'Hash Argon2id.',
    'No revelar si un email existe en contextos sensibles.',
    'Enviar verificación si el despliegue lo requiere.',
]))

story.append(endpoint('POST /auth/login'))
story.append(p('Crea sesión segura y devuelve cookies o tokens según el cliente.'))

story.append(endpoint('POST /auth/logout'))
story.append(p('Revoca la sesión actual.'))

story.append(endpoint('POST /auth/refresh'))
story.append(p('Rota refresh token cuando aplique.'))

story.append(endpoint('GET /auth/me'))
story.append(p('Devuelve usuario y workspaces permitidos, nunca secretos.'))

story.append(endpoint('POST /auth/lock'))
story.append(p('Bloquea la bóveda de la sesión local o solicita reautenticación.'))

# ===== 10. Endpoints de chat =====
add_heading('10. Endpoints de chat', style_h1, level=0, story=story)

story.append(endpoint('POST /chat'))
story.append(p('Entrada:'))
story.append(code_block(
    '{\n'
    '  "conversation_id": "conv_123",\n'
    '  "agent_id": "agent_default",\n'
    '  "content": "Recuérdame pagar la electricidad mañana a las 8",\n'
    '  "attachments": [],\n'
    '  "client_context": {\n'
    '    "timezone": "America/Caracas",\n'
    '    "platform": "web"\n'
    '  }\n'
    '}'
))
story.append(p('Proceso:'))
story.extend(numbered_list([
    'Validar usuario y workspace.',
    'Crear mensaje.',
    'Crear operación.',
    'Clasificar intención.',
    'Recuperar contexto autorizado.',
    'Generar propuesta estructurada.',
    'Evaluar riesgo.',
    'Responder con texto y/o operation_id.',
]))
story.append(p('Respuesta posible:'))
story.append(code_block(
    '{\n'
    '  "data": {\n'
    '    "message_id": "msg_123",\n'
    '    "operation_id": "op_123",\n'
    '    "assistant_text": "Puedo recordarte pagar la electricidad el 17 de julio de 2026 a las 08:00.",\n'
    '    "proposal": {\n'
    '      "type": "create_reminder",\n'
    '      "title": "Pagar la electricidad",\n'
    '      "due_at": "2026-07-17T08:00:00-04:00",\n'
    '      "timezone": "America/Caracas"\n'
    '    },\n'
    '    "status": "WAITING_CONFIRMATION"\n'
    '  }\n'
    '}'
))

story.append(endpoint('GET /chat/conversations'))
story.append(p('Lista conversaciones paginadas del workspace.'))

story.append(endpoint('GET /chat/conversations/{id}'))
story.append(p('Devuelve mensajes con paginación. Las partes sensibles deben respetar la política de retención.'))

story.append(endpoint('POST /chat/operations/{id}/confirm'))
story.append(p('Confirma una propuesta. La API debe volver a validar permisos, fechas y disponibilidad antes de ejecutar.'))

story.append(endpoint('POST /chat/operations/{id}/cancel'))
story.append(p('Cancela una propuesta o job si todavía es cancelable.'))

# ===== 11. Endpoints de memoria =====
add_heading('11. Endpoints de memoria', style_h1, level=0, story=story)

story.append(endpoint('POST /memory/nodes'))
story.append(p('Crea un nodo explícito. Ejemplo:'))
story.append(code_block(
    '{\n'
    '  "type": "preference",\n'
    '  "label": "Horario preferido de reuniones",\n'
    '  "content": "Prefiero reuniones después de las 16:00",\n'
    '  "sensitivity": "personal",\n'
    '  "provenance": "explicit_user_input"\n'
    '}'
))

story.append(endpoint('GET /memory/nodes/{id}'))
story.append(p('Devuelve nodo, procedencia y relaciones autorizadas.'))

story.append(endpoint('PATCH /memory/nodes/{id}'))
story.append(p('Permite corregir contenido, label, tipo, sensibilidad o expiración. Toda modificación crea un evento de auditoría.'))

story.append(endpoint('DELETE /memory/nodes/{id}'))
story.append(p('Debe aplicar política de borrado:'))
story.extend(bullet_list([
    'Marcar como eliminado.',
    'Eliminar relaciones dependientes.',
    'Invalidar índices.',
    'Programar borrado de embeddings y archivos relacionados.',
    'Confirmar al usuario qué fue eliminado.',
]))

story.append(endpoint('GET /memory/search'))
story.append(p('Parámetros:'))
story.append(code_block(
    'q\n'
    'mode=text|semantic|hybrid|graph\n'
    'limit\n'
    'cursor\n'
    'type\n'
    'sensitivity\n'
    'created_after\n'
    'created_before'
))
story.append(p('La respuesta debe incluir relevancia, fuente y nivel de confianza.'))

story.append(endpoint('POST /memory/edges'))
story.append(p('Crea relación entre nodos. Las aristas inferidas deben marcarse como inferred y no como explicit.'))

story.append(endpoint('DELETE /memory/edges/{id}'))
story.append(p('Elimina o invalida una relación.'))

# ===== 12. Endpoints del grafo =====
add_heading('12. Endpoints del grafo', style_h1, level=0, story=story)

story.append(endpoint('GET /graph/subgraph'))
story.append(p('Entrada:'))
story.append(code_block(
    'root_node_id\n'
    'max_depth=2\n'
    'max_nodes=50\n'
    'relation_types[]=RELATED_TO'
))
story.append(p('Respuesta:'))
story.append(code_block(
    '{\n'
    '  "data": {\n'
    '    "nodes": [],\n'
    '    "edges": [],\n'
    '    "truncated": false,\n'
    '    "query": {\n'
    '      "root": "node_123",\n'
    '      "depth": 2\n'
    '    }\n'
    '  }\n'
    '}'
))

story.append(endpoint('GET /graph/stats'))
story.append(p('Devuelve contadores agregados del workspace:'))
story.extend(bullet_list([
    'Total de nodos.',
    'Total de relaciones.',
    'Tipos.',
    'Memorias expiradas.',
    'Índices pendientes.',
]))

story.append(endpoint('POST /graph/rebuild'))
story.append(p('Solo para administración o usuario autorizado. Encola reindexación; no bloquea la API.'))

story.append(endpoint('POST /graph/merge'))
story.append(p('Fusiona entidades duplicadas con confirmación. Debe conservar procedencia e historial.'))

# ===== 13. Endpoints de recordatorios =====
add_heading('13. Endpoints de recordatorios', style_h1, level=0, story=story)

story.append(endpoint('POST /reminders'))
story.append(p('Crea un recordatorio con una regla explícita:'))
story.append(code_block(
    '{\n'
    '  "title": "Revisar presupuesto",\n'
    '  "description": "Comprobar gastos de la semana",\n'
    '  "due_at": "2026-07-20T09:00:00-04:00",\n'
    '  "timezone": "America/Caracas",\n'
    '  "recurrence": {\n'
    '    "frequency": "weekly",\n'
    '    "by_weekday": ["MO"]\n'
    '  },\n'
    '  "priority": "normal",\n'
    '  "channel": "push"\n'
    '}'
))

story.append(endpoint('GET /reminders'))
story.append(p('Filtros disponibles:'))
story.append(code_block(
    'status\n'
    'from\n'
    'to\n'
    'priority\n'
    'channel\n'
    'cursor\n'
    'limit'
))

story.append(endpoint('GET /reminders/{id}'))
story.append(p('Incluye regla, próxima ocurrencia, historial y estado.'))

story.append(endpoint('PATCH /reminders/{id}'))
story.append(p('Toda modificación debe actualizar futuras ocurrencias sin alterar entregas históricas.'))

story.append(endpoint('POST /reminders/{id}/complete'))
story.append(p('Completa la ocurrencia actual o el recordatorio completo según el payload.'))

story.append(endpoint('POST /reminders/{id}/snooze'))
story.append(p('Entrada:'))
story.append(code_block(
    '{\n'
    '  "until": "2026-07-17T18:00:00-04:00"\n'
    '}'
))

story.append(endpoint('POST /reminders/{id}/cancel'))
story.append(p('Cancela futuras ocurrencias y conserva historial.'))

story.append(endpoint('GET /reminders/{id}/deliveries'))
story.append(p('Muestra intentos y resultados sin incluir credenciales ni contenido innecesario.'))

# ===== 14. Motor de recordatorios =====
add_heading('14. Motor de recordatorios', style_h1, level=0, story=story)

add_heading('14.1. Separación entre regla y ocurrencia', style_h2, level=1, story=story)
story.append(p(
    'Un recordatorio recurrente no debe duplicarse como cientos de filas sin control. La '
    'separación entre regla (Recurrence Rule) y ocurrencias (Occurrences) permite generar '
    'instancias con anticipación controlada.'
))
story.append(code_block(
    'Reminder\n'
    '  └── Recurrence Rule\n'
    '        ├── Occurrence 2026-07-20\n'
    '        ├── Occurrence 2026-07-27\n'
    '        └── Occurrence 2026-08-03'
))
story.append(p(
    'Las ocurrencias pueden crearse con una ventana anticipada, por ejemplo 30 días, y '
    'generarse progresivamente por el scheduler.'
))

add_heading('14.2. Scheduler', style_h2, level=1, story=story)
story.append(p('Cada ciclo del scheduler ejecuta 5 pasos:'))
story.extend(numbered_list([
    'Busca recordatorios activos.',
    'Calcula ocurrencias próximas según timezone.',
    'Adquiere lock.',
    'Crea job idempotente.',
    'Libera lock.',
]))

add_heading('14.3. Delivery worker', style_h2, level=1, story=story)
story.append(p('El worker de entrega sigue 8 pasos:'))
story.extend(numbered_list([
    'Toma job.',
    'Comprueba que la ocurrencia sigue activa.',
    'Comprueba que no fue entregada.',
    'Comprueba ventana de silencio.',
    'Selecciona canal.',
    'Envía notificación.',
    'Registra resultado.',
    'Reintenta si el error es temporal.',
]))

add_heading('14.4. Canales', style_h2, level=1, story=story)
story.append(p('Cada canal implementa una interfaz común:'))
story.append(code_block(
    'class NotificationChannel(Protocol):\n'
    '    async def send(self, notification: Notification) -> DeliveryResult: ...\n'
    '    async def healthcheck(self) -> HealthStatus: ...'
))

# ===== 15. Jobs y cola =====
add_heading('15. Jobs y cola', style_h1, level=0, story=story)

add_heading('15.1. Tipos de job', style_h2, level=1, story=story)
story.append(p('El sistema maneja 14 tipos de jobs asíncronos:'))
story.append(code_block(
    'transcribe_audio\n'
    'extract_document\n'
    'embed_memory\n'
    'index_memory\n'
    'consolidate_memory\n'
    'send_reminder\n'
    'send_notification\n'
    'sync_mcp\n'
    'sync_calendar\n'
    'generate_briefing\n'
    'create_backup\n'
    'restore_backup\n'
    'purge_expired_data\n'
    'rebuild_graph'
))

add_heading('15.2. Estructura', style_h2, level=1, story=story)
story.append(p('Estructura JSON de un job en cola:'))
story.append(code_block(
    '{\n'
    '  "id": "job_123",\n'
    '  "type": "send_reminder",\n'
    '  "payload_ref": "reminder_occurrence_123",\n'
    '  "workspace_id": "ws_123",\n'
    '  "priority": "normal",\n'
    '  "attempt": 1,\n'
    '  "max_attempts": 5,\n'
    '  "status": "running",\n'
    '  "idempotency_key": "occurrence_123_push",\n'
    '  "trace_id": "trace_123"\n'
    '}'
))

add_heading('15.3. Prioridades', style_h2, level=1, story=story)
prio_data = [
    ['Prioridad', 'Uso'],
    ['critical', 'Operaciones de seguridad o restauración'],
    ['high', 'Recordatorios próximos'],
    ['normal', 'Transcripción y embeddings'],
    ['low', 'Consolidación y estadísticas'],
]
story.append(make_table(prio_data, col_widths=[30*mm, 140*mm]))

add_heading('15.4. Dead-letter queue', style_h2, level=1, story=story)
story.append(p(
    'Un job que supera sus reintentos pasa a DLQ. El usuario o administrador puede ver el '
    'error resumido, reintentar, cancelar, corregir configuración o exportar el incidente '
    'para análisis.'
))

# ===== 16. Audio y archivos =====
add_heading('16. Audio y archivos', style_h1, level=0, story=story)

add_heading('16.1. Endpoint de subida', style_h2, level=1, story=story)
story.append(endpoint('POST /files/upload'))
story.append(p('Recibe un archivo temporal con:'))
story.extend(bullet_list([
    'Tamaño máximo.',
    'MIME permitido.',
    'Hash.',
    'Usuario/workspace.',
    'Política de retención.',
]))
story.append(callout(
    'Nunca se debe confiar solo en la extensión del archivo. El MIME type debe validarse '
    'realmente con magic bytes, no solo con el Content-Type header.',
    color=SEM_WARNING
))

add_heading('16.2. Audio — estados', style_h2, level=1, story=story)
story.append(p('Pipeline de estados del audio:'))
story.append(code_block(
    'uploaded\n'
    '→ validated\n'
    '→ queued_transcription\n'
    '→ transcribing\n'
    '→ transcript_ready\n'
    '→ user_review\n'
    '→ processed\n'
    '→ deleted/retained'
))

add_heading('16.3. Política de retención', style_h2, level=1, story=story)
story.append(p('El usuario debe elegir entre 4 opciones:'))
story.extend(bullet_list([
    'Eliminar audio después de transcribir.',
    'Conservar audio junto a la memoria.',
    'Conservar durante un periodo.',
    'No guardar audio en ningún servidor.',
]))

add_heading('16.4. Documentos e imágenes', style_h2, level=1, story=story)
story.append(p(
    'Los documentos deben procesarse en worker. El OCR o extracción no debe bloquear la '
    'request HTTP. La respuesta inicial debe devolver job_id y estado para que el cliente '
    'pueda polling o recibir WebSocket update.'
))

# ===== 17. Agentes, skills y policy engine =====
add_heading('17. Agentes, skills y policy engine', style_h1, level=0, story=story)

add_heading('17.1. Agente', style_h2, level=1, story=story)
story.append(code_block(
    'Agent\n'
    '- id\n'
    '- workspace_id\n'
    '- name\n'
    '- description\n'
    '- system_prompt\n'
    '- model_config_json\n'
    '- autonomy_level\n'
    '- budget_json\n'
    '- avatar_id\n'
    '- status'
))

add_heading('17.2. Skill', style_h2, level=1, story=story)
story.append(code_block(
    'Skill\n'
    '- id\n'
    '- version\n'
    '- name\n'
    '- input_schema\n'
    '- output_schema\n'
    '- risk_level\n'
    '- required_tools\n'
    '- memory_scopes\n'
    '- confirmation_policy'
))

add_heading('17.3. Policy decision', style_h2, level=1, story=story)
story.append(p('El policy engine devuelve decisiones estructuradas:'))
story.append(code_block(
    '{\n'
    '  "allowed": false,\n'
    '  "reason": "TOOL_REQUIRES_CONFIRMATION",\n'
    '  "risk_level": "high",\n'
    '  "required_action": "user_confirmation"\n'
    '}'
))

add_heading('17.4. Tool call', style_h2, level=1, story=story)
story.append(p('Cada llamada a herramienta debe registrar:'))
story.extend(bullet_list([
    'Agente.',
    'Skill.',
    'Herramienta.',
    'Input filtrado.',
    'Scope.',
    'Resultado.',
    'Duración.',
    'Error.',
    'Confirmación.',
]))
story.append(p(
    'Los inputs completos pueden omitirse o cifrarse si contienen datos sensibles. La '
    'auditoría no debe convertirse en una filtración de datos privados.'
))

# ===== 18. MCP Gateway =====
add_heading('18. MCP Gateway', style_h1, level=0, story=story)

add_heading('18.1. Registro', style_h2, level=1, story=story)
story.append(endpoint('POST /integrations/mcp'))
story.append(p('Entrada:'))
story.append(code_block(
    '{\n'
    '  "name": "graphify-local",\n'
    '  "transport": "streamable_http",\n'
    '  "endpoint": "http://localhost:8000/mcp",\n'
    '  "auth_type": "bearer",\n'
    '  "scopes": ["graph.read"]\n'
    '}'
))
story.append(callout(
    'El token real no debe devolverse después de guardarse. La respuesta POST no debe '
    'incluir el secret en ningún campo.',
    color=SEM_WARNING
))

add_heading('18.2. Handshake', style_h2, level=1, story=story)
story.append(p('El gateway debe almacenar tras el handshake:'))
story.extend(bullet_list([
    'Protocol version.',
    'Server name.',
    'Server version.',
    'Capabilities.',
    'Tools.',
    'Resources.',
    'Fecha de último healthcheck.',
]))

add_heading('18.3. Scopes iniciales', style_h2, level=1, story=story)
story.append(code_block(
    'graph.read\n'
    'graph.write\n'
    'memory.read\n'
    'memory.write\n'
    'calendar.read\n'
    'calendar.write\n'
    'email.read\n'
    'email.draft\n'
    'email.send\n'
    'filesystem.read\n'
    'filesystem.write\n'
    'web.fetch'
))
story.append(callout(
    'email.send, filesystem.write y acciones equivalentes requieren confirmación fuerte '
    'y no se habilitan por defecto.',
    color=SEM_ERROR
))

add_heading('18.4. Aislamiento', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Timeouts.',
    'Límite de tamaño de respuestas.',
    'Límite de llamadas por operación.',
    'Red permitida.',
    'No pasar todos los secretos del proceso a un MCP.',
    'Credenciales específicas por integración.',
    'Revocación.',
]))

# ===== 19. LLM Router y contexto =====
add_heading('19. LLM Router y contexto', style_h1, level=0, story=story)

add_heading('19.1. Pipeline', style_h2, level=1, story=story)
story.append(code_block(
    'Intent classifier\n'
    '  ↓\n'
    'Context retriever\n'
    '  ↓\n'
    'Prompt builder\n'
    '  ↓\n'
    'Provider adapter\n'
    '  ↓\n'
    'Structured output validator\n'
    '  ↓\n'
    'Policy engine'
))

add_heading('19.2. Contexto mínimo', style_h2, level=1, story=story)
story.append(p('El retriever debe enviar solamente:'))
story.extend(bullet_list([
    'Memorias relevantes.',
    'Relaciones necesarias.',
    'Preferencias aplicables.',
    'Estado de tarea relacionado.',
    'Instrucciones de la skill.',
]))
story.append(callout(
    'No se debe enviar el grafo completo ni todo el historial de conversación por defecto. '
    'El principio de mínimo contexto protege privacidad y reduce coste.',
    color=ACCENT
))

add_heading('19.3. Structured output', style_h2, level=1, story=story)
story.append(p('Las salidas deben validarse con JSON Schema/Pydantic:'))
story.append(code_block(
    '{\n'
    '  "intent": "create_reminder",\n'
    '  "confidence": 0.96,\n'
    '  "fields": {\n'
    '    "title": "Pagar la electricidad",\n'
    '    "due_at": "2026-07-17T08:00:00-04:00"\n'
    '  },\n'
    '  "needs_clarification": false\n'
    '}'
))
story.append(callout(
    'Una respuesta que no valida no puede pasar al ejecutor. Siempre fallback a heurística '
    'o solicitar clarificación al usuario.',
    color=SEM_WARNING
))

# ===== 20. Persistencia y repositorios =====
add_heading('20. Persistencia y repositorios', style_h1, level=0, story=story)

add_heading('20.1. Repositories', style_h2, level=1, story=story)
story.append(p('Interfaces esperadas (Protocol pattern):'))
story.append(code_block(
    'class MemoryRepository(Protocol):\n'
    '    async def create(self, node: MemoryNode) -> MemoryNode: ...\n'
    '    async def get(self, node_id: str) -> MemoryNode | None: ...\n'
    '    async def search(self, query: MemoryQuery) -> list[MemoryNode]: ...\n'
    '    async def delete(self, node_id: str) -> None: ...'
))

add_heading('20.2. Transacciones', style_h2, level=1, story=story)
story.append(p(
    'Las operaciones que creen un recordatorio y su primera ocurrencia deben ser '
    'transaccionales. Las operaciones asíncronas posteriores pueden ser jobs independientes.'
))

add_heading('20.3. Soft delete', style_h2, level=1, story=story)
story.append(p('Para memorias y relaciones se recomienda soft delete inicial para permitir:'))
story.extend(bullet_list([
    'Auditoría.',
    'Recuperación limitada.',
    'Propagación a índices.',
    'Confirmación de borrado.',
]))
story.append(p(
    'Después del periodo definido, un job de purga elimina definitivamente el contenido.'
))

add_heading('20.4. Migraciones', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Alembic.',
    'Migraciones reversibles cuando sea posible.',
    'Backup antes de cambios destructivos.',
    'Versionado de schema.',
    'No cambiar tablas manualmente en producción.',
]))

# ===== 21. Caching e índices =====
add_heading('21. Caching e índices', style_h1, level=0, story=story)

add_heading('21.1. Redis', style_h2, level=1, story=story)
story.append(p('Usos de Redis en el backend:'))
story.extend(bullet_list([
    'Rate limit.',
    'Locks distribuidos.',
    'Cola.',
    'Cache de consultas cortas.',
    'Estado temporal de confirmaciones.',
    'Pub/sub para actualización de UI.',
]))
story.append(callout(
    'No usar Redis como única fuente de verdad para memorias o recordatorios. Redis es '
    'cache y cola, no persistencia crítica.',
    color=SEM_WARNING
))

add_heading('21.2. Índices de base de datos', style_h2, level=1, story=story)
story.append(p('Índices recomendados:'))
story.append(code_block(
    'memory_nodes(workspace_id, type)\n'
    'memory_nodes(workspace_id, created_at)\n'
    'memory_nodes(workspace_id, sensitivity)\n'
    'reminders(workspace_id, status, next_due_at)\n'
    'occurrences(status, due_at)\n'
    'jobs(status, priority, created_at)\n'
    'execution_logs(workspace_id, created_at)'
))

add_heading('21.3. Índice vectorial', style_h2, level=1, story=story)
story.append(p(
    'El vector debe asociarse al workspace y al nodo. Si el nodo se elimina, su vector debe '
    'invalidarse y purgarse para evitar búsquedas fantasma.'
))

# ===== 22. Notificaciones =====
add_heading('22. Notificaciones', style_h1, level=0, story=story)

add_heading('22.1. Modelo', style_h2, level=1, story=story)
story.append(code_block(
    'Notification\n'
    '- id\n'
    '- workspace_id\n'
    '- occurrence_id nullable\n'
    '- channel\n'
    '- payload_ref\n'
    '- status\n'
    '- attempts\n'
    '- delivered_at\n'
    '- last_error'
))

add_heading('22.2. Estados', style_h2, level=1, story=story)
story.append(code_block(
    'pending\n'
    'sending\n'
    'delivered\n'
    'failed\n'
    'cancelled'
))

add_heading('22.3. Reglas', style_h2, level=1, story=story)
story.extend(bullet_list([
    'No incluir secretos en previews de notificación.',
    'Permitir modo silencioso.',
    'Respetar preferencias de canal.',
    'No enviar una notificación duplicada por reintento.',
    'Mostrar error de configuración sin fingir entrega.',
]))

# ===== 23. Exportación, importación y backups =====
add_heading('23. Exportación, importación y backups', style_h1, level=0, story=story)

add_heading('23.1. Exportación', style_h2, level=1, story=story)
story.append(endpoint('POST /exports'))
story.append(p('Debe ser asíncrona para volúmenes grandes. Contenido:'))
story.append(code_block(
    'manifest.json\n'
    'user-settings.json\n'
    'memories.jsonl.enc\n'
    'edges.jsonl.enc\n'
    'reminders.jsonl.enc\n'
    'agents.jsonl.enc\n'
    'files/\n'
    'checksums.sha256'
))

add_heading('23.2. Importación', style_h2, level=1, story=story)
story.append(p('Debe:'))
story.extend(bullet_list([
    'Validar schema.',
    'Verificar checksum.',
    'Mostrar resumen antes de importar.',
    'Permitir importar a workspace nuevo.',
    'Detectar duplicados.',
    'Mantener procedencia de importación.',
]))

add_heading('23.3. Backup', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Backup lógico cifrado.',
    'Backup de base de datos según despliegue.',
    'Backup de objetos.',
    'Prueba periódica de restauración.',
    'No guardar la clave de descifrado junto al backup.',
]))

# ===== 24. Healthchecks =====
add_heading('24. Healthchecks', style_h1, level=0, story=story)

story.append(endpoint('GET /health/live'))
story.append(p('Responde si el proceso está vivo:'))
story.append(code_block(
    '{\n'
    '  "status": "ok",\n'
    '  "service": "vnbot-api",\n'
    '  "version": "0.1.0"\n'
    '}'
))

story.append(endpoint('GET /health/ready'))
story.append(p('Comprueba dependencias críticas:'))
story.extend(bullet_list([
    'Base de datos.',
    'Migraciones.',
    'Cola cuando el modo lo requiere.',
    'Storage si se necesitan archivos.',
]))

story.append(endpoint('GET /health/dependencies'))
story.append(p('Devuelve estado detallado:'))
story.append(code_block(
    '{\n'
    '  "database": {"status": "ok", "latency_ms": 4},\n'
    '  "redis": {"status": "ok", "latency_ms": 2},\n'
    '  "storage": {"status": "ok"},\n'
    '  "ollama": {"status": "optional_unavailable"},\n'
    '  "mcp_gateway": {"status": "ok"}\n'
    '}'
))
story.append(callout(
    'Los proveedores opcionales no deben hacer que una instalación básica aparezca como '
    'completamente caída. El healthcheck debe distinguir críticos de opcionales.',
    color=ACCENT
))

# ===== 25. Errores y códigos =====
add_heading('25. Errores y códigos', style_h1, level=0, story=story)

add_heading('25.1. Categorías', style_h2, level=1, story=story)
story.append(code_block(
    'AUTH_*          autenticación\n'
    'PERMISSION_*    autorización\n'
    'VALIDATION_*    payload inválido\n'
    'MEMORY_*        memoria/grafo\n'
    'REMINDER_*      recordatorios\n'
    'JOB_*           trabajos\n'
    'LLM_*           proveedores IA\n'
    'MCP_*           herramientas MCP\n'
    'FILE_*          archivos\n'
    'INTEGRATION_*   integraciones\n'
    'SYSTEM_*        infraestructura'
))

add_heading('25.2. Ejemplos', style_h2, level=1, story=story)
story.append(code_block(
    'AUTH_SESSION_EXPIRED\n'
    'PERMISSION_TOOL_DENIED\n'
    'VALIDATION_INVALID_DATETIME\n'
    'REMINDER_AMBIGUOUS_TIME\n'
    'REMINDER_ALREADY_COMPLETED\n'
    'JOB_MAX_RETRIES\n'
    'LLM_PROVIDER_RATE_LIMIT\n'
    'MCP_TOOL_TIMEOUT\n'
    'MCP_SCOPE_REQUIRED\n'
    'FILE_TOO_LARGE\n'
    'INTEGRATION_REAUTH_REQUIRED\n'
    'SYSTEM_DATABASE_UNAVAILABLE'
))

add_heading('25.3. Retryable', style_h2, level=1, story=story)
story.append(p(
    'Cada error debe indicar si es reintentable. No reintentar automáticamente errores de '
    'autorización, validación o confirmación faltante. Los errores retryable son típicamente '
    'fallos de red, rate limits y caídas temporales de proveedores.'
))

# ===== 26. Seguridad del backend =====
add_heading('26. Seguridad del backend', style_h1, level=0, story=story)

add_heading('26.1. Secretos', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Variables de entorno solo en desarrollo controlado.',
    'Docker secrets o vault en servidor.',
    'Keychain del sistema para desktop.',
    'No tokens en URL.',
    'No secretos en logs.',
    'Rotación documentada.',
]))

add_heading('26.2. Archivos', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Validar tamaño.',
    'Validar MIME real.',
    'Renombrar con identificadores internos.',
    'Guardar fuera del web root.',
    'Analizar malware cuando el despliegue lo requiera.',
    'Impedir path traversal.',
]))

add_heading('26.3. URLs externas', style_h2, level=1, story=story)
story.append(p('El fetch web y MCP deben protegerse contra SSRF:'))
story.extend(bullet_list([
    'Bloquear redes privadas por defecto.',
    'Permitir allowlist configurada.',
    'Resolver y verificar IP final.',
    'Limitar redirects.',
    'Timeout.',
    'Tamaño máximo de respuesta.',
]))

add_heading('26.4. Prompt injection', style_h2, level=1, story=story)
story.append(callout(
    'El contenido de emails, páginas, documentos y MCP debe tratarse como datos no '
    'confiables. Las instrucciones encontradas dentro de esos datos no deben modificar la '
    'política del agente.',
    color=SEM_ERROR
))

# ===== 27. Concurrencia y consistencia =====
add_heading('27. Concurrencia y consistencia', style_h1, level=0, story=story)

add_heading('27.1. Recordatorios', style_h2, level=1, story=story)
story.append(p(
    'Usar lock por ocurrencia. La entrega debe ser exactamente una vez en condiciones '
    'normales y como máximo una vez en escenarios de recuperación no verificable, con '
    'deduplicación por provider cuando sea posible.'
))

add_heading('27.2. Memoria', style_h2, level=1, story=story)
story.append(p('Usar versionado optimista:'))
story.append(endpoint('PATCH con expected_version'))
story.append(p(
    'Si otro proceso modificó el nodo, devolver conflicto y no sobrescribir silenciosamente. '
    'El cliente debe refrescar y volver a intentar.'
))

add_heading('27.3. Integraciones', style_h2, level=1, story=story)
story.append(p(
    'Cada integración debe guardar cursor o timestamp de sincronización y manejar eventos '
    'repetidos con idempotency keys.'
))

# ===== 28. Escalabilidad =====
add_heading('28. Escalabilidad', style_h1, level=0, story=story)

add_heading('28.1. Escalado vertical inicial', style_h2, level=1, story=story)
story.append(p(
    'Para una instalación personal, aumentar CPU/RAM y mantener una sola instancia puede '
    'ser suficiente. La arquitectura permite empezar simple y crecer sin reescribir.'
))

add_heading('28.2. Escalado horizontal', style_h2, level=1, story=story)
story.append(p('La API debe ser stateless salvo por:'))
story.extend(bullet_list([
    'Sesión server-side si se usa.',
    'Cache Redis.',
    'Base de datos.',
    'Storage externo.',
]))
story.append(p('Los workers pueden aumentar según la cola.'))

add_heading('28.3. Cuellos de botella esperados', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Transcripción local.',
    'Embeddings.',
    'Proveedores LLM.',
    'Reindexación.',
    'Render del grafo en cliente.',
    'Entrega de notificaciones.',
    'Storage de audios.',
]))

add_heading('28.4. Límites configurables', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Memorias por workspace.',
    'Tamaño de archivo.',
    'Audio diario.',
    'Jobs concurrentes.',
    'Tokens por usuario.',
    'Profundidad de grafo.',
    'Número de MCP.',
    'Herramientas por agente.',
]))

# ===== 29. Configuración =====
add_heading('29. Configuración', style_h1, level=0, story=story)

add_heading('29.1. Variables principales', style_h2, level=1, story=story)
story.append(code_block(
    'VNBOT_ENV=production\n'
    'VNBOT_BASE_URL=https://vnbot.example.com\n'
    'DATABASE_URL=postgresql+asyncpg://...\n'
    'REDIS_URL=redis://...\n'
    'STORAGE_ENDPOINT=http://minio:9000\n'
    'STORAGE_BUCKET=vnbot\n'
    'SESSION_SECRET=...\n'
    'ENCRYPTION_KEY=...\n'
    'DEFAULT_TIMEZONE=UTC\n'
    'LOG_LEVEL=INFO'
))

add_heading('29.2. Reglas', style_h2, level=1, story=story)
story.extend(bullet_list([
    '.env.example no contiene secretos reales.',
    'Configuración crítica debe validarse al iniciar.',
    'Proveedores opcionales pueden quedar desactivados.',
    'Un error de configuración debe indicar cómo corregirse.',
]))

# ===== 30. Pruebas del backend =====
add_heading('30. Pruebas del backend', style_h1, level=0, story=story)

add_heading('30.1. Unitarias', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Entidades.',
    'Recurrencia.',
    'Timezones.',
    'Policy engine.',
    'Idempotency keys.',
    'Parsers.',
    'Validación de tools.',
    'Cifrado.',
]))

add_heading('30.2. Integración', style_h2, level=1, story=story)
story.extend(bullet_list([
    'SQLite.',
    'PostgreSQL.',
    'Redis.',
    'Worker.',
    'Scheduler.',
    'Mock LLM.',
    'Mock MCP.',
    'Storage.',
]))

add_heading('30.3. Contratos', style_h2, level=1, story=story)
story.extend(bullet_list([
    'OpenAPI.',
    'JSON Schema de skills.',
    'Tool schemas MCP.',
    'Export/import.',
    'Eventos internos.',
]))

add_heading('30.4. E2E', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Crear recordatorio y reiniciar worker.',
    'Reintentar delivery.',
    'Confirmar acción.',
    'Cancelar antes de ejecución.',
    'Borrar memoria y verificar índices.',
    'Desconectar MCP.',
    'Importar backup.',
]))

# ===== 31. Observabilidad y privacidad =====
add_heading('31. Observabilidad y privacidad', style_h1, level=0, story=story)
story.append(p(
    'La observabilidad debe ayudar a operar el sistema sin convertir el contenido del '
    'usuario en telemetría. Esta dualidad es esencial: trazabilidad operativa sin invasión '
    'de privacidad.'
))

add_heading('31.1. Se puede registrar', style_h2, level=1, story=story)
story.extend(bullet_list([
    'IDs internos.',
    'Tiempos.',
    'Estados.',
    'Códigos de error.',
    'Proveedor/modelo.',
    'Tokens agregados.',
    'Tamaños.',
    'Conteos.',
    'Hashes no reversibles cuando sean necesarios.',
]))

add_heading('31.2. No registrar por defecto', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Plaintext de memorias.',
    'Audio.',
    'API keys.',
    'Tokens OAuth.',
    'Passwords.',
    'Contenido completo de emails.',
    'Respuestas completas de proveedores.',
]))

# ===== 32. Requisitos para Docker =====
add_heading('32. Requisitos para Docker', style_h1, level=0, story=story)

docker_data = [
    ['Servicio', 'Requisitos'],
    ['API', 'Imagen no root, Healthcheck HTTP, Migración explícita, Puerto interno, Sin persistencia local crítica.'],
    ['Worker', 'Healthcheck de proceso, Conexión a Redis, Conexión a base de datos, Graceful shutdown, Visibilidad de jobs activos.'],
    ['Scheduler', 'Lock distribuido, Una sola autoridad para crear ocurrencias, Graceful shutdown.'],
]
story.append(make_table(docker_data, col_widths=[30*mm, 140*mm]))
story.append(Spacer(1, 8))

add_heading('32.1. Volúmenes', style_h2, level=1, story=story)
story.append(code_block(
    'postgres_data\n'
    'redis_data opcional\n'
    'minio_data\n'
    'vnbot_backups'
))

# ===== 33. Criterios de aceptación backend MVP =====
add_heading('33. Criterios de aceptación backend MVP', style_h1, level=0, story=story)
story.append(p('El backend cumple el MVP cuando satisface los 15 criterios:'))
story.extend(numbered_list([
    'Puede crear y consultar una memoria.',
    'Puede crear un nodo y una relación.',
    'Puede crear un recordatorio con zona horaria.',
    'Puede generar ocurrencias recurrentes.',
    'Puede entregar una notificación sin duplicarla.',
    'Puede reintentar un job fallido.',
    'Puede detener un job cancelable.',
    'Puede procesar una instrucción sin LLM mediante heurística.',
    'Puede registrar una operación y su auditoría.',
    'Puede exportar/importar datos.',
    'Puede ejecutarse con SQLite en local.',
    'Puede ejecutarse con PostgreSQL y Redis en servidor.',
    'Expone live/ready/dependencies.',
    'No mezcla credenciales con datos de usuario.',
    'No autoriza herramientas solo porque el LLM las solicite.',
]))

# ===== 34. Orden de implementación backend =====
add_heading('34. Orden de implementación backend', style_h1, level=0, story=story)
story.append(p('El backend se implementa en 7 fases secuenciales con criterios de salida:'))

fases_data = [
    ['Fase', 'Módulos', 'Criterio de salida'],
    ['Fase 1 — Dominio', 'Entidades, estados, reglas de recordatorio, memoria y grafo, tests unitarios', 'Tests unitarios pasan, cobertura 80%+'],
    ['Fase 2 — Persistencia', 'SQLAlchemy, SQLite, migraciones, repositorios, exportación básica', 'CRUD de memoria y recordatorio funciona'],
    ['Fase 3 — API', 'Auth, Memory, Graph, Reminders, Operations, Health', 'OpenAPI documenta todos los endpoints'],
    ['Fase 4 — Jobs', 'Tabla/cola, Worker, Scheduler, Locks, Reintentos, Delivery', 'Recordatorio se entrega sin duplicados'],
    ['Fase 5 — IA', 'Heurística, LLM Router, Structured output, Embeddings', 'Funciona con y sin LLM'],
    ['Fase 6 — Integraciones', 'Notificaciones, MCP interno, MCP externo, Graphify, Calendario', 'MCP con scopes y policy engine'],
    ['Fase 7 — Producción', 'PostgreSQL, Redis, MinIO, Docker, Observabilidad, Backups, CI/CD', 'Despliegue reproducible'],
]
story.append(make_table(fases_data, col_widths=[35*mm, 80*mm, 55*mm]))

# ===== 35. Decisiones abiertas =====
add_heading('35. Decisiones abiertas', style_h1, level=0, story=story)
story.append(p('Estas decisiones deberán cerrarse antes de cada fase correspondiente:'))
story.extend(numbered_list([
    'Dramatiq o Celery como worker principal.',
    'SQLite job queue propia o Redis obligatorio en modo local.',
    'pgvector como único índice vectorial o adaptador adicional.',
    'Transporte WebSocket o SSE para estados de jobs.',
    'Duración de retención de operaciones y logs.',
    'Política de soft delete por tipo de dato.',
    'Soporte de múltiples regiones/zonas horarias en workspaces compartidos.',
    'Formato definitivo de plugins externos.',
    'Servicio separado de notificaciones en VNBOT 1.0.',
    'WebAuthn en el MVP o en una versión posterior.',
]))

# ===== 36. Conclusión =====
add_heading('36. Conclusión', style_h1, level=0, story=story)
story.append(p(
    'El backend de VNBOT debe ser una plataforma modular, no un conjunto de endpoints que '
    'llaman directamente a un LLM. La memoria, los recordatorios y las operaciones deben '
    'tener reglas deterministas y estados persistentes. La IA, MCP y las integraciones deben '
    'utilizar esas reglas, no sustituirlas.'
))
story.append(p('La estructura recomendada es:'))
story.append(code_block(
    'API stateless\n'
    '+ dominio explícito\n'
    '+ storage adapters\n'
    '+ jobs durables\n'
    '+ scheduler idempotente\n'
    '+ LLM Router\n'
    '+ policy engine\n'
    '+ MCP Gateway\n'
    '+ auditoría\n'
    '+ healthchecks'
))
story.append(p(
    'Esta arquitectura permite comenzar con SQLite y una instalación personal, y evolucionar '
    'hacia PostgreSQL, Redis, workers replicados y múltiples agentes sin reescribir el núcleo. '
    'También permite que VNBOT se distribuya en web, APK, desktop, Docker y CLI manteniendo '
    'el mismo modelo de datos y las mismas reglas de seguridad.'
))

# ===== 37. Endpoints de sincronización =====
add_heading('37. Endpoints de sincronización (fase 0.3+)', style_h1, level=0, story=story)
story.append(p(
    'Estos endpoints se implementan cuando la sync strategy esté diseñada y probada.'
))

story.append(endpoint('GET /api/v1/sync/status'))
story.append(p('Devuelve el estado de sincronización del workspace.'))

story.append(endpoint('POST /api/v1/sync/push'))
story.append(p('Envía cambios locales al servidor. El cuerpo incluye ops con version vectors.'))

story.append(endpoint('POST /api/v1/sync/pull'))
story.append(p('Recibe cambios del servidor desde un cursor dado.'))

story.append(endpoint('GET /api/v1/sync/conflicts'))
story.append(p('Lista conflictos pendientes de resolución.'))

story.append(endpoint('POST /api/v1/sync/conflicts/{id}/resolve'))
story.append(p('Resuelve un conflicto específico con la opción elegida por el usuario.'))

story.append(endpoint('POST /api/v1/sync/full-reset'))
story.append(p('Resetea la sincronización (peligroso, requiere confirmación doble).'))

# ===== 38. Requisitos de testing del backend =====
add_heading('38. Requisitos de testing del backend', style_h1, level=0, story=story)

add_heading('38.1. Tests unitarios', style_h2, level=1, story=story)
story.append(p('Cada servicio de dominio debe tener tests unitarios:'))
story.extend(bullet_list([
    '<b>MemoryService:</b> crear, actualizar, borrar, buscar, relacionar, olvidar.',
    '<b>ReminderService:</b> crear puntual, crear recurrente, disparar, completar, posponer.',
    '<b>GraphService:</b> agregar nodo, agregar edge, recorrido, invalidación.',
    '<b>AgentService:</b> crear, asignar skills, verificar permisos.',
    '<b>PolicyEngine:</b> evaluar permiso, denegar por defecto, auditar.',
    '<b>LLMRouter:</b> seleccionar provider, fallback, structured output parsing.',
]))
story.append(p('Cobertura mínima: 80% en dominio, 70% en API.'))

add_heading('38.2. Tests de integración', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Crear recordatorio → verificar que se dispara en el momento correcto.',
    'Crear memoria → verificar que aparece en búsqueda.',
    'Conectar MCP tool → verificar que se ejecuta con permisos correctos.',
    'Exportar e importar → verificar integridad de datos.',
]))

add_heading('38.3. Contract testing para MCP', style_h2, level=1, story=story)
story.append(p('Cada tool MCP debe tener un contract test que verifique:'))
story.extend(bullet_list([
    'Input schema es válido.',
    'Output schema es válido.',
    'La tool respeta sus scopes declarados.',
    'Un fallo de la tool no afecta al núcleo.',
]))

add_heading('38.4. Benchmarks automatizados', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Operaciones CRUD sobre memorias (1,000 ops).',
    'Búsqueda textual con 5,000 memorias.',
    'Recordatorios: crear 1,000 y verificar que ninguno se duplica.',
    'Grafo: subgrafo profundidad 3 con 50 nodos.',
    'Scheduler: 100 jobs concurrentes sin duplicados.',
]))

# ===== 39. Instrumentación de observabilidad =====
add_heading('39. Instrumentación de observabilidad', style_h1, level=0, story=story)
story.append(p(
    'Todos los servicios del backend deben estar instrumentados con OpenTelemetry desde '
    'la primera versión.'
))

add_heading('39.1. Spans obligatorios', style_h2, level=1, story=story)
story.extend(bullet_list([
    '<b>vnbot.api.&lt;method&gt;.&lt;endpoint&gt;</b>: cada request HTTP.',
    '<b>vnbot.domain.&lt;service&gt;.&lt;operation&gt;</b>: cada operación de dominio.',
    '<b>vnbot.llm.&lt;provider&gt;.call</b>: cada llamada a LLM.',
    '<b>vnbot.mcp.&lt;tool&gt;.call</b>: cada invocación de tool MCP.',
    '<b>vnbot.worker.&lt;job_type&gt;.execute</b>: cada ejecución de job.',
    '<b>vnbot.sync.push / vnbot.sync.pull</b>: cada operación de sincronización.',
]))

add_heading('39.2. Métricas obligatorias', style_h2, level=1, story=story)
story.append(code_block(
    'vnbot_api_requests_total{method, endpoint, status}\n'
    'vnbot_api_duration_seconds{method, endpoint} (histogram)\n'
    'vnbot_llm_tokens_total{provider, model, direction}\n'
    'vnbot_llm_duration_seconds{provider, model}\n'
    'vnbot_jobs_total{type, status}\n'
    'vnbot_jobs_duration_seconds{type}\n'
    'vnbot_sync_conflicts_total{workspace_id}\n'
    'vnbot_graph_nodes_total{workspace_id}\n'
    'vnbot_graph_query_duration_seconds{operation}'
))

add_heading('39.3. Regla de contenido', style_h2, level=1, story=story)
story.append(callout(
    'Ningún span, métrica ni log debe contener el contenido de una memoria, mensaje o dato '
    'personal. Solo IDs, estados, duraciones y tipos. Esta regla se valida con scanners '
    'automáticos de PII en CI.',
    color=SEM_ERROR
))

# ===== 40. Restricciones de rendimiento del grafo =====
add_heading('40. Restricciones de rendimiento del grafo', style_h1, level=0, story=story)

add_heading('40.1. Límites por consulta', style_h2, level=1, story=story)
grafo_limites = [
    ['Parámetro', 'Valor'],
    ['Profundidad máxima por defecto', '3'],
    ['Top-K máximo configurable', '50 (por defecto 20)'],
    ['Nodos máximos devueltos por consulta', '100'],
    ['Timeout por consulta', '5 segundos'],
]
story.append(make_table(grafo_limites, col_widths=[90*mm, 80*mm]))

add_heading('40.2. No cargar el grafo completo', style_h2, level=1, story=story)
story.append(p(
    'El cliente nunca recibe el grafo completo. Todas las consultas son server-side con '
    'paginación y filtros. La visualización recibe solo los nodos y edges del resultado.'
))

add_heading('40.3. Degradación graciosa', style_h2, level=1, story=story)
story.append(p('Si una consulta excede los límites, el sistema sigue 4 pasos:'))
story.extend(numbered_list([
    'Reduce la profundidad.',
    'Aplica top-K más agresivo.',
    'Devuelve un mensaje al usuario: "La consulta es muy amplia. Refina los filtros o selecciona un nodo de inicio."',
    'Nunca agota la memoria del servidor por una consulta de grafo.',
]))

# ===== Build PDF =====
output_body = '/home/z/my-project/scripts/backend_body.pdf'
doc = TocDocTemplate(
    output_body,
    pagesize=A4,
    leftMargin=20*mm,
    rightMargin=20*mm,
    topMargin=22*mm,
    bottomMargin=22*mm,
    title='VNBOT — Esquema Backend',
    author='VNBOT Project',
    subject='Esquema Backend v1.0.0-draft — Servicios, API, jobs, scheduler, MCP, observabilidad',
    creator='Z.ai',
)
doc.multiBuild(story, onFirstPage=page_decoration, onLaterPages=page_decoration)
print(f'Body PDF generated: {output_body}')
print(f'Size: {os.path.getsize(output_body) / 1024:.1f} KB')
