#!/usr/bin/env python3
"""
VNBOT Volumen II — Roadmap y Sincronización
Compila 2 documentos: Roadmap (10) + Estrategia de Sync (11)
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
ACCENT        = colors.HexColor('#0E7490')   # cyan — Roadmap
ACCENT_AMBER  = colors.HexColor('#B45309')   # amber — Sync
ACCENT_MAG    = colors.HexColor('#7152cb')
TEXT_PRIMARY  = colors.HexColor('#111827')
TEXT_MUTED    = colors.HexColor('#6B7280')
SEM_SUCCESS   = colors.HexColor('#047857')
SEM_WARNING   = colors.HexColor('#B45309')
SEM_ERROR     = colors.HexColor('#B91C1C')
SEM_INFO      = colors.HexColor('#4e769e')
CODE_BG       = colors.HexColor('#0F172A')
CODE_TEXT     = colors.HexColor('#E5F1FF')

# Version colors for roadmap
VERSION_COLORS = {
    '0.1': colors.HexColor('#22D3EE'),  # cyan
    '0.2': colors.HexColor('#10B981'),  # green
    '0.3': colors.HexColor('#4e769e'),  # blue
    '0.4': colors.HexColor('#7152cb'),  # purple
    '0.5': colors.HexColor('#0E7490'),  # dark cyan
    '0.6': colors.HexColor('#B91C1C'),  # red
    '0.7': colors.HexColor('#7152cb'),  # purple
    '0.8': colors.HexColor('#047857'),  # green
    '0.9': colors.HexColor('#1F2937'),  # dark
    '1.0': colors.HexColor('#047857'),  # stable green
}

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

style_checklist = ParagraphStyle('Checklist', parent=style_body,
    leftIndent=22, bulletIndent=8, spaceAfter=3, alignment=TA_LEFT,
    fontName='NotoSerifSC', bulletFontName='Mono', bulletFontSize=10)

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

def checklist(items):
    return [Paragraph(item, style_checklist, bulletText='[ ]') for item in items]

def make_table(data, col_widths=None, header=True, version_col=None):
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
    # Version column coloring
    if version_col is not None:
        for i in range(1, len(data)):
            try:
                version = str(data[i][version_col]).strip()
                # Extract version prefix (e.g. "0.1", "1.0")
                if '.' in version:
                    parts = version.split('.')
                    vkey = f"{parts[0]}.{parts[1]}" if len(parts) > 1 else parts[0]
                    if vkey in VERSION_COLORS:
                        style_cmds.append(('BACKGROUND', (version_col, i), (version_col, i), VERSION_COLORS[vkey]))
                        style_cmds.append(('TEXTCOLOR', (version_col, i), (version_col, i), colors.white))
                        style_cmds.append(('FONTNAME', (version_col, i), (version_col, i), 'Mono-Bold'))
                        style_cmds.append(('ALIGN', (version_col, i), (version_col, i), 'CENTER'))
                        style_cmds.append(('VALIGN', (version_col, i), (version_col, i), 'MIDDLE'))
            except (ValueError, IndexError):
                pass
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
    canv.drawString(20*mm, 12*mm, 'VNBOT // VOL II // v1.0.0-draft')
    canv.drawRightString(190*mm, 12*mm, f'{page_num}')
    canv.setStrokeColor(BORDER)
    canv.setLineWidth(0.4)
    canv.line(20*mm, 15*mm, 190*mm, 15*mm)
    if page_num > 1:
        canv.setFont('Mono', 7.5)
        canv.setFillColor(TEXT_MUTED)
        canv.drawString(20*mm, 285*mm, 'VNBOT — Vol II: Roadmap · Sincronización')
        canv.drawRightString(190*mm, 285*mm, '10+11')
        canv.line(20*mm, 283*mm, 190*mm, 283*mm)
    canv.restoreState()

# ===== Build story =====
story = []

# --- TOC ---
story.append(Paragraph('Tabla de Contenidos', style_toc_title))
story.append(HRFlowable(width='100%', thickness=1, color=ACCENT, spaceAfter=14))
story.append(Paragraph(
    'Este volumen compila 2 documentos de VNBOT: Roadmap y Estrategia de Sincronización. '
    'El Roadmap define la evolución del producto desde la demo hasta el release estable; '
    'la Estrategia de Sync define cómo se sincronizan datos entre múltiples dispositivos '
    'con detección y resolución de conflictos.',
    style_body))
story.append(Spacer(1, 14))
toc = TableOfContents()
toc.levelStyles = [toc_level0, toc_level1]
story.append(toc)
story.append(PageBreak())

# ============================================================
# DOCUMENTO 10 — ROADMAP
# ============================================================
story.append(doc_divider('10', 'ROADMAP',
    'Plan de evolución del producto: fases 0.1→1.0, versionado, métricas y comunidad.',
    ACCENT))
story.append(Spacer(1, 10))

# 1. Propósito
add_heading('1. Propósito', style_h1, level=0, story=story)
story.append(p(
    'Este roadmap define cómo VNBOT evolucionará desde una demostración pública hasta una '
    'plataforma open source de memoria personal, recordatorios y mini-agentes. El roadmap no '
    'debe interpretarse como una promesa de fechas rígidas. Define prioridades, dependencias '
    'y condiciones de salida. Las funciones se incorporan cuando el núcleo anterior es '
    'confiable, no simplemente porque sean atractivas o técnicamente posibles.'
))
story.append(p('La prioridad estratégica es:'))
story.append(code_block(
    'Confiabilidad\n'
    '→ privacidad\n'
    '→ memoria\n'
    '→ distribución\n'
    '→ extensibilidad\n'
    '→ integraciones\n'
    '→ autonomía'
))

# 2. Principios del roadmap
add_heading('2. Principios del roadmap', style_h1, level=0, story=story)
principios_rm = [
    ['Principio', 'Descripción'],
    ['Publicar pronto, pero no inseguro', 'La demo de GitHub Pages puede publicarse temprano porque no procesa datos reales. Las funciones con memoria real, audio, archivos e integraciones deben pasar por controles adicionales.'],
    ['Cada release utilizable', 'Una release no debe ser solo una colección de commits. Cada versión debe resolver un flujo concreto y tener documentación, instalación, pruebas, notas de cambios, migraciones y criterios de rollback.'],
    ['El núcleo no depende de integraciones', 'Las integraciones externas se añaden como adaptadores. Si Google Calendar, Telegram, Graphify o un proveedor LLM falla, la memoria y los recordatorios internos deben continuar funcionando.'],
    ['Primero internas, después externas', 'La creación de una memoria o recordatorio propio es menos riesgosa que enviar un correo o modificar un calendario externo. La autonomía se incrementa por niveles.'],
    ['Comunidad por módulos', 'El proyecto debe permitir contribuciones independientes en frontend, UI pixel art, skills, integraciones, documentación, localización, seguridad y modelos/adapters.'],
]
story.append(make_table(principios_rm, col_widths=[42*mm, 128*mm]))

# 3. Estado actual
add_heading('3. Estado actual', style_h1, level=0, story=story)
add_heading('3.1. Completado en documentación', style_h2, level=1, story=story)
story.extend(bullet_list([
    'PRD, TRD, Esquema Backend, Plan de Implementación.',
    'Diseño UI/UX, App Flow, Modelo de Datos.',
    'Seguridad y Privacidad, MCP y Skills.',
    'Roadmap, Documento Maestro.',
]))
add_heading('3.2. Prototipos visuales existentes', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Golem informático principal y variantes.',
    'Hoja conceptual de estados de animación.',
    'Referencias de HUD cyberpunk.',
    'Dirección visual pixel art definida.',
]))
add_heading('3.3. Pendiente de implementación', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Monorepo funcional.',
    'Demo navegable.',
    'Núcleo local.',
    'Backend real.',
    'Scheduler y workers.',
    'APK y desktop.',
    'MCP Gateway.',
    'Skills ejecutables.',
]))

# 4. Versionado
add_heading('4. Versionado', style_h1, level=0, story=story)
add_heading('4.1. Semantic Versioning', style_h2, level=1, story=story)
story.append(code_block(
    'MAJOR.MINOR.PATCH\n'
    '\n'
    'MAJOR: cambios incompatibles de API, exportación o configuración\n'
    'MINOR: nuevas funciones compatibles\n'
    'PATCH: correcciones y mejoras compatibles'
))
add_heading('4.2. Canales', style_h2, level=1, story=story)
story.append(code_block(
    'nightly  → builds automáticos para desarrollo\n'
    'alpha    → funciones incompletas para pruebas técnicas\n'
    'beta     → flujo de usuario estable, posibles cambios menores\n'
    'stable   → release recomendada'
))
add_heading('4.3. Etiquetas de versión', style_h2, level=1, story=story)
story.append(code_block(
    'v0.1.0-demo\n'
    'v0.2.0-local\n'
    'v0.3.0-server\n'
    'v0.4.0-platforms\n'
    'v0.4.5-sync\n'
    'v0.5.0-memory\n'
    'v0.6.0-mcp\n'
    'v0.7.0-agents\n'
    'v0.8.0-integrations\n'
    'v0.9.0-stabilization\n'
    'v0.9.5-testing\n'
    'v1.0.0-stable'
))

# 5. Fases del roadmap (tabla resumen con colores por versión)
add_heading('5. Fases del roadmap', style_h1, level=0, story=story)
story.append(p('El roadmap se organiza en 11 fases secuenciales, cada una con objetivo, funciones y criterios de salida verificables:'))

fases_rm = [
    ['Versión', 'Nombre', 'Resultado principal'],
    ['0.1', 'Demo pública', 'GitHub Pages navegable con chat, panel y grafo mock'],
    ['0.2', 'Núcleo local', 'PWA + IndexedDB + memorias y recordatorios offline'],
    ['0.3', 'Servidor privado', 'Docker con API, PostgreSQL/SQLite, workers y scheduler'],
    ['0.4', 'Plataformas', 'APK (Capacitor), Desktop (Tauri), CLI con sync probada'],
    ['0.5', 'Memoria grafo', 'MemoryNode/Edge, procedencia, búsqueda híbrida, contradicciones'],
    ['0.6', 'MCP Gateway', 'Registro, scopes, policy engine, Graphify read-only'],
    ['0.7', 'Skills y agentes', '7 agentes iniciales, skills versionadas, autonomía limitada'],
    ['0.8', 'Integraciones', 'Calendario, Telegram, Gmail, Outlook, Discord, WhatsApp'],
    ['0.9', 'Estabilización', 'Seguridad, rendimiento, comunidad, plugin SDK'],
    ['1.0', 'Release estable', 'API versionada, backups probados, releases firmados, documentación'],
]
story.append(make_table(fases_rm, col_widths=[18*mm, 38*mm, 114*mm], version_col=0))

# 6. Detalle por fase
add_heading('6. Detalle por fase', style_h1, level=0, story=story)

add_heading('6.1. VNBOT 0.1 — Demo pública en GitHub Pages', style_h2, level=1, story=story)
story.append(p('Objetivo: presentar visualmente VNBOT sin requerir instalación, cuenta ni proveedor de IA.'))
story.append(p('Funciones:'))
story.extend(bullet_list([
    'Landing, golem principal, chat simulado.',
    'Crear recordatorio ficticio, vista Hoy ficticia.',
    'Grafo de ejemplo, selector de agentes, estados emocionales.',
    'Presentación de Docker, APK y desktop como próximos canales.',
    'Documentación enlazada.',
]))
story.append(callout(
    'Criterios de salida: carga desde GitHub Pages, funciona en móvil y desktop, accesos a '
    'documentación y repositorio, navegación principal se entiende en menos de un minuto, '
    'tests unitarios con 60% cobertura en core, OpenTelemetry tracing, axe-core sin violaciones AA críticas.',
    color=SEM_SUCCESS
))

add_heading('6.2. VNBOT 0.2 — Núcleo local', style_h2, level=1, story=story)
story.append(p('Objetivo: ofrecer una aplicación personal capaz de funcionar sin servidor remoto.'))
story.append(p('Funciones: PWA, IndexedDB, bóveda local, chat, heurística, memoria CRUD, grafo básico, recordatorios locales, notificación local, importación/exportación, configuración de zona horaria.'))
story.append(p('No incluir todavía: MCP remoto, envío de email, WhatsApp, agente autónomo, audio cloud obligatorio.'))
story.append(callout(
    'Criterios de salida: crear memoria sin conexión, crear recordatorio sin LLM, reiniciar y '
    'conservar datos, exportar e importar, olvidar memoria y limpiar índices locales.',
    color=SEM_SUCCESS
))

add_heading('6.3. VNBOT 0.3 — Servidor privado y Docker', style_h2, level=1, story=story)
story.append(p('Objetivo: permitir que una persona despliegue VNBOT en un servidor propio.'))
story.append(p('Componentes: FastAPI, SQLite para instalación sencilla, PostgreSQL para servidor, Redis, worker, scheduler, healthchecks, API /api/v1, autenticación, workspaces, backups.'))
story.append(p('Distribución:'))
story.append(code_block(
    'docker compose -f docker-compose.server.yml up -d\n'
    'vnbot doctor\n'
    'vnbot migrate'
))
story.append(callout(
    'Criterios de salida: reiniciar API sin perder datos, reiniciar worker sin perder jobs, '
    'ejecutar backup y restore, ver healthchecks, separar usuarios y workspaces, entregar '
    'notificaciones internas de forma idempotente.',
    color=SEM_SUCCESS
))

add_heading('6.4. VNBOT 0.4 — Plataformas', style_h2, level=1, story=story)
story.append(p('Objetivo: distribuir VNBOT como APK, desktop y CLI. Requiere sync strategy probada.'))
story.append(p('<b>APK:</b> Capacitor, permisos de micrófono, notificaciones locales, estado de red, filesystem seguro, APK firmado.'))
story.append(p('<b>Desktop:</b> Tauri, SQLite local, notificaciones nativas, auto-lock, instaladores para Windows/Linux/macOS.'))
story.append(p('<b>CLI:</b>'))
story.append(code_block(
    'vnbot init\n'
    'vnbot add "revisar presupuesto"\n'
    'vnbot search "Daniel"\n'
    'vnbot reminders list\n'
    'vnbot backup create\n'
    'vnbot doctor'
))

add_heading('6.5. VNBOT 0.5 — Memoria grafo', style_h2, level=1, story=story)
story.append(p('Objetivo: convertir la memoria básica en un sistema visible de nodos y relaciones.'))
story.append(p('Funciones: MemoryNode, MemoryEdge, procedencia, confianza, contradicciones, expiración, búsqueda textual y semántica, recorrido de subgrafos, inspector, vista lista, corrección y olvido, exportación del grafo.'))
story.append(p('Límites iniciales: profundidad 2-3, Top-K configurable, máximo visible por consulta, sin cargar toda la bóveda en el navegador.'))

add_heading('6.6. VNBOT 0.6 — MCP Gateway', style_h2, level=1, story=story)
story.append(p('Objetivo: conectar herramientas externas de manera segura y visible.'))
story.append(p('Funciones: registro de servidores, stdio, Streamable HTTP, handshake, descubrimiento, scopes, policy engine, confirmaciones, healthchecks, auditoría, revocación.'))
story.append(p('Primera integración: Graphify en modo read-only.'))
story.append(p('Segunda integración: Calendario con lectura y creación de eventos confirmada.'))
story.append(callout(
    'No incluir inicialmente: escritura arbitraria de filesystem, envío automático de emails, '
    'acciones financieras, navegación sin sandbox.',
    color=SEM_WARNING
))

add_heading('6.7. VNBOT 0.7 — Skills y agentes', style_h2, level=1, story=story)
story.append(p('Objetivo: permitir que el usuario cree asistentes especializados.'))
story.append(p('Agentes iniciales (7): VNBOT Core, Archivista, Beacon, Navigator, Forge, Sentinel, Scout.'))
story.append(p('Skills iniciales (11):'))
story.append(code_block(
    'memory.save · memory.search · memory.correct · memory.forget\n'
    'reminder.create · reminder.snooze · reminder.complete\n'
    'list.manage · briefing.daily · graph.explore · mcp.connect'
))

add_heading('6.8. VNBOT 0.8 — Integraciones oficiales', style_h2, level=1, story=story)
story.append(p('Orden recomendado:'))
story.extend(numbered_list([
    'Calendario interno.',
    'Google Calendar.',
    'Telegram Bot API.',
    'Gmail lectura/borradores.',
    'Outlook.',
    'Discord bot oficial.',
    'WhatsApp Business Cloud API.',
]))

add_heading('6.9. VNBOT 0.9 — Estabilización', style_h2, level=1, story=story)
story.append(p('<b>Seguridad:</b> Threat model revisado, pentest básico, SAST/DAST, escaneo de secretos, dependencias auditadas, revisión MCP, revisión de backups, responsible disclosure.'))
story.append(p('<b>Rendimiento:</b> Pruebas con 10.000 memorias, 1.000 recordatorios, workers, sincronización, grafo, Android gama baja, desktop.'))
story.append(p('<b>Comunidad:</b> Plugin SDK inicial, documentación de contribución, issue templates, código de conducta, guías de assets, guía de localización.'))

add_heading('6.10. VNBOT 1.0 — Release estable', style_h2, level=1, story=story)
story.append(p('Requisitos:'))
story.extend(bullet_list([
    'API versionada y migraciones documentadas.',
    'Backups/restores probados.',
    'Release web, APK, desktop, Docker y CLI estables.',
    'Seguridad revisada y UI accesible.',
    'Exportación portable.',
    'Sistema de skills documentado.',
    'MCP con scopes y auditoría.',
    'Guía de administración y guía de privacidad.',
]))
story.append(callout(
    'VNBOT 1.0 no significa autonomía ilimitada ni todas las integraciones posibles. Significa '
    'que el núcleo es confiable, documentado y estable para ampliarse.',
    color=ACCENT
))

# 7. Roadmap funcional por áreas
add_heading('7. Roadmap funcional por áreas', style_h1, level=0, story=story)
story.append(p('Cada área evoluciona en paralelo pero con dependencias claras:'))

add_heading('7.1. Memoria', style_h2, level=1, story=story)
story.append(code_block(
    'MVP: CRUD y búsqueda\n'
    '0.5: grafo y procedencia\n'
    '0.7: scopes por agente\n'
    '1.0: consolidación, conflictos y exportación madura'
))

add_heading('7.2. Recordatorios', style_h2, level=1, story=story)
story.append(code_block(
    'MVP: puntual/recurrente\n'
    '0.3: workers y scheduler distribuido\n'
    '0.4: APK/desktop\n'
    '0.8: calendario y canales externos\n'
    '1.0: métricas de entrega y resiliencia'
))

add_heading('7.3. IA', style_h2, level=1, story=story)
story.append(code_block(
    'MVP: heurística\n'
    '0.3: proveedor local/externo\n'
    '0.4: router y structured output\n'
    '0.7: agentes\n'
    '1.0: evaluación y optimización de coste'
))

add_heading('7.4. Visual', style_h2, level=1, story=story)
story.append(code_block(
    '0.1: landing y mascotas\n'
    '0.2: panel y chat\n'
    '0.5: grafo\n'
    '0.7: mascotas por agente\n'
    '1.0: packs y sistema de assets estable'
))

add_heading('7.5. MCP', style_h2, level=1, story=story)
story.append(code_block(
    '0.6: gateway y tools internas\n'
    '0.6: Graphify read-only\n'
    '0.8: integraciones oficiales\n'
    '1.0: SDK y plugins'
))

# 8. Matriz de prioridad
add_heading('8. Matriz de prioridad', style_h1, level=0, story=story)
story.append(p('Cada funcionalidad se evalúa por valor, riesgo, dependencia y prioridad resultante:'))
matriz_data = [
    ['Funcionalidad', 'Valor', 'Riesgo', 'Prioridad'],
    ['Fallback heurístico', 'Alto', 'Bajo', 'P0'],
    ['Testing unitario', 'Alto', 'Bajo', 'P0'],
    ['Observabilidad (tracing)', 'Alto', 'Bajo', 'P0'],
    ['Recordatorio puntual', 'Alto', 'Bajo', 'P0'],
    ['Recurrencia', 'Alto', 'Medio', 'P0'],
    ['Memoria CRUD', 'Alto', 'Medio', 'P0'],
    ['Estrategia de sync', 'Alto', 'Alto', 'P1'],
    ['Accesibilidad WCAG AA', 'Alto', 'Medio', 'P1'],
    ['Grafo visual', 'Medio', 'Bajo', 'P1'],
    ['LLM Router', 'Alto', 'Medio', 'P1'],
    ['Audio local', 'Alto', 'Medio', 'P1'],
    ['APK', 'Alto', 'Medio', 'P1'],
    ['Desktop', 'Medio', 'Medio', 'P1'],
    ['MCP interno', 'Alto', 'Alto', 'P2'],
    ['Graphify', 'Medio', 'Alto', 'P2'],
    ['Email send', 'Medio', 'Alto', 'P3'],
    ['WhatsApp', 'Medio', 'Alto', 'P3'],
    ['Marketplace skills', 'Medio', 'Alto', 'P4'],
    ['Multiagente autónomo', 'Alto', 'Muy alto', 'P4'],
]
story.append(make_table(matriz_data, col_widths=[60*mm, 25*mm, 25*mm, 60*mm]))

# 9. Métricas de release
add_heading('9. Métricas de release', style_h1, level=0, story=story)
add_heading('9.1. Producto', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Tiempo hasta primer recordatorio.',
    'Porcentaje de onboarding completado.',
    'Tasa de confirmación correcta.',
    'Memorias recuperadas correctamente.',
    'Recordatorios completados.',
]))

add_heading('9.2. Backend', style_h2, level=1, story=story)
story.extend(bullet_list([
    'P95 de API.',
    'Jobs fallidos y jobs reintentados.',
    'Duplicados.',
    'Disponibilidad del scheduler.',
    'Cache hit rate.',
]))

add_heading('9.3. Seguridad', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Vulnerabilidades abiertas.',
    'Secret scans fallidos.',
    'Integraciones con scopes excesivos.',
    'Incidentes.',
    'Tiempo de respuesta a reportes.',
]))

add_heading('9.4. Comunidad', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Contribuidores.',
    'PRs.',
    'Issues.',
    'Plugins revisados.',
    'Descargas.',
    'Instalaciones Docker.',
]))
story.append(callout(
    'No se deben recopilar contenidos privados para calcular estas métricas. La telemetría '
    'es opt-in y agregada.',
    color=SEM_WARNING
))

# 10. Dependencias críticas
add_heading('10. Dependencias críticas', style_h1, level=0, story=story)
story.append(p('Las fases siguen una cadena de dependencias estricta. No se debe implementar un agente avanzado sobre un sistema de jobs todavía no confiable.'))
story.append(code_block(
    'Demo\n'
    '  ↓\n'
    'Frontend base\n'
    '  ↓\n'
    'Modelo de dominio\n'
    '  ↓\n'
    'Storage\n'
    '  ↓\n'
    'Recordatorios\n'
    '  ↓\n'
    'Worker/scheduler\n'
    '  ↓\n'
    'LLM/audio\n'
    '  ↓\n'
    'Grafo\n'
    '  ↓\n'
    'MCP\n'
    '  ↓\n'
    'Agentes\n'
    '  ↓\n'
    'Integraciones'
))

# 11. Release checklist
add_heading('11. Release checklist', style_h1, level=0, story=story)
story.append(p('Cada release debe verificar checklist completo en 5 áreas:'))

add_heading('11.1. Producto', style_h3, level=2, story=story)
story.extend(checklist([
    'Objetivo de release documentado.',
    'Funciones fuera de alcance listadas.',
    'Criterios de aceptación verificados.',
]))

add_heading('11.2. Código', style_h3, level=2, story=story)
story.extend(checklist([
    'Tests, lint, typecheck.',
    'Build, migraciones.',
]))

add_heading('11.3. Seguridad', style_h3, level=2, story=story)
story.extend(checklist([
    'Secret scan, dependencias.',
    'SAST, permisos, logs.',
]))

add_heading('11.4. Distribución', style_h3, level=2, story=story)
story.extend(checklist([
    'Artefactos, checksums, SBOM.',
    'Notas, compatibilidad.',
]))

add_heading('11.5. Documentación y visual', style_h3, level=2, story=story)
story.extend(checklist([
    'README, guía de instalación, variables de entorno.',
    'Guía de upgrade y rollback.',
    'Capturas, assets licenciados, reduced motion, responsive, accesibilidad.',
]))

# 12. Riesgos del roadmap
add_heading('12. Riesgos del roadmap', style_h1, level=0, story=story)
riesgos_rm = [
    ['Riesgo', 'Consecuencia', 'Respuesta'],
    ['Demasiadas integraciones', 'Mantenimiento inabarcable', 'Plugins/adapters'],
    ['Confundir demo con producto', 'Expectativas incorrectas', 'Etiquetas claras'],
    ['MCP sin controles', 'Exposición de datos', 'Gateway + policy'],
    ['Pixel art pesado', 'Mala experiencia móvil', 'Sprite sheets/lazy load'],
    ['LLM costoso', 'Sostenibilidad baja', 'Local/fallback/router'],
    ['Scheduler inestable', 'Recordatorios duplicados', 'Locks/idempotencia'],
    ['Licencias dudosas', 'Riesgo legal', 'Inventario/auditoría'],
    ['Scope creep', 'Release interminable', 'P0/P1 congelado'],
    ['Poca documentación', 'Comunidad bloqueada', 'Docs por módulo'],
    ['Sync sin diseñar', 'Pérdida de datos multi-dispositivo', 'Doc 11 antes de 0.3'],
    ['Testing insuficiente', 'Regresiones silenciosas', 'Cobertura mínima por módulo'],
    ['Accesibilidad postergada', 'Exclusión de usuarios', 'WCAG AA desde 0.1'],
    ['Sin gobernanza clara', 'Bloqueo de decisiones', 'Doc 13 en fase 0'],
]
story.append(make_table(riesgos_rm, col_widths=[45*mm, 55*mm, 70*mm]))

# 13. Preocupaciones transversales
add_heading('13. Preocupaciones transversales', style_h1, level=0, story=story)
story.append(p('Las siguientes áreas no son fases sino requisitos que aplican a todo el desarrollo:'))

add_heading('13.1. Testing', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Unit tests: mínimos por módulo.',
    'Integration tests: flujos críticos (chat → memoria, recordatorio → notificación).',
    'E2E tests: recorrido principal por plataforma.',
    'Contract tests: MCP tools y API endpoints.',
]))

add_heading('13.2. Observabilidad', style_h2, level=1, story=story)
story.extend(bullet_list([
    'OpenTelemetry para tracing distribuido.',
    'Logs estructurados (JSON).',
    'Métricas por módulo (latencia P95, error rate, throughput).',
    'Dashboards por release.',
]))

add_heading('13.3. Accesibilidad', style_h2, level=1, story=story)
story.extend(bullet_list([
    'WCAG 2.2 AA obligatorio.',
    'axe-core en CI.',
    'Auditoría manual por release.',
    'Testing con screen reader antes de v1.0.',
]))

# 14. Roadmap comunitario
add_heading('14. Roadmap comunitario', style_h1, level=0, story=story)
add_heading('14.1. Contribuciones tempranas', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Correcciones de documentación.',
    'Traducciones.',
    'Tests.',
    'Componentes UI.',
    'Fixtures.',
    'Accesibilidad.',
    'Themes.',
    'Sprites.',
]))

add_heading('14.2. Contribuciones intermedias', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Adapters de storage.',
    'Proveedores LLM.',
    'Integraciones oficiales.',
    'Skills.',
    'Notificaciones.',
    'Plugins MCP.',
]))

add_heading('14.3. Contribuciones avanzadas', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Sincronización.',
    'Graph RAG.',
    'Workers distribuidos.',
    'Android nativo.',
    'Observabilidad.',
    'Seguridad.',
]))

# 15. Conclusión Roadmap
add_heading('15. Conclusión', style_h1, level=0, story=story)
story.append(p('VNBOT crecerá en capas. La primera versión no intentará resolver todas las tareas del usuario, sino demostrar una memoria personal y un sistema de recordatorios fiables, privados y extensibles.'))
story.append(p('La evolución recomendada es:'))
story.append(code_block(
    '0.1 Demo\n'
    '0.2 Local\n'
    '0.3 Server\n'
    '0.4 Plataformas\n'
    '0.5 Memoria\n'
    '0.6 MCP\n'
    '0.7 Agentes\n'
    '0.8 Integraciones\n'
    '0.9 Estabilización\n'
    '1.0 Release estable'
))
story.append(callout(
    'No se añade autonomía a una base que todavía no puede explicar, auditar y recuperar sus propias acciones.',
    color=ACCENT
))

# Page break before next document
story.append(PageBreak())

# ============================================================
# DOCUMENTO 11 — ESTRATEGIA DE SINCRONIZACIÓN
# ============================================================
story.append(doc_divider('11', 'ESTRATEGIA DE SINCRONIZACIÓN',
    'Sincronización multi-dispositivo offline-first: version vectors, conflictos y casos especiales.',
    ACCENT_AMBER))
story.append(Spacer(1, 10))

# 1. Propósito
add_heading('1. Propósito', style_h1, level=0, story=story)
story.append(p(
    'Este documento define cómo VNBOT sincroniza datos entre múltiples dispositivos del mismo '
    'usuario. La sincronización es un requisito previo a la distribución multiplataforma '
    '(APK, Desktop, CLI) y debe estar diseñada y probada antes de que un usuario pueda acceder '
    'a sus datos desde más de un cliente.'
))
story.append(callout(
    'Sin una estrategia de sync clara, VNBOT se arriesga a: pérdida de datos, duplicados '
    'silenciosos, conflictos irresolubles y una experiencia degradada en dispositivos móviles.',
    color=SEM_ERROR
))

# 2. Principios de sincronización
add_heading('2. Principios de sincronización', style_h1, level=0, story=story)
principios_sync = [
    ['Principio', 'Descripción'],
    ['Offline-first', 'VNBOT funciona completamente sin conexión. La sincronización es un mecanismo de transporte, no un requisito de operación. Si el servidor está caído, el usuario sigue creando memorias, recordatorios y listas localmente.'],
    ['Sin pérdida de datos', 'Nunca se descarta silenciosamente una operación local. Si hay un conflicto, se presenta al usuario. Si hay un error de sync, se reintenta. Si no se puede resolver, se marca para intervención manual.'],
    ['Conflicto visible, resolución por el usuario', 'Los conflictos no se resuelven con last-write-wins como política por defecto. El usuario siempre ve qué cambió en cada dispositivo y decide.'],
    ['Cifrado en tránsito y en reposo', 'Las operaciones de sync siempre viajan sobre TLS 1.2+. Los datos pendientes de sync en el dispositivo se almacenan cifrados.'],
    ['Idempotencia', 'Reenviar la misma operación no debe crear duplicados. Cada operación tiene un ID único por dispositivo.'],
]
story.append(make_table(principios_sync, col_widths=[42*mm, 128*mm]))

# 3. Modelo de datos de sincronización
add_heading('3. Modelo de datos de sincronización', style_h1, level=0, story=story)

add_heading('3.1. Version vectors', style_h2, level=1, story=story)
story.append(p(
    'Cada dispositivo mantiene un version vector: un mapa de {device_id → counter} que '
    'representa el estado de conocimiento del dispositivo. Los version vectors permiten '
    'detectar qué operaciones faltan sin necesidad de comparar timestamps.'
))
story.append(code_block(
    'Dispositivo A: {A: 5, B: 3}\n'
    'Dispositivo B: {A: 3, B: 7}\n'
    '\n'
    'Si A sync con B:\n'
    '- A aprende que B está en counter 7.\n'
    '- B aprende que A está en counter 5.\n'
    '- Se intercambian las operaciones pendientes.'
))

add_heading('3.2. Operación de sync', style_h2, level=1, story=story)
story.append(p('Cada cambio local genera una sync_operation:'))
story.append(code_block(
    '{\n'
    '  "op_id": "uuid-local-unique",\n'
    '  "device_id": "device-A",\n'
    '  "entity_type": "memory",\n'
    '  "entity_id": "uuid-memory",\n'
    '  "operation": "update",\n'
    '  "payload": {"title": "nuevo título", ...},\n'
    '  "base_version": 5,\n'
    '  "timestamp": "2026-07-17T10:00:00Z"\n'
    '}'
))

add_heading('3.3. Detección de conflictos', style_h2, level=1, story=story)
story.append(p('Un conflicto ocurre cuando:'))
story.extend(numbered_list([
    'El servidor recibe una operación con base_version que no coincide con la versión actual de la entidad.',
    'Dos dispositivos envían operaciones para la misma entidad basadas en versiones diferentes.',
]))
story.append(p('Ejemplo:'))
story.append(code_block(
    'Device A: edita memoria v3 → envía op(base: 3)\n'
    'Device B: edita memoria v3 → envía op(base: 3)\n'
    'Servidor: aplica A → versión es 4\n'
    'Servidor: recibe B(base: 3) ≠ versión actual(4) → CONFLICTO'
))

# 4. Estrategia de resolución
add_heading('4. Estrategia de resolución', style_h1, level=0, story=story)

add_heading('4.1. Reglas automáticas (sin intervención del usuario)', style_h2, level=1, story=story)
auto_data = [
    ['Tipo de conflicto', 'Resolución automática', 'Razón'],
    ['Mismo campo, mismo valor', 'Ignorar', 'No hay diferencia real'],
    ['Recordatorio completado en A, editado en B', 'Prevalece completado', 'La acción de completar es definitiva'],
    ['Soft delete en A, editado en B', 'Prevalece delete, ofrece recuperar', 'El usuario confirmó el borrado'],
    ['Campos diferentes en la misma entidad', 'Merge de campos no conflictivos', 'Cada campo es independiente'],
]
story.append(make_table(auto_data, col_widths=[55*mm, 55*mm, 60*mm]))

add_heading('4.2. Conflictos que requieren al usuario', style_h2, level=1, story=story)
manual_data = [
    ['Tipo de conflicto', 'Presentación al usuario'],
    ['Mismo campo con valores diferentes', 'Diff lado a lado con opción de elegir'],
    ['Borrado hard en un dispositivo, edición en otro', 'Confirmación: "¿Eliminar definitivamente?"'],
    ['Estructura cambiada (ej: lista reordenada)', 'Vista de ambas versiones + opción de fusión manual'],
]
story.append(make_table(manual_data, col_widths=[70*mm, 100*mm]))

add_heading('4.3. Flujo de resolución', style_h2, level=1, story=story)
story.append(code_block(
    '[Conflicto detectado]\n'
    '        ↓\n'
    '[Crear registro en sync_conflicts]\n'
    '        ↓\n'
    '[Notificar al usuario]\n'
    '        ↓\n'
    '[Mostrar diff: versión local vs versión remota]\n'
    '        ↓\n'
    '[Usuario elige: local | remota | fusionar | ambas]\n'
    '        ↓\n'
    '[Aplicar resolución]\n'
    '        ↓\n'
    '[Marcar conflicto como resuelto]\n'
    '        ↓\n'
    '[Re-sync]'
))

# 5. Protocolo de sincronización
add_heading('5. Protocolo de sincronización', style_h1, level=0, story=story)
story.append(p('El protocolo de sync usa 3 endpoints principales con intercambio de version vectors:'))

add_heading('5.1. Push — enviar cambios locales', style_h2, level=1, story=story)
story.append(code_block(
    'POST /api/v1/sync/push\n'
    'Authorization: Bearer <token>\n'
    'Content-Type: application/json\n'
    '\n'
    '{\n'
    '  "device_id": "device-A",\n'
    '  "operations": [\n'
    '    {"op_id": "...", "entity_type": "memory", "entity_id": "...", ...}\n'
    '  ],\n'
    '  "current_vector": {"A": 5, "server": 3}\n'
    '}\n'
    '\n'
    'Response:\n'
    '{\n'
    '  "accepted": 8,\n'
    '  "conflicts": [\n'
    '    {"entity_type": "memory", "entity_id": "...", "local": {...}, "remote": {...}}\n'
    '  ],\n'
    '  "server_vector": {"A": 5, "server": 8}\n'
    '}'
))

add_heading('5.2. Pull — recibir cambios del servidor', style_h2, level=1, story=story)
story.append(code_block(
    'POST /api/v1/sync/pull\n'
    'Authorization: Bearer <token>\n'
    'Content-Type: application/json\n'
    '\n'
    '{\n'
    '  "device_id": "device-A",\n'
    '  "known_vector": {"A": 5, "server": 3}\n'
    '}\n'
    '\n'
    'Response:\n'
    '{\n'
    '  "operations": [\n'
    '    {"op_id": "...", "entity_type": "reminder", "entity_id": "...", ...}\n'
    '  ],\n'
    '  "server_vector": {"A": 5, "server": 8},\n'
    '  "has_more": false\n'
    '}'
))

add_heading('5.3. Resolución de conflicto', style_h2, level=1, story=story)
story.append(code_block(
    'POST /api/v1/sync/conflicts/{id}/resolve\n'
    'Authorization: Bearer <token>\n'
    'Content-Type: application/json\n'
    '\n'
    '{\n'
    '  "resolution": "local" | "remote" | "merged" | "both",\n'
    '  "merged_payload": {...}  // solo si resolution = "merged"\n'
    '}'
))

# 6. Entidades afectadas
add_heading('6. Entidades afectadas por sync', style_h1, level=0, story=story)
story.append(p('No todas las entidades se sincronizan de la misma manera:'))
entidades_data = [
    ['Entidad', 'Sync', 'Notas'],
    ['memory_nodes', 'Sí', 'Con procedencia y confianza'],
    ['memory_edges', 'Sí', 'Las edges derivadas se recalculan si es necesario'],
    ['reminders', 'Sí', 'Los disparos locales se coordinan por timezone'],
    ['reminders_recurring', 'Sí', 'Las instancias futuras se recalculan'],
    ['lists', 'Sí', 'Con items'],
    ['agents', 'Sí', 'Configuración del agente'],
    ['skills', 'Sí', 'Versión de skill asignada'],
    ['audit_logs', 'Solo server → cliente', 'No se sync de cliente a server'],
    ['settings', 'Sí', 'Preferencias del usuario'],
    ['credentials', 'No', 'Se reconfiguran por dispositivo'],
]
story.append(make_table(entidades_data, col_widths=[40*mm, 40*mm, 90*mm]))
story.append(callout(
    'Las credenciales nunca se sincronizan. Se reconfiguran por dispositivo porque viven en '
    'el keychain/keystore del sistema, no en la base de datos.',
    color=SEM_WARNING
))

# 7. Casos especiales
add_heading('7. Casos especiales', style_h1, level=0, story=story)

add_heading('7.1. Recordatorios durante sync', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Si un recordatorio se crea en el dispositivo A y se sincroniza al servidor, el scheduler del servidor lo toma.',
    'Si el dispositivo A está offline, el scheduler local del dispositivo dispara el recordatorio.',
    'Si ambos schedulers disparan el mismo recordatorio, el servidor deduplica por reminder_id + scheduled_time.',
    'Las notificaciones se envían solo desde un punto (server wins si está disponible).',
]))

add_heading('7.2. Borrado de memorias con relaciones', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Al borrar un nodo, sus edges se invalidan.',
    'Al sincronizar el borrado, el servidor propaga la invalidación.',
    'Si otro dispositivo creó edges nuevas mientras tanto, se marcan como "huérfanas" y se notifican al usuario.',
]))

add_heading('7.3. Clock skew', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Todos los timestamps se normalizan a UTC en el servidor.',
    'Si el clock del dispositivo tiene drift > 5 minutos, se muestra una advertencia y se sugiere sincronizar la hora del dispositivo.',
    'Las operaciones se ordenan por version vector, no por timestamp.',
]))

# 8. Implementación por fase
add_heading('8. Implementación por fase', style_h1, level=0, story=story)
story.append(p('La sync se introduce progresivamente, no de golpe:'))
fases_sync = [
    ['Fase', 'Sync'],
    ['0.1 MVP', 'No. Solo local. Los campos version y updated_at se preparan.'],
    ['0.2 Servidor', 'Sync server ↔ browser (misma máquina o red local).'],
    ['0.3 Plataformas', 'Sync multi-dispositivo completo con conflict resolution.'],
]
story.append(make_table(fases_sync, col_widths=[35*mm, 135*mm]))
story.append(callout(
    'La sync multi-dispositivo completa solo se activa en 0.3, después de que la sync '
    'server ↔ browser haya sido probada en 0.2. No se salta fases.',
    color=ACCENT_AMBER
))

# 9. Riesgos de sync
add_heading('9. Riesgos de sincronización', style_h1, level=0, story=story)
riesgos_sync = [
    ['Riesgo', 'Impacto', 'Mitigación'],
    ['Conflictos frecuentes', 'Experiencia degradada', 'Minimizar con detección temprana y merge automático de campos'],
    ['Queue local crece sin límite', 'Storage agotado', 'Límite de 10.000 ops pendientes. Alerta al usuario.'],
    ['Sync parcial falla', 'Estado inconsistente', 'Transacciones por batch. Rollback automático.'],
    ['Device perdido con ops pendientes', 'Datos perdidos', 'Las ops se descargan al server en el próximo sync de cualquier dispositivo. Si solo había un dispositivo, el backup local las contiene.'],
    ['Performance con muchos dispositivos', 'Latencia alta', 'Sync es peer-to-server, no peer-to-peer. Un usuario típico tiene 2-3 dispositivos.'],
]
story.append(make_table(riesgos_sync, col_widths=[50*mm, 35*mm, 85*mm]))

# 10. Seguridad de la sincronización
add_heading('10. Seguridad de la sincronización', style_h1, level=0, story=story)
story.append(p('La sync introduce riesgos específicos que se manejan con controles adicionales:'))
story.extend(bullet_list([
    'La sync nunca envía contenido en texto claro sobre HTTP. Siempre TLS 1.2+.',
    'El version vector no contiene datos del usuario, solo metadatos operativos.',
    'Las operaciones pendientes se cifran en reposo (local encryption).',
    'Un dispositivo no autorizado no puede iniciar sync sin autenticación válida.',
    'La sync_operations queue se almacena cifrada en el dispositivo.',
    'Si el dispositivo se pierde o es robado, el cifrado local protege las ops pendientes.',
    'Las credenciales de autenticación se almacenan en keychain/keystore del sistema.',
]))

add_heading('10.1. Conflicto = visibilidad', style_h2, level=1, story=story)
story.append(callout(
    'Los conflictos de sync nunca se resuelven silenciosamente. Siempre se presentan al '
    'usuario con la información suficiente para decidir.',
    color=ACCENT_AMBER
))

add_heading('10.2. Reset de sync', style_h2, level=1, story=story)
story.append(p('La operación sync/full-reset requiere:'))
story.extend(bullet_list([
    'Autenticación completa.',
    'Confirmación doble con delay de 5 segundos.',
    'Auditoría inmediata.',
    'No se permite durante una sync activa.',
]))

# 11. Conclusión Sync
add_heading('11. Conclusión', style_h1, level=0, story=story)
story.append(p(
    'La sincronización multi-dispositivo es el prerrequisito técnico para que VNBOT se '
    'distribuya en APK, desktop y CLI. Sin una sync confiable, la experiencia multiplataforma '
    'se degrada y se arriesgan datos del usuario.'
))
story.append(p('La estrategia se resume en 5 principios:'))
story.append(code_block(
    'Offline-first\n'
    '+ sin pérdida de datos\n'
    '+ conflicto visible al usuario\n'
    '+ cifrado en tránsito y reposo\n'
    '+ idempotencia por operación'
))
story.append(callout(
    'La sync no es una feature, es una capa de transporte. El usuario debe poder trabajar sin '
    'ella y solo notarla cuando hay conflictos que requieren su decisión.',
    color=ACCENT_AMBER
))

# ===== Build PDF =====
output_body = '/home/z/my-project/scripts/vol2_body.pdf'
doc = TocDocTemplate(
    output_body,
    pagesize=A4,
    leftMargin=20*mm,
    rightMargin=20*mm,
    topMargin=22*mm,
    bottomMargin=22*mm,
    title='VNBOT — Volumen II: Roadmap y Sincronización',
    author='VNBOT Project',
    subject='Compilado v1.0.0-draft — Roadmap (10) + Estrategia Sync (11)',
    creator='Z.ai',
)
doc.multiBuild(story, onFirstPage=page_decoration, onLaterPages=page_decoration)
print(f'Body PDF generated: {output_body}')
print(f'Size: {os.path.getsize(output_body) / 1024:.1f} KB')
