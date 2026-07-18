#!/usr/bin/env python3
"""
VNBOT Volumen I — Datos, Seguridad y Extensibilidad
Compila 3 documentos: Modelo de Datos (07) + Seguridad y Privacidad (08) + MCP y Skills (09)
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

# ===== Palette =====
PAGE_BG       = colors.HexColor('#FFFFFF')
SECTION_BG    = colors.HexColor('#eff1f1')
CARD_BG       = colors.HexColor('#f4f6f7')
TABLE_STRIPE  = colors.HexColor('#edeff0')
HEADER_FILL   = colors.HexColor('#1F2937')
BORDER        = colors.HexColor('#b3bfc6')
ACCENT        = colors.HexColor('#0E7490')   # cyan — Modelo de Datos
ACCENT_AMBER  = colors.HexColor('#B45309')   # amber — Seguridad
ACCENT_MAG    = colors.HexColor('#7152cb')   # magenta/purple — MCP/Skills
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

# Document divider styles — for separating the 3 compiled documents
style_doc_divider = ParagraphStyle('DocDivider',
    fontName='NotoSansSC-Bold', fontSize=28, leading=34,
    textColor=colors.white, alignment=TA_LEFT,
    backColor=HEADER_FILL, borderPadding=18,
    spaceBefore=20, spaceAfter=14, leftIndent=0, rightIndent=0)

style_doc_subtitle = ParagraphStyle('DocSubtitle',
    fontName='Mono', fontSize=10, leading=14,
    textColor=colors.white, alignment=TA_LEFT,
    backColor=HEADER_FILL, borderPadding=10,
    spaceBefore=0, spaceAfter=20, leftIndent=0, rightIndent=0)

toc_level0 = ParagraphStyle('TocL0',
    fontName='NotoSansSC-Bold', fontSize=11, leading=18,
    textColor=TEXT_PRIMARY, leftIndent=0, spaceBefore=6, spaceAfter=2)

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

def doc_divider(doc_num, title, subtitle, accent_color):
    """Visual divider between compiled documents."""
    # Build a 2-cell table: top = number+title (dark bg), bottom = subtitle (dark bg)
    num_title = Paragraph(
        f'<font color="{accent_color.hexval()}">DOC {doc_num}</font>  ·  {title}',
        style_doc_divider
    )
    sub = Paragraph(subtitle, style_doc_subtitle)
    t = Table([[num_title], [sub]], colWidths=[170*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HEADER_FILL),
        ('LEFTPADDING', (0,0), (-1,-1), 16),
        ('RIGHTPADDING', (0,0), (-1,-1), 16),
        ('TOPPADDING', (0,0), (0,0), 14),
        ('BOTTOMPADDING', (0,0), (0,0), 4),
        ('TOPPADDING', (0,1), (0,1), 0),
        ('BOTTOMPADDING', (0,1), (0,1), 14),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    return t

# ===== Page decoration =====
def page_decoration(canv, doc):
    canv.saveState()
    canv.setFont('Mono', 8)
    canv.setFillColor(TEXT_MUTED)
    page_num = canv.getPageNumber()
    canv.drawString(20*mm, 12*mm, 'VNBOT // VOL I // v1.0.0-draft')
    canv.drawRightString(190*mm, 12*mm, f'{page_num}')
    canv.setStrokeColor(BORDER)
    canv.setLineWidth(0.4)
    canv.line(20*mm, 15*mm, 190*mm, 15*mm)
    if page_num > 1:
        canv.setFont('Mono', 7.5)
        canv.setFillColor(TEXT_MUTED)
        canv.drawString(20*mm, 285*mm, 'VNBOT — Vol I: Datos · Seguridad · Extensibilidad')
        canv.drawRightString(190*mm, 285*mm, '07+08+09')
        canv.line(20*mm, 283*mm, 190*mm, 283*mm)
    canv.restoreState()

# ===== Build story =====
story = []

# --- TOC ---
story.append(Paragraph('Tabla de Contenidos', style_toc_title))
story.append(HRFlowable(width='100%', thickness=1, color=ACCENT, spaceAfter=14))
story.append(Paragraph(
    'Este volumen compila 3 documentos técnicos de VNBOT: Modelo de Datos, Seguridad y Privacidad, '
    'y MCP y Skills. Cada documento preserva su numeración original para facilitar la referencia '
    'cruzada con el resto del proyecto.',
    style_body))
story.append(Spacer(1, 14))
toc = TableOfContents()
toc.levelStyles = [toc_level0, toc_level1]
story.append(toc)
story.append(PageBreak())

# ============================================================
# DOCUMENTO 07 — MODELO DE DATOS
# ============================================================
story.append(doc_divider('07', 'MODELO DE DATOS',
    'Entidades, relaciones, identificadores, estados, reglas de integridad y formatos de persistencia.',
    ACCENT))
story.append(Spacer(1, 10))

# 1. Propósito
add_heading('1. Propósito', style_h1, level=0, story=story)
story.append(p(
    'Este documento define las entidades, relaciones, identificadores, estados, reglas de '
    'integridad y formatos de persistencia de VNBOT. El modelo debe soportar instalación local '
    'con SQLite, PWA con IndexedDB, servidor con PostgreSQL, memoria de nodos y relaciones, '
    'recordatorios puntuales y recurrentes, agentes y skills, integraciones MCP, jobs '
    'asíncronos, archivos y audio, auditoría, exportación/importación y sincronización futura '
    'entre dispositivos.'
))
story.append(p(
    'El modelo no debe asumir que todo el contenido estará en texto plano. Algunos campos se '
    'almacenarán cifrados, algunos serán metadatos operativos y otros serán índices derivados.'
))

# 2. Principios del modelo
add_heading('2. Principios del modelo', style_h1, level=0, story=story)
principios_data = [
    ['Principio', 'Descripción'],
    ['Aislamiento por workspace', 'Toda entidad relacionada con datos del usuario debe tener un workspace_id directo o heredado de una relación autorizada.'],
    ['Procedencia obligatoria', 'Toda memoria o relación generada por IA debe indicar cómo fue creada: explicit_user_input, user_confirmed, conversation_extraction, audio_transcription, image_ocr, llm_inference, external_integration, imported_data, system_generated.'],
    ['Confianza ≠ autoridad', 'confidence (qué tan seguro está el sistema) y authority (si el usuario confirmó) son diferentes. Una inferencia con confianza 0.98 no equivale a una preferencia confirmada.'],
    ['Borrado gradual', 'Los datos pasan por: active → deleted/soft_deleted → purged. La purga definitiva debe incluir índices, vectores, archivos, cache y referencias derivadas.'],
    ['Fechas UTC + zona explícita', 'Los timestamps técnicos se guardan en UTC. Las operaciones de usuario también deben conservar la zona horaria de interpretación.'],
    ['Identificadores opacos', 'No usar emails, nombres o índices secuenciales como IDs públicos. Usar UUID/ULID o identificadores equivalentes.'],
]
story.append(make_table(principios_data, col_widths=[40*mm, 130*mm]))

# 3. Capas de almacenamiento
add_heading('3. Capas de almacenamiento', style_h1, level=0, story=story)
capas_data = [
    ['Capa', 'Tipo', 'Contenido'],
    ['Datos de dominio', 'Fuente de verdad', 'Usuarios, workspaces, memorias, relaciones, recordatorios, agentes, integraciones, jobs.'],
    ['Datos derivados', 'Reconstruibles', 'Embeddings, índices de búsqueda, resúmenes, estadísticas, layout del grafo, cache.'],
    ['Archivos', 'Storage externo', 'Audio, imágenes, documentos, backups, assets generados. La base de datos conserva referencia segura y metadata.'],
]
story.append(make_table(capas_data, col_widths=[35*mm, 30*mm, 105*mm]))
story.append(Spacer(1, 8))
story.append(p('Adaptadores de persistencia:'))
story.append(code_block(
    'IndexedDBAdapter → PWA\n'
    'SQLiteAdapter    → local/desktop\n'
    'PostgresAdapter  → server\n'
    'FileAdapter      → export/import\n'
    'ObjectStorage    → S3/MinIO/filesystem'
))

# 4. Convenciones
add_heading('4. Convenciones', style_h1, level=0, story=story)
add_heading('4.1. IDs', style_h2, level=1, story=story)
story.append(code_block(
    'usr_01J...\n'
    'ws_01J...\n'
    'mem_01J...\n'
    'edge_01J...\n'
    'rem_01J...\n'
    'occ_01J...\n'
    'job_01J...'
))
story.append(p('La parte legible ayuda a debugging, pero no debe revelar información personal.'))

add_heading('4.2. Timestamps estándar', style_h2, level=1, story=story)
story.append(code_block('created_at · updated_at · deleted_at · expires_at'))
story.append(p('Todos en UTC ISO 8601 o tipo timestamp con zona en la base de datos.'))

# 5-9. Entidades principales
add_heading('5. Entidades principales de identidad', style_h1, level=0, story=story)
story.append(p('Las entidades de identidad siguen un modelo jerárquico: User → Session/Device → Workspace → WorkspaceMember.'))

add_heading('5.1. User', style_h2, level=1, story=story)
story.append(code_block(
    'User\n'
    '- id: string PK\n'
    '- email: string nullable, unique cuando exista\n'
    '- display_name: string nullable\n'
    '- password_hash: string nullable\n'
    '- status: active|locked|pending|deleted\n'
    '- timezone: IANA timezone\n'
    '- locale: string\n'
    '- created_at, updated_at, last_login_at'
))
story.append(p('Reglas: no almacenar contraseña en texto, email puede ser nullable en modo local, no usar email como ID, la eliminación de usuario debe revocar sesiones e integraciones, las memorias pertenecen a workspaces no directamente a emails.'))

add_heading('5.2. Workspace', style_h2, level=1, story=story)
story.append(p('Un workspace es el límite de datos, memoria y permisos. Tipos: personal, family, team, project.'))
story.append(code_block(
    'Workspace\n'
    '- id, owner_user_id, name\n'
    '- type: personal|family|team|project\n'
    '- status: active|archived|deleted\n'
    '- default_timezone, settings_json\n'
    '- created_at, updated_at'
))
story.append(callout(
    'Un recurso no puede cruzar workspaces sin una operación explícita. Un agente debe pertenecer '
    'a un workspace. Las integraciones deben estar vinculadas a un workspace concreto.',
    color=SEM_WARNING
))

add_heading('5.3. Roles y autorización', style_h2, level=1, story=story)
story.extend(bullet_list([
    '<b>owner</b> — propietario del workspace, control total.',
    '<b>admin</b> — administración sin poder eliminar el workspace.',
    '<b>member</b> — uso completo de memoria y recordatorios.',
    '<b>viewer</b> — solo lectura.',
]))

# 6. Conversation y Message
add_heading('6. Conversation y Message', style_h1, level=0, story=story)
story.append(code_block(
    'Conversation\n'
    '- id, workspace_id, user_id, agent_id nullable\n'
    '- title nullable, status: active|archived|deleted\n'
    '- created_at, updated_at, last_message_at\n'
    '\n'
    'Message\n'
    '- id, conversation_id, workspace_id\n'
    '- role: user|assistant|system|tool\n'
    '- content_ciphertext nullable\n'
    '- content_preview nullable\n'
    '- content_format: text|markdown|json|audio_transcript\n'
    '- model_provider, model_name nullable\n'
    '- operation_id, source_file_id nullable\n'
    '- created_at, deleted_at nullable'
))
story.append(p('Reglas: el contenido puede estar cifrado, content_preview debe ser opcional y no contener secretos, los mensajes de herramientas deben referenciar la ejecución no copiar credenciales, la retención de conversación debe ser configurable.'))

# 7. MemoryNode
add_heading('7. MemoryNode — entidad principal de memoria', style_h1, level=0, story=story)
story.append(p('Es la entidad principal de memoria personal. Contenido cifrado, procedencia obligatoria, confianza separada de autoridad.'))
story.append(code_block(
    'MemoryNode\n'
    '- id, workspace_id, type, label\n'
    '- content_ciphertext, content_format\n'
    '- structured_data_ciphertext nullable\n'
    '- source_type, source_id nullable\n'
    '- provenance, authority, confidence decimal, sensitivity\n'
    '- status: active|superseded|deleted|expired|archived\n'
    '- valid_from, valid_until, expires_at nullable\n'
    '- version integer\n'
    '- created_by_user_id, created_by_agent_id nullable\n'
    '- created_at, updated_at, deleted_at nullable'
))

add_heading('7.1. Tipos de nodos', style_h2, level=1, story=story)
story.append(code_block(
    'person · place · project · task · reminder · event\n'
    'preference · note · document · conversation · agent\n'
    'contact · secret_reference'
))

add_heading('7.2. Authority y sensitivity', style_h2, level=1, story=story)
auth_data = [
    ['Campo', 'Valores'],
    ['authority', 'explicit · user_confirmed · system_extracted · inferred · external_source'],
    ['sensitivity', 'public · personal · sensitive · secret'],
]
story.append(make_table(auth_data, col_widths=[30*mm, 140*mm]))

# 8. MemoryEdge
add_heading('8. MemoryEdge — relaciones entre nodos', style_h1, level=0, story=story)
story.append(code_block(
    'MemoryEdge\n'
    '- id, workspace_id\n'
    '- source_node_id, target_node_id\n'
    '- relation_type, properties_ciphertext nullable\n'
    '- provenance, authority, confidence decimal\n'
    '- status: active|invalidated|superseded|deleted\n'
    '- valid_from, valid_until, version\n'
    '- created_by_user_id, created_by_agent_id nullable\n'
    '- created_at, updated_at, deleted_at nullable'
))
story.append(p('Relaciones iniciales (13 tipos):'))
story.append(code_block(
    'KNOWS · WORKS_ON · RELATED_TO · DEPENDS_ON\n'
    'REMINDER_FOR · HAPPENS_AT · PREFERS · SUPERSEDES\n'
    'CONTRADICTS · DERIVED_FROM · ASSIGNED_TO\n'
    'MENTIONED_IN · LOCATED_AT'
))

# 9. EmbeddingIndex
add_heading('9. EmbeddingIndex — datos derivados', style_h1, level=0, story=story)
story.append(p('Los embeddings son datos derivados y deben poder regenerarse desde la fuente de verdad.'))
story.append(code_block(
    'EmbeddingIndex\n'
    '- id, workspace_id\n'
    '- entity_type: memory_node|message|document\n'
    '- entity_id, model_name, dimensions\n'
    '- vector_reference nullable, content_hmac\n'
    '- status: pending|ready|stale|deleted|failed\n'
    '- created_at, updated_at'
))
story.append(callout(
    'No crear embeddings remotos sin consentimiento. El vector debe estar limitado al workspace. '
    'Si se borra el contenido, se borra o invalida el embedding.',
    color=SEM_WARNING
))

# 10. Reminder y ReminderOccurrence
add_heading('10. Reminder y ReminderOccurrence', style_h1, level=0, story=story)
story.append(p('La separación entre Reminder (regla) y ReminderOccurrence (instancia) permite generar ocurrencias con anticipación controlada sin duplicar filas infinitamente.'))
story.append(code_block(
    'Reminder\n'
    '- id, workspace_id, created_by_user_id, created_by_agent_id nullable\n'
    '- title, description_ciphertext nullable\n'
    '- timezone, recurrence_rule nullable\n'
    '- priority: low|normal|high|critical\n'
    '- channel, recipient_ref nullable\n'
    '- status: active|paused|completed|cancelled|expired\n'
    '- source_memory_id, next_due_at nullable\n'
    '- created_at, updated_at, completed_at, cancelled_at nullable\n'
    '\n'
    'ReminderOccurrence\n'
    '- id, reminder_id, workspace_id\n'
    '- occurrence_key unique (determinista: {reminder_id}:{due_at_utc}:{rule_version})\n'
    '- due_at, timezone\n'
    '- status: pending|queued|sending|delivered|snoozed|completed|failed|cancelled\n'
    '- attempts, delivered_at, completed_at, snoozed_until nullable\n'
    '- last_error_code nullable, created_at, updated_at'
))

# 11. Agent, Skill, ToolPermission
add_heading('11. Agent, Skill y ToolPermission', style_h1, level=0, story=story)
add_heading('11.1. Agent', style_h2, level=1, story=story)
story.append(code_block(
    'Agent\n'
    '- id, workspace_id, name, description\n'
    '- avatar_id, system_prompt_ciphertext\n'
    '- model_provider, model_name, model_config_json\n'
    '- autonomy_level: 0-4, budget_json\n'
    '- status: draft|active|paused|archived\n'
    '- created_by_user_id, created_at, updated_at'
))
add_heading('11.2. Skill con manifest YAML', style_h2, level=1, story=story)
story.append(code_block(
    'id: reminder.create\n'
    'version: 1.0.0\n'
    'risk_level: low\n'
    'required_tools:\n'
    '  - reminder_create\n'
    'memory_scopes:\n'
    '  - personal\n'
    'confirmation: required_if_ambiguous\n'
    'input_schema: schemas/reminder-input.json\n'
    'output_schema: schemas/reminder-output.json'
))
add_heading('11.3. ToolPermission — deny by default', style_h2, level=1, story=story)
story.append(code_block(
    'ToolPermission\n'
    '- id, workspace_id, agent_id, integration_id nullable\n'
    '- tool_name\n'
    '- permission_level: deny|read|write|execute\n'
    '- scope_json, requires_confirmation\n'
    '- max_calls_per_operation nullable\n'
    '- created_by_user_id, created_at, revoked_at nullable'
))
story.append(callout(
    'Deny por defecto. Una skill no puede ampliar permisos por sí sola. Un agente no puede usar '
    'una herramienta sin permiso vigente. La revocación debe ser inmediata para nuevas llamadas.',
    color=SEM_ERROR
))

# 12. Operation, ExecutionLog, Job
add_heading('12. Operation, ExecutionLog y Job', style_h1, level=0, story=story)
story.append(p('Estas entidades dan trazabilidad completa a cada acción del usuario o agente.'))
story.append(code_block(
    'Operation\n'
    '- id, workspace_id, user_id, agent_id nullable\n'
    '- conversation_id nullable, type, status\n'
    '- risk_level, input_ref, proposal_json nullable\n'
    '- requires_confirmation, confirmed_at nullable\n'
    '- created_at, expires_at, completed_at nullable\n'
    '\n'
    'ExecutionLog\n'
    '- id, workspace_id, operation_id\n'
    '- agent_id, integration_id, tool_name nullable\n'
    '- status, duration_ms nullable, error_code nullable\n'
    '- input_hash nullable, result_summary_ciphertext nullable\n'
    '- created_at\n'
    '\n'
    'Job\n'
    '- id, workspace_id, type, payload_ref\n'
    '- status: pending|running|retrying|succeeded|failed|cancelled|dead_letter\n'
    '- priority, idempotency_key\n'
    '- attempt, max_attempts\n'
    '- available_at, started_at, finished_at nullable\n'
    '- last_error_code nullable, trace_id, created_at'
))

# 13. Relaciones principales
add_heading('13. Relaciones principales entre entidades', style_h1, level=0, story=story)
story.append(code_block(
    'User 1 ─── N WorkspaceMember\n'
    'Workspace 1 ─── N MemoryNode\n'
    'Workspace 1 ─── N MemoryEdge\n'
    'MemoryNode N ─── N MemoryNode vía MemoryEdge\n'
    'Workspace 1 ─── N Reminder\n'
    'Reminder 1 ─── N ReminderOccurrence\n'
    'ReminderOccurrence 1 ─── N Notification\n'
    'Notification 1 ─── N DeliveryAttempt\n'
    'Workspace 1 ─── N Agent\n'
    'Agent N ─── N Skill vía AgentSkill\n'
    'Agent 1 ─── N ToolPermission\n'
    'Workspace 1 ─── N Integration\n'
    'Integration 1 ─── N CredentialRef\n'
    'Integration 1 ─── N MCPServer\n'
    'MCPServer 1 ─── N MCPTool\n'
    'Workspace 1 ─── N Operation\n'
    'Operation 1 ─── N ExecutionLog\n'
    'Workspace 1 ─── N Job\n'
    'Workspace 1 ─── N FileAsset\n'
    'FileAsset 1 ─── 0..1 AudioAsset\n'
    'FileAsset 1 ─── 0..1 Document'
))

# 14. Estados y transiciones
add_heading('14. Estados y transiciones', style_h1, level=0, story=story)
estados_data = [
    ['Entidad', 'Transiciones permitidas'],
    ['MemoryNode', 'active → superseded · active → expired · active → deleted · superseded → deleted · expired → deleted'],
    ['Reminder', 'active → paused · active → completed · active → cancelled · paused → active · paused → cancelled'],
    ['ReminderOccurrence', 'pending → queued · queued → sending · sending → delivered · sending → failed · failed → retrying · retrying → sending · pending → cancelled · pending → snoozed · snoozed → pending'],
    ['Integration', 'disconnected → connecting · connecting → healthy · connecting → degraded · healthy → reauth_required · healthy → revoked · degraded → healthy'],
]
story.append(make_table(estados_data, col_widths=[35*mm, 135*mm]))

# 15. Índices y cifrado
add_heading('15. Índices recomendados y campos cifrados', style_h1, level=0, story=story)
add_heading('15.1. Índices de base de datos', style_h2, level=1, story=story)
story.append(code_block(
    'users(email)\n'
    'workspace_members(user_id, workspace_id)\n'
    'memory_nodes(workspace_id, type, status)\n'
    'memory_nodes(workspace_id, created_at)\n'
    'memory_nodes(workspace_id, sensitivity)\n'
    'memory_edges(workspace_id, source_node_id)\n'
    'memory_edges(workspace_id, target_node_id)\n'
    'reminders(workspace_id, status, next_due_at)\n'
    'reminder_occurrences(status, due_at)\n'
    'notifications(status, created_at)\n'
    'jobs(status, priority, available_at)\n'
    'operations(workspace_id, status, created_at)\n'
    'execution_logs(workspace_id, created_at)\n'
    'file_assets(workspace_id, status)'
))

add_heading('15.2. Campos potencialmente cifrados', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Message.content_ciphertext',
    'MemoryNode.content_ciphertext y structured_data_ciphertext',
    'MemoryEdge.properties_ciphertext',
    'Reminder.description_ciphertext',
    'Agent.system_prompt_ciphertext',
    'FileAsset.original_name_ciphertext',
    'CredentialRef.encrypted_secret',
    'ExecutionLog.result_summary_ciphertext',
]))

# 16. Criterios de aceptación
add_heading('16. Criterios de aceptación del modelo', style_h1, level=0, story=story)
story.append(p('El modelo se considera preparado cuando cumple 16 criterios:'))
story.extend(numbered_list([
    'Se puede representar una memoria explícita y una memoria inferida.',
    'Se puede conservar procedencia y editar/versionar.',
    'Se puede relacionar nodos e invalidar una relación.',
    'Se puede crear recurrencia sin duplicar ocurrencias.',
    'Se puede registrar delivery.',
    'Se puede asignar una skill a un agente y revocar una tool permission.',
    'Se puede auditar una operación.',
    'Se puede almacenar un audio temporal.',
    'Se puede exportar e importar.',
    'Se puede utilizar SQLite y PostgreSQL.',
    'Se puede purgar un dato y sus derivados.',
    'Se puede sincronizar con detección de conflictos futura.',
]))

# 17. Conclusión Modelo de Datos
add_heading('17. Conclusión', style_h1, level=0, story=story)
story.append(p('El modelo de datos de VNBOT separa claramente identidad, workspaces, conversaciones, memorias, relaciones, recordatorios, ocurrencias, notificaciones, agentes, skills, integraciones, jobs, archivos, auditoría y datos derivados.'))
story.append(callout(
    'La fuente de verdad debe ser portable y comprensible; los índices, embeddings, caches y '
    'respuestas de IA deben ser derivados y reemplazables.',
    color=ACCENT
))

# Page break before next document
story.append(PageBreak())

# ============================================================
# DOCUMENTO 08 — SEGURIDAD Y PRIVACIDAD
# ============================================================
story.append(doc_divider('08', 'SEGURIDAD Y PRIVACIDAD',
    'Modelo de amenaza, criptografía, modos de privacidad, gestión de incidentes y testing de seguridad.',
    ACCENT_AMBER))
story.append(Spacer(1, 10))

# 1. Propósito
add_heading('1. Propósito', style_h1, level=0, story=story)
story.append(p(
    'VNBOT procesará información que puede ser íntima o sensible: recordatorios, relaciones '
    'personales, conversaciones, audios, documentos, datos de calendario, preferencias, correos '
    'y credenciales de integraciones. Este documento define cómo proteger esa información en '
    'todas las capas: Web/PWA, APK, desktop, CLI, backend, workers, base de datos, object '
    'storage, LLM Router, MCP Gateway, integraciones externas, CI/CD, backups y comunidad open source.'
))
story.append(p('La seguridad no se limita a cifrar tablas. VNBOT debe cumplir 7 objetivos:'))
story.extend(bullet_list([
    'Reducir la cantidad de datos recogidos.',
    'Separar datos por usuario y workspace.',
    'Limitar qué puede leer cada agente.',
    'Explicar cuándo los datos salen del dispositivo.',
    'Evitar acciones irreversibles sin confirmación.',
    'Permitir exportar, corregir y eliminar.',
    'Mantener trazabilidad sin registrar contenido privado innecesario.',
]))

# 2. Principios de seguridad
add_heading('2. Principios de seguridad', style_h1, level=0, story=story)
principios_sec = [
    ['Principio', 'Descripción'],
    ['Privacidad por defecto', 'Las funciones que impliquen proveedores externos, lectura de correo, envío de mensajes o acceso a archivos deben estar deshabilitadas por defecto.'],
    ['Mínimo privilegio', 'Cada usuario, agente, skill, integración y job recibe únicamente los permisos necesarios para su operación.'],
    ['Separación de secretos y contenido', 'Una API key, token OAuth o contraseña no son memorias normales. Deben residir en un almacén de secretos separado y no aparecer en logs, embeddings, prompts ni exportaciones normales.'],
    ['Transparencia operacional', 'El usuario debe poder saber qué modelo se utilizó, qué herramienta se llamó, qué datos se enviaron, qué acción fue ejecutada, qué quedó pendiente y qué se guardó como memoria.'],
    ['El LLM no es frontera de seguridad', 'Las instrucciones del modelo pueden estar equivocadas o manipuladas. La autorización se aplica fuera del prompt mediante código determinista.'],
    ['Fail closed para riesgo', 'Si el sistema no puede verificar permiso, identidad, fecha, destinatario o integridad, debe detener la operación y pedir revisión.'],
    ['Portabilidad', 'El usuario debe poder exportar sus datos en un formato documentado y no depender exclusivamente de un proveedor.'],
    ['Eliminación verificable', 'Borrar un dato implica considerar fuente, versiones, índices, embeddings, cache, archivos y backups según retención.'],
]
story.append(make_table(principios_sec, col_widths=[42*mm, 128*mm]))

# 3. Modelo de amenaza
add_heading('3. Modelo de amenaza', style_h1, level=0, story=story)
add_heading('3.1. Activos protegidos', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Bóveda de memoria, mensajes y conversaciones.',
    'Recordatorios y relaciones del grafo.',
    'Audios, imágenes y documentos.',
    'Calendarios, correos y contactos de terceros.',
    'API keys y tokens OAuth.',
    'Configuración de agentes y prompts privados.',
    'Skills instaladas, backups, logs y trazas.',
]))

add_heading('3.2. Actores de amenaza', style_h2, level=1, story=story)
amenazas_data = [
    ['Actor', 'Objetivo'],
    ['Atacante remoto', 'Explotar API, autenticación, archivos, SSRF o dependencias.'],
    ['Atacante con XSS', 'Ejecutar JavaScript en el navegador para robar sesión, modificar acciones o acceder a datos descifrados durante una sesión activa.'],
    ['Servidor comprometido', 'Leer base de datos, archivos, variables de entorno o procesos.'],
    ['Proveedor LLM externo', 'Recibir contexto si el usuario lo autoriza. El riesgo depende de su política, retención, ubicación y configuración.'],
    ['Servidor MCP malicioso', 'Devolver instrucciones manipuladoras, solicitar scopes excesivos o intentar extraer datos.'],
    ['Skill maliciosa', 'Usar instrucciones para pedir herramientas no necesarias o provocar acciones peligrosas.'],
    ['Extensión/navegador comprometido', 'Leer el DOM o interceptar eventos durante la sesión web.'],
    ['Persona con acceso al dispositivo', 'Acceder a archivos locales, backups, sesiones abiertas o claves almacenadas en el sistema.'],
    ['Usuario malicioso dentro de workspace', 'Consultar memorias, archivos o integraciones de otro miembro.'],
]
story.append(make_table(amenazas_data, col_widths=[45*mm, 125*mm]))
story.append(Spacer(1, 8))
story.append(p('Límites explícitos — no se puede garantizar protección absoluta contra:'))
story.extend(bullet_list([
    'Un sistema operativo completamente comprometido.',
    'Malware con acceso al proceso desbloqueado.',
    'Un usuario que entregue voluntariamente sus credenciales.',
    'Un administrador del servidor que controle la máquina y las claves de ejecución.',
    'Un proveedor externo que procese datos enviados bajo su propia política.',
]))

# 4. Modos de privacidad
add_heading('4. Modos de privacidad', style_h1, level=0, story=story)
modos_data = [
    ['Modo', 'Características', 'Límites'],
    ['Local Estricto', 'Memoria en SQLite/IndexedDB local, embeddings locales, audio local, LLM local (Ollama, llama.cpp), sin sync remota por defecto, sin analytics, exportación manual cifrada.', 'Si el dispositivo está comprometido o desbloqueado, el atacante podría acceder a datos procesados en memoria.'],
    ['Servidor Privado', 'API y DB en servidor elegido, acceso desde varios dispositivos, PostgreSQL, Redis y storage opcional, LLM local o proveedor configurado.', 'El administrador del servidor puede tener capacidad técnica para inspeccionar procesos, archivos o memoria. El cifrado en reposo no equivale automáticamente a zero-knowledge.'],
    ['LLM Externo', 'El usuario selecciona proveedor y modelo, se envía el contexto mínimo necesario, memorias secretas pueden bloquearse para proveedores externos, se muestra el proveedor utilizado.', 'Antes de activar este modo se debe mostrar: proveedor, modelo y datos excluidos.'],
]
story.append(make_table(modos_data, col_widths=[30*mm, 80*mm, 60*mm]))

# 5. Zero-knowledge
add_heading('5. Zero-knowledge: definición precisa', style_h1, level=0, story=story)
story.append(p('En VNBOT, "zero-knowledge" solo debe utilizarse si el componente concreto no puede leer el plaintext, incluyendo el flujo de interpretación necesario.'))
zk_data = [
    ['Caso', '¿Servidor ve plaintext?', 'Descripción correcta'],
    ['Bóveda local + LLM local', 'No, fuera del dispositivo', 'Procesamiento local'],
    ['DB con ciphertext + API cloud para analizar texto', 'Sí durante la solicitud', 'Cifrado en reposo, no ZK total'],
    ['Servidor propio con proceso que descifra', 'Sí, el servidor puede leerlo', 'Servidor privado'],
    ['WebCrypto con LLM externo', 'Sí, el proveedor recibe el texto', 'Cifrado local parcial'],
]
story.append(make_table(zk_data, col_widths=[60*mm, 40*mm, 70*mm]))
story.append(callout(
    'La documentación debe especificar siempre: dónde se cifra, dónde se descifra, quién puede '
    'ver plaintext, qué se envía a proveedores, qué se almacena y cuánto tiempo se conserva.',
    color=SEM_WARNING
))

# 6. Criptografía
add_heading('6. Criptografía', style_h1, level=0, story=story)
add_heading('6.1. Datos en reposo', style_h2, level=1, story=story)
story.extend(bullet_list([
    'AES-256-GCM.',
    'XChaCha20-Poly1305 cuando la librería soporte el algoritmo correctamente.',
    'Envelope encryption para servidores y backups.',
]))

add_heading('6.2. Derivación de claves', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Argon2id preferido para claves derivadas desde passphrase.',
    'Salt aleatorio único.',
    'Parámetros documentados y política de migración si se actualizan.',
    'Verificación de versión criptográfica.',
    'PBKDF2 puede mantenerse por compatibilidad web cuando sea necesario, documentado como decisión de compatibilidad.',
]))

add_heading('6.3. Claves por capas', style_h2, level=1, story=story)
story.append(code_block(
    'Passphrase del usuario\n'
    '  ↓ KDF\n'
    'Vault Key\n'
    '  ↓ envelope encryption\n'
    'Data Encryption Keys\n'
    '  ↓\n'
    'Memorias, archivos y backups'
))
story.append(p('Las claves de integración no deben derivarse de una memoria ni almacenarse junto al contenido.'))

# 7. Gestión de identidad
add_heading('7. Gestión de identidad', style_h1, level=0, story=story)
add_heading('7.1. Contraseñas y sesiones', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Argon2id para contraseñas con longitud mínima razonable.',
    'Rate limit y mensajes que no revelen existencia de cuentas.',
    'Cookies HttpOnly, Secure y SameSite.',
    'Expiración corta para access session + refresh token rotatorio.',
    'Revocación server-side y detección básica de reutilización.',
    'MFA posterior: TOTP, WebAuthn/passkeys, códigos de recuperación.',
]))

# 8. Autorización y aislamiento
add_heading('8. Autorización y aislamiento', style_h1, level=0, story=story)
add_heading('8.1. Capas de autorización', style_h2, level=1, story=story)
story.append(code_block(
    'Identity\n'
    '  ↓\n'
    'Workspace membership\n'
    '  ↓\n'
    'Resource ownership\n'
    '  ↓\n'
    'Agent permission\n'
    '  ↓\n'
    'Skill permission\n'
    '  ↓\n'
    'Tool scope\n'
    '  ↓\n'
    'Action risk policy'
))
add_heading('8.2. Workspace isolation', style_h2, level=1, story=story)
story.append(p('Cada query debe filtrar por workspace_id antes de:'))
story.extend(bullet_list([
    'Búsqueda textual.',
    'Búsqueda vectorial.',
    'Recorrido de grafo.',
    'Lectura de archivos.',
    'Selección de contexto para LLM.',
]))
story.append(callout(
    'Denegación por defecto: si no hay una política explícita, la operación se deniega o queda '
    'en espera de confirmación.',
    color=SEM_ERROR
))

# 9. Seguridad del frontend
add_heading('9. Seguridad del frontend', style_h1, level=0, story=story)
story.extend(bullet_list([
    '<b>XSS:</b> Sanitizar Markdown y HTML, no insertar directamente contenido de LLM, usar CSP, evitar dangerouslySetInnerHTML.',
    '<b>Almacenamiento local:</b> No guardar en localStorage API keys, refresh tokens, passphrases, secretos ni plaintext sensible. Usar IndexedDB cifrado, keychain del sistema, Secure Storage Android, cookies HttpOnly.',
    '<b>Archivos:</b> Validar MIME real, limitar tamaño, no ejecutar archivos subidos, no permitir path traversal, crear nombres internos.',
    '<b>CSP estricta:</b> Mantener actualizada. No permitir unsafe-eval salvo dependencia indispensable justificada.',
    '<b>Micrófono:</b> Solicitar permiso justo antes del uso, mostrar estado de grabación, no grabar en background sin indicación.',
    '<b>Clickjacking:</b> frame-ancestors none, X-Content-Type-Options nosniff, Referrer-Policy restrictiva, enlaces externos con noopener noreferrer.',
]))

# 10. Seguridad del backend
add_heading('10. Seguridad del backend', style_h1, level=0, story=story)
story.extend(bullet_list([
    '<b>Validación:</b> Todos los endpoints validan tipo, longitud, enumeraciones, fechas, tamaño de archivos, URLs, identificadores y JSON estructurado.',
    '<b>Rate limiting:</b> Por IP, usuario, workspace, agente, proveedor, herramienta, tipo de operación y coste/token. En despliegues múltiples usar Redis u otro almacén compartido.',
    '<b>SSRF:</b> Bloquear IPs privadas por defecto, resolver DNS y verificar destino final, limitar redirects, aplicar timeout, limitar respuesta, usar allowlist configurable.',
    '<b>SQL y comandos:</b> Usar queries parametrizadas/ORM seguro, no ejecutar comandos del sistema desde texto del usuario, no permitir shell a agentes en MVP.',
    '<b>Webhooks:</b> Firma HMAC, timestamp, nonce, protección replay, idempotency key, validación de proveedor, respuesta rápida y procesamiento asíncrono.',
    '<b>Deserialización:</b> No deserializar objetos arbitrarios provenientes de archivos, MCP o integraciones. Usar schemas explícitos.',
]))

# 11. Seguridad de LLM
add_heading('11. Seguridad de LLM', style_h1, level=0, story=story)
add_heading('11.1. Prompt injection y separación de instrucciones', style_h2, level=1, story=story)
story.append(p('El contenido de emails, webs, documentos, notas y servidores MCP debe tratarse como datos no confiables. Un texto externo no puede cambiar las instrucciones de seguridad del agente.'))
story.append(code_block(
    'System policy\n'
    '  ↓ prioridad máxima\n'
    'Skill instructions\n'
    '  ↓\n'
    'Agent configuration\n'
    '  ↓\n'
    'User request\n'
    '  ↓\n'
    'External content/data'
))

add_heading('11.2. Tool calling — el LLM propone, no ejecuta', style_h2, level=1, story=story)
story.append(p('El LLM propone una tool call; no la ejecuta directamente. El backend debe:'))
story.extend(numbered_list([
    'Validar nombre.',
    'Validar argumentos.',
    'Comprobar permiso.',
    'Evaluar riesgo.',
    'Pedir confirmación si aplica.',
    'Ejecutar con timeout.',
    'Auditar.',
]))

# 12. Seguridad de MCP
add_heading('12. Seguridad de MCP', style_h1, level=0, story=story)
story.append(p('MCP no es una capa automática de confianza. Un servidor MCP puede estar mal configurado, comprometido o diseñado para solicitar más datos de los necesarios.'))
add_heading('12.1. Herramientas peligrosas que requieren confirmación fuerte', style_h2, level=1, story=story)
story.extend(bullet_list([
    'email.send',
    'filesystem.write',
    'memory.delete_many',
    'calendar.delete_event',
    'share.create',
    'Herramientas con efectos externos irreversibles.',
]))
add_heading('12.2. Aislamiento', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Credenciales por integración.',
    'Timeouts y límites de respuesta.',
    'Límite de tool calls.',
    'Sin acceso a variables de entorno globales.',
    'Red restringida.',
    'No ejecutar servidores externos como root.',
    'Revocación inmediata.',
]))

# 13. Logs, auditoría y telemetría
add_heading('13. Logs, auditoría y telemetría', style_h1, level=0, story=story)
add_heading('13.1. Logs operativos permitidos', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Request ID, Operation ID, Job ID.',
    'Estado, duración, error code.',
    'Modelo/proveedor, conteos, tamaño agregado.',
]))
add_heading('13.2. No registrar por defecto', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Plaintext, audio, passwords.',
    'API keys, OAuth tokens, cookies.',
    'Contenido completo de email.',
    'Prompt completo si contiene datos privados.',
]))
story.append(callout(
    'Telemetría opt-in: debe estar desactivada por defecto en modo privado, no incluir contenido, '
    'ser agregada, documentar eventos, permitir desactivar y no utilizar identificadores personales innecesarios.',
    color=SEM_WARNING
))

# 14. Backups y recuperación
add_heading('14. Backups y recuperación', style_h1, level=0, story=story)
story.extend(bullet_list([
    'El backup debe cifrarse antes de salir del dispositivo o servidor.',
    'La clave de backup no debe almacenarse junto al archivo. Puede conservarse en passphrase del usuario, keychain, secret manager o hardware key futura.',
    'Un backup no se considera válido hasta que pueda restaurarse en un entorno de prueba.',
    'Ransomware y corrupción: mantener versiones, checksums, backups offline o inmutables cuando sea posible, detectar cambios anómalos, no sobrescribir el único backup.',
]))

# 15. Gestión de incidentes
add_heading('15. Gestión de incidentes', style_h1, level=0, story=story)
add_heading('15.1. Clasificación', style_h2, level=1, story=story)
clasif_data = [
    ['Nivel', 'Descripción'],
    ['P0', 'Exposición activa o pérdida masiva.'],
    ['P1', 'Vulnerabilidad explotable o servicio crítico afectado.'],
    ['P2', 'Impacto limitado o configuración incorrecta.'],
    ['P3', 'Mejora o vulnerabilidad de bajo impacto.'],
]
story.append(make_table(clasif_data, col_widths=[20*mm, 150*mm]))

add_heading('15.2. Flujo de respuesta', style_h2, level=1, story=story)
story.append(code_block(
    'Detectar\n'
    '  ↓\n'
    'Contener\n'
    '  ↓\n'
    'Evaluar alcance\n'
    '  ↓\n'
    'Revocar/rotar credenciales\n'
    '  ↓\n'
    'Preservar evidencia mínima\n'
    '  ↓\n'
    'Corregir\n'
    '  ↓\n'
    'Verificar\n'
    '  ↓\n'
    'Comunicar según corresponda\n'
    '  ↓\n'
    'Postmortem'
))

# 16. Testing de seguridad
add_heading('16. Testing de seguridad', style_h1, level=0, story=story)
add_heading('16.1. Automatizado en CI (obligatorio desde día uno)', style_h2, level=1, story=story)
testing_sec = [
    ['Herramienta', 'Propósito', 'Frecuencia'],
    ['Gitleaks', 'Detección de secretos en commits', 'Cada PR'],
    ['Semgrep', 'SAST (análisis estático)', 'Cada PR'],
    ['npm audit / pip-audit', 'Vulnerabilidades en dependencias', 'Cada PR y nightly'],
    ['Trivy', 'Scan de contenedores Docker', 'Cada build de imagen'],
]
story.append(make_table(testing_sec, col_widths=[40*mm, 70*mm, 60*mm]))

add_heading('16.2. Antes de cada release', style_h2, level=1, story=story)
story.extend(bullet_list([
    'DAST con OWASP ZAP para todos los endpoints públicos.',
    'Dependencias con Snyk / Grype para todo el árbol.',
    'Permisos: revisión manual de archivos de configuración, Docker, CI.',
    'Secrets con TruffleHog para historial completo del repo.',
]))

add_heading('16.3. Antes de v1.0', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Pentest básico por un revisor externo.',
    'Revisión del threat model completo.',
    'Revisión de todos los scopes de MCP.',
    'Revisión de backups y restore.',
    'Revisión de exportación/importación.',
    'Test de recuperación ante desastre.',
]))

# 17. Criterios de aceptación de seguridad
add_heading('17. Criterios de aceptación de seguridad', style_h1, level=0, story=story)
story.append(p('VNBOT cumple el baseline de seguridad cuando satisface 20 criterios:'))
story.extend(numbered_list([
    'Las contraseñas no se almacenan en texto.',
    'Los tokens se pueden revocar.',
    'Un usuario no puede leer otro workspace.',
    'Un agente no puede usar una herramienta no autorizada.',
    'Las acciones de riesgo requieren confirmación.',
    'Las respuestas de LLM no ejecutan código directamente.',
    'MCP está sujeto a scopes y timeouts.',
    'Los archivos no permiten path traversal.',
    'Los logs no contienen secretos.',
    'Las claves no viven en localStorage.',
    'La aplicación tiene CSP y sanitización.',
    'Los backups están cifrados.',
    'Existe exportación y eliminación.',
    'Se pueden reconstruir índices derivados.',
    'Hay healthchecks y alertas.',
    'Existe SECURITY.md.',
    'La CI escanea secretos y dependencias.',
    'Los releases tienen checksums o firma.',
    'La política de privacidad distingue local, servidor privado y cloud.',
    'Las integraciones oficiales se documentan con sus scopes y límites.',
]))

# 18. Conclusión Seguridad
add_heading('18. Conclusión', style_h1, level=0, story=story)
story.append(p('La seguridad de VNBOT no debe depender de una única función de cifrado. Debe surgir de la combinación de:'))
story.append(code_block(
    'Minimización de datos\n'
    '+ aislamiento por workspace\n'
    '+ permisos por agente\n'
    '+ scopes MCP\n'
    '+ validación determinista\n'
    '+ cifrado adecuado\n'
    '+ jobs auditables\n'
    '+ logs sanitizados\n'
    '+ backups verificables\n'
    '+ exportación y borrado\n'
    '+ documentación honesta'
))
story.append(callout(
    'VNBOT debe ser extensible en capacidades, pero restrictivo en autoridad.',
    color=ACCENT_AMBER
))

# Page break before next document
story.append(PageBreak())

# ============================================================
# DOCUMENTO 09 — MCP Y SKILLS
# ============================================================
story.append(doc_divider('09', 'MCP Y SKILLS',
    'Tools, scopes, agentes, autonomía, marketplace futuro y contract testing.',
    ACCENT_MAG))
story.append(Spacer(1, 10))

# 1. Propósito
add_heading('1. Propósito', style_h1, level=0, story=story)
story.append(p(
    'VNBOT debe poder crecer sin que cada nueva capacidad obligue a modificar el núcleo de '
    'memoria, recordatorios y usuarios. Para ello utilizará dos mecanismos relacionados, pero '
    'diferentes: MCP (protocolo para conectar herramientas, recursos y prompts externos o '
    'internos) y Skills (capacidades de comportamiento versionadas que indican cómo realizar '
    'una tarea y qué herramientas necesitan).'
))
story.append(p('Los agentes son la combinación de:'))
story.append(code_block(
    'Modelo\n'
    '+ instrucciones\n'
    '+ skills\n'
    '+ memoria permitida\n'
    '+ herramientas permitidas\n'
    '+ política de autonomía\n'
    '+ presupuesto\n'
    '+ identidad visual'
))
story.append(callout(
    'La extensibilidad no debe significar autoridad ilimitada. Un agente puede saber cómo usar '
    'una herramienta, pero el policy engine decide si tiene permiso para usarla en una operación concreta.',
    color=ACCENT_MAG
))

# 2. Principios
add_heading('2. Principios', style_h1, level=0, story=story)
principios_mcp = [
    ['Principio', 'Descripción'],
    ['MCP no es autorización', 'MCP define cómo intercambiar contexto y herramientas. No decide si una acción es segura para VNBOT. La autorización se implementa en el gateway y en el dominio.'],
    ['Deny by default', 'Una herramienta nueva aparece deshabilitada hasta que se registra, inspecciona, asigna scope, revisa riesgo y el usuario la activa.'],
    ['El LLM propone, el policy engine decide', 'LLM → propone tool call · Schema → valida argumentos · Policy → valida permiso/riesgo · Usuario → confirma cuando aplica · Executor → ejecuta · Audit → registra.'],
    ['Memoria mínima', 'Un agente recibe el mínimo contexto necesario para una skill. No se inyecta toda la bóveda por defecto.'],
    ['Herramientas pequeñas', 'Las tools deben tener responsabilidades concretas. Es preferible calendar.create_event + calendar.list_events + calendar.delete_event en lugar de system.do_anything.'],
    ['Reversibilidad', 'Las acciones deben ser reversibles o requerir confirmación si no lo son.'],
    ['Versionado', 'MCP servers, tools, skills, manifests y agentes deben poder versionarse y migrarse.'],
]
story.append(make_table(principios_mcp, col_widths=[42*mm, 128*mm]))

# 3. Arquitectura MCP
add_heading('3. Arquitectura MCP de VNBOT', style_h1, level=0, story=story)
story.append(code_block(
    '┌──────────────────────────────────────────────┐\n'
    '│                VNBOT CLIENTS                 │\n'
    '│ Web · Android · Desktop · CLI                │\n'
    '└─────────────────────┬────────────────────────┘\n'
    '                      ▼\n'
    '┌──────────────────────────────────────────────┐\n'
    '│              VNBOT API / ORCHESTRATOR        │\n'
    '│ Conversations · Operations · Agents · Policy │\n'
    '└─────────────────────┬────────────────────────┘\n'
    '                      ▼\n'
    '┌──────────────────────────────────────────────┐\n'
    '│                 MCP GATEWAY                  │\n'
    '│ Registry · Scopes · Router · Timeouts · Audit│\n'
    '└───────────────┬──────────────┬───────────────┘\n'
    '                │              │\n'
    '                ▼              ▼\n'
    '        MCP internal      MCP external\n'
    '        memory/tools      Graphify/calendar/email'
))

add_heading('3.1. MCP interno (13 tools)', style_h2, level=1, story=story)
story.append(code_block(
    'memory_search · memory_create · memory_update\n'
    'memory_forget · memory_link · graph_expand\n'
    'reminder_create · reminder_update · reminder_complete\n'
    'reminder_snooze · list_create · list_update\n'
    'briefing_generate'
))

add_heading('3.2. MCP externo', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Graphify (repos de código).',
    'Calendarios (Google, ICS, CalDAV).',
    'Email (Gmail, IMAP).',
    'Filesystem (carpetas locales).',
    'Web/search.',
    'Notas (Obsidian, Notion).',
    'Mensajería oficial (Telegram, WhatsApp Business).',
    'Herramientas de desarrollo.',
]))

# 4. Registro de servidores MCP
add_heading('4. Registro de servidores MCP', style_h1, level=0, story=story)
add_heading('4.1. Flujo de registro', style_h2, level=1, story=story)
story.append(code_block(
    'Usuario pulsa Añadir MCP\n'
    '  ↓\n'
    'Selecciona local o remoto\n'
    '  ↓\n'
    'Introduce comando/endpoint\n'
    '  ↓\n'
    'VNBOT valida formato\n'
    '  ↓\n'
    'Realiza handshake\n'
    '  ↓\n'
    'Descubre capabilities/tools/resources\n'
    '  ↓\n'
    'Clasifica riesgo\n'
    '  ↓\n'
    'Usuario selecciona scopes\n'
    '  ↓\n'
    'Healthcheck\n'
    '  ↓\n'
    'Guardar configuración\n'
    '  ↓\n'
    'Servidor disponible de forma controlada'
))

add_heading('4.2. Registro local (stdio)', style_h2, level=1, story=story)
story.append(code_block(
    '{\n'
    '  "name": "graphify-local",\n'
    '  "transport": "stdio",\n'
    '  "command": "graphify",\n'
    '  "args": ["mcp", "serve"],\n'
    '  "working_directory": "/home/user/projects/vnbot",\n'
    '  "allowed_paths": ["/home/user/projects/vnbot"]\n'
    '}'
))
story.append(p('El comando debe ejecutarse con un usuario sin privilegios y con directorios limitados.'))

add_heading('4.3. Registro remoto (Streamable HTTP)', style_h2, level=1, story=story)
story.append(code_block(
    '{\n'
    '  "name": "calendar-server",\n'
    '  "transport": "streamable_http",\n'
    '  "endpoint": "https://mcp.example.com/mcp",\n'
    '  "auth_type": "oauth2",\n'
    '  "scopes": ["calendar.read"]\n'
    '}'
))
story.append(callout(
    'Las credenciales se almacenan en un secret store. No se guardan en el documento de '
    'configuración público.',
    color=SEM_WARNING
))

# 5. Scopes y permisos
add_heading('5. Scopes y permisos', style_h1, level=0, story=story)
add_heading('5.1. Scopes iniciales (15 scopes)', style_h2, level=1, story=story)
story.append(code_block(
    'graph.read · graph.write\n'
    'memory.read · memory.write · memory.delete\n'
    'calendar.read · calendar.write · calendar.delete\n'
    'email.read · email.draft · email.send\n'
    'filesystem.read · filesystem.write\n'
    'web.fetch · notification.send'
))

add_heading('5.2. Niveles de permiso', style_h2, level=1, story=story)
story.extend(bullet_list([
    '<b>deny</b> — denegado.',
    '<b>read</b> — solo lectura.',
    '<b>write</b> — escritura.',
    '<b>execute</b> — ejecución.',
    '<b>admin</b> — administración (no autorización genérica para todo el sistema).',
]))

add_heading('5.3. Matriz de permisos comprensible', style_h2, level=1, story=story)
story.append(p('La UI debe presentar una matriz comprensible:'))
story.append(code_block(
    'Agente: Beacon\n'
    '\n'
    'Memoria personal       Leer ✓   Escribir ✓   Borrar ✕\n'
    'Calendario             Leer ✓   Crear ✓      Borrar ✕\n'
    'Correo                 Leer ✕   Borrador ✕   Enviar ✕\n'
    'Filesystem             Leer ✕   Escribir ✕\n'
    'Graphify               Leer ✓   Escribir ✕'
))

# 6. Clasificación de riesgo
add_heading('6. Clasificación de riesgo de herramientas', style_h1, level=0, story=story)
riesgo_mcp = [
    ['Nivel', 'Ejemplos'],
    ['Bajo', 'Buscar memoria, leer calendario, listar tareas, consultar healthcheck, crear lista local, generar resumen.'],
    ['Medio', 'Crear memoria, crear recordatorio, crear evento, actualizar preferencia, sincronizar documento.'],
    ['Alto', 'Leer emails completos, crear borradores, compartir información, leer directorios personales, enviar notificaciones a terceros, modificar eventos existentes.'],
    ['Crítico', 'Enviar emails, borrar datos masivamente, escribir archivos arbitrarios, cambiar permisos, acciones financieras, ejecutar comandos del sistema.'],
]
story.append(make_table(riesgo_mcp, col_widths=[22*mm, 148*mm]))
story.append(callout(
    'Las acciones críticas no estarán disponibles en el MVP o exigirán confirmación fuerte, '
    'reautenticación y límites adicionales.',
    color=SEM_ERROR
))

# 7. Confirmaciones
add_heading('7. Confirmaciones', style_h1, level=0, story=story)
add_heading('7.1. Confirmación simple (riesgo bajo/medio)', style_h2, level=1, story=story)
story.append(code_block(
    'Voy a crear este recordatorio:\n'
    'Título: Revisar presupuesto\n'
    'Fecha: lunes 20 de julio, 09:00\n'
    'Agente: Beacon\n'
    '\n'
    '[Confirmar] [Editar] [Cancelar]'
))

add_heading('7.2. Confirmación fuerte (riesgo alto)', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Mostrar tool exacta.',
    'Mostrar destino y contenido completo.',
    'Mostrar scopes utilizados y agente.',
    'Requerir interacción explícita.',
    'Solicitar reautenticación si es necesario.',
]))

add_heading('7.3. Confirmación caducada', style_h2, level=1, story=story)
story.append(p('Una propuesta no confirmada después de su TTL debe pasar a EXPIRED. Si el usuario intenta confirmarla, debe recalcularse.'))

# 8. Skills
add_heading('8. Skills', style_h1, level=0, story=story)
add_heading('8.1. Estructura de una skill', style_h2, level=1, story=story)
story.append(code_block(
    'id · version · name · description · license\n'
    'author/source · risk_level\n'
    'required_tools · memory_scopes\n'
    'confirmation_policy\n'
    'input_schema · output_schema\n'
    'instructions'
))

add_heading('8.2. Manifest YAML', style_h2, level=1, story=story)
story.append(code_block(
    'id: reminder.create\n'
    'version: 1.0.0\n'
    'name: Crear recordatorio\n'
    'description: Convierte lenguaje natural en un recordatorio validado\n'
    'license: MIT\n'
    'risk_level: low\n'
    'required_tools:\n'
    '  - reminder_create\n'
    'memory_scopes:\n'
    '  - personal\n'
    'confirmation_policy: required_if_ambiguous\n'
    'input_schema: schemas/reminder-input.json\n'
    'output_schema: schemas/reminder-output.json'
))

add_heading('8.3. Skills iniciales (19 skills)', style_h2, level=1, story=story)
story.append(code_block(
    'capture.note · capture.audio\n'
    'memory.save · memory.search · memory.correct · memory.forget · memory.link\n'
    'reminder.create · reminder.edit · reminder.snooze · reminder.complete\n'
    'list.manage\n'
    'briefing.daily · briefing.weekly\n'
    'graph.explore\n'
    'calendar.read · calendar.create_event\n'
    'email.draft\n'
    'mcp.connect'
))

# 9. Ciclo de vida de una skill
add_heading('9. Ciclo de vida de una skill', style_h1, level=0, story=story)
story.append(code_block(
    'available\n'
    '  ↓\n'
    'review_required\n'
    '  ↓\n'
    'installed\n'
    '  ↓\n'
    'assigned_to_agent\n'
    '  ↓\n'
    'enabled\n'
    '  ↓\n'
    'updated/paused\n'
    '  ↓\n'
    'revoked/uninstalled'
))

add_heading('9.1. Actualización de skills', style_h2, level=1, story=story)
story.append(p('Si cambia cualquiera de estos campos se requiere revisión del usuario:'))
story.extend(bullet_list([
    'required_tools',
    'memory_scopes',
    'risk_level',
    'confirmation_policy',
]))

# 10. Agentes
add_heading('10. Agentes', style_h1, level=0, story=story)
add_heading('10.1. Configuración de un agente', style_h2, level=1, story=story)
story.append(code_block(
    'Agent\n'
    '- name · description · avatar\n'
    '- model · system instructions\n'
    '- skills · memory scopes · tools\n'
    '- autonomy level · budget\n'
    '- schedule · status'
))

add_heading('10.2. Agentes iniciales (7 agentes)', style_h2, level=1, story=story)
agentes_data = [
    ['Agente', 'Orientación', 'Herramientas externas'],
    ['VNBOT Core', 'Asistente general de bajo riesgo', 'Buscar memoria y proponer recordatorios'],
    ['Archivista', 'Guardar, organizar y recuperar memorias', 'No tiene herramientas externas por defecto'],
    ['Beacon', 'Recordatorios y tareas', 'Crear y gestionar recordatorios internos'],
    ['Navigator', 'Calendario', 'Inicia con lectura y propone eventos'],
    ['Forge', 'Proyectos e ideas', 'Crear listas, notas y relaciones'],
    ['Sentinel', 'Seguridad, permisos, healthchecks y auditoría', 'No ejecuta acciones externas'],
    ['Scout', 'Investigación con web/MCP', 'Trata contenido externo como no confiable'],
]
story.append(make_table(agentes_data, col_widths=[28*mm, 65*mm, 77*mm]))

# 11. Niveles de autonomía
add_heading('11. Niveles de autonomía (0-4)', style_h1, level=0, story=story)
autonomia_data = [
    ['Nivel', 'Nombre', 'Capacidades'],
    ['0', 'Responder', 'El agente solo genera respuestas. No crea datos.'],
    ['1', 'Proponer', 'Puede presentar memorias, recordatorios o tool calls para aprobación.'],
    ['2', 'Acciones internas', 'Puede crear y modificar datos internos según skills permitidas.'],
    ['3', 'Integraciones confirmadas', 'Puede preparar acciones externas y ejecutarlas después de confirmación.'],
    ['4', 'Automatización limitada', 'Puede ejecutar reglas explícitas bajo horario, presupuesto, lista cerrada de herramientas, máximo de llamadas, registro y botón de parada.'],
]
story.append(make_table(autonomia_data, col_widths=[15*mm, 40*mm, 115*mm]))
story.append(callout(
    'Nunca debe existir una opción "sin límites" en el sentido de acceso total al sistema.',
    color=SEM_ERROR
))

# 12. Memoria accesible por agente
add_heading('12. Memoria accesible por agente', style_h1, level=0, story=story)
add_heading('12.1. Scopes de memoria', style_h2, level=1, story=story)
story.append(code_block(
    'personal · work · study · family\n'
    'project:vnbot · sensitive · secret'
))

add_heading('12.2. Reglas de memoria por agente', style_h2, level=1, story=story)
story.extend(bullet_list([
    'secret no se incluye en prompts externos.',
    'Un agente solo consulta scopes asignados.',
    'Los scopes se filtran antes del LLM.',
    'La UI muestra qué scopes utiliza.',
    'Un agente no puede cambiar sus propios scopes.',
]))

add_heading('12.3. Context assembly', style_h2, level=1, story=story)
story.append(code_block(
    'User request\n'
    '  ↓\n'
    'Skill active\n'
    '  ↓\n'
    'Memory scopes\n'
    '  ↓\n'
    'Relevant retrieval\n'
    '  ↓\n'
    'Redaction\n'
    '  ↓\n'
    'Prompt context'
))

# 13. Presupuesto y límites
add_heading('13. Presupuesto y límites', style_h1, level=0, story=story)
add_heading('13.1. Límites por agente', style_h2, level=1, story=story)
story.append(code_block(
    'max_tokens_per_operation\n'
    'max_cost_per_day\n'
    'max_tool_calls_per_operation\n'
    'max_external_calls_per_hour\n'
    'max_memory_results\n'
    'max_graph_depth\n'
    'max_file_bytes'
))

add_heading('13.2. Exceso de presupuesto', style_h2, level=1, story=story)
story.append(callout(
    'El sistema debe detenerse con estado explícito BUDGET_EXCEEDED. No debe cambiar '
    'silenciosamente a un proveedor más costoso.',
    color=SEM_WARNING
))

# 14. Tool execution
add_heading('14. Tool execution — preflight, ejecución y post', style_h1, level=0, story=story)
add_heading('14.1. Preflight (antes de ejecutar)', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Tool existe.',
    'Servidor healthy.',
    'Schema válido.',
    'Scope presente.',
    'Usuario autorizado.',
    'Presupuesto disponible.',
    'Confirmación vigente.',
    'Idempotency key.',
]))

add_heading('14.2. Ejecución', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Timeout.',
    'Cancelación.',
    'Captura de status.',
    'Sanitización de resultado.',
    'Límite de respuesta.',
]))

add_heading('14.3. Post-execution', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Guardar resumen.',
    'Actualizar recurso interno si corresponde.',
    'Invalidar cache.',
    'Registrar auditoría.',
    'Actualizar UI.',
    'Mostrar resultado y warnings.',
]))

# 15. Contract testing
add_heading('15. Contract testing para herramientas MCP', style_h1, level=0, story=story)
story.append(p('Cada herramienta MCP integrada en VNBOT debe tener contract tests que verifiquen su comportamiento sin depender de un servidor MCP real.'))
contract_data = [
    ['Aspecto', 'Verificación'],
    ['Input schema', 'El schema declarado coincide con lo que la tool realmente acepta.'],
    ['Output schema', 'El output real coincide con el schema declarado.'],
    ['Scopes', 'La tool solo accede a los recursos que sus scopes permiten.'],
    ['Aislamiento', 'Un fallo en la tool no propaga al resto del sistema.'],
    ['Timeout', 'La tool respeta el timeout configurado.'],
    ['Idempotencia', 'Llamar la tool dos veces con los mismos args produce el mismo resultado (cuando aplica).'],
]
story.append(make_table(contract_data, col_widths=[35*mm, 135*mm]))

add_heading('15.1. Métricas de tools', style_h2, level=1, story=story)
story.append(code_block(
    'vnbot_mcp_tool_calls_total{tool_name, status}\n'
    'vnbot_mcp_tool_duration_seconds{tool_name}\n'
    'vnbot_mcp_tool_permissions_denied{tool_name, scope}'
))

# 16. Criterios de aceptación
add_heading('16. Criterios de aceptación', style_h1, level=0, story=story)
add_heading('16.1. MCP está correctamente implementado cuando (13 criterios)', style_h2, level=1, story=story)
story.extend(numbered_list([
    'Se puede registrar un servidor local o remoto.',
    'El handshake queda auditado.',
    'Las tools descubiertas aparecen deshabilitadas por defecto.',
    'El usuario selecciona scopes.',
    'El agente solo ve herramientas autorizadas.',
    'Las llamadas tienen schemas.',
    'Las operaciones de riesgo requieren confirmación.',
    'Existen timeouts y límites.',
    'El servidor puede revocarse.',
    'El fallo de un MCP no rompe VNBOT.',
    'Los logs no contienen secretos.',
    'Graphify funciona como integración opcional.',
    'Las respuestas externas se tratan como datos no confiables.',
]))

add_heading('16.2. Una skill está lista cuando', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Tiene manifest, licencia y input/output schema.',
    'Declara herramientas, memoria y riesgo.',
    'Tiene instrucciones claras, tests y simulación.',
    'Tiene manejo de error.',
    'Puede desactivarse.',
    'No puede ampliar permisos sola.',
]))

add_heading('16.3. Un agente está listo cuando', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Tiene identidad, propósito y mascota/estado.',
    'Tiene modelo configurable, skills definidas y scopes de memoria.',
    'Tiene tools permitidas y autonomía explícita.',
    'Tiene presupuesto, simulación y auditoría.',
    'Puede pausarse y revocarse.',
]))

# 17. Conclusión MCP y Skills
add_heading('17. Conclusión', style_h1, level=0, story=story)
story.append(p('MCP y las skills permiten que VNBOT crezca desde una aplicación de recordatorios hasta una plataforma de agentes personalizables. Pero esa expansión solo es sostenible si cada capacidad tiene límites claros.'))
story.append(p('La arquitectura de VNBOT queda definida así:'))
story.append(code_block(
    'Skill describe cómo trabajar.\n'
    'Agente define quién trabaja.\n'
    'MCP conecta qué puede usar.\n'
    'Policy engine decide si puede usarlo.\n'
    'Usuario confirma cuando el riesgo lo exige.\n'
    'Auditoría registra lo ocurrido.'
))
story.append(callout(
    'Una herramienta puede estar conectada sin estar autorizada; un agente puede conocer una '
    'skill sin tener permiso para ejecutarla.',
    color=ACCENT_MAG
))

# ===== Build PDF =====
output_body = '/home/z/my-project/scripts/vol1_body.pdf'
doc = TocDocTemplate(
    output_body,
    pagesize=A4,
    leftMargin=20*mm,
    rightMargin=20*mm,
    topMargin=22*mm,
    bottomMargin=22*mm,
    title='VNBOT — Volumen I: Datos, Seguridad y Extensibilidad',
    author='VNBOT Project',
    subject='Compilado v1.0.0-draft — Modelo de Datos + Seguridad + MCP y Skills',
    creator='Z.ai',
)
doc.multiBuild(story, onFirstPage=page_decoration, onLaterPages=page_decoration)
print(f'Body PDF generated: {output_body}')
print(f'Size: {os.path.getsize(output_body) / 1024:.1f} KB')
