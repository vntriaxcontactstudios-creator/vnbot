#!/usr/bin/env python3
"""
VNBOT Plan de Implementación — Body PDF generator (ReportLab)
Genera el cuerpo del Plan con TOC, 28 secciones, tablas de fases, milestones y backlog.
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

# Phase colors for the phases table
PHASE_COLORS = {
    0: colors.HexColor('#6B7280'),   # gray - prep
    1: colors.HexColor('#0E7490'),   # cyan - demo
    2: colors.HexColor('#047857'),   # green - local
    3: colors.HexColor('#4e769e'),   # blue - backend
    4: colors.HexColor('#7152cb'),   # purple - intelligence
    5: colors.HexColor('#B45309'),   # amber - platforms
    6: colors.HexColor('#0E7490'),   # cyan - graph
    7: colors.HexColor('#B91C1C'),   # red - mcp (security)
    8: colors.HexColor('#7152cb'),   # purple - agents
    9: colors.HexColor('#047857'),   # green - integrations
    10: colors.HexColor('#1F2937'),  # dark - stabilization
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

style_phase_num = ParagraphStyle('PhaseNum',
    fontName='Mono-Bold', fontSize=14, leading=18,
    textColor=colors.white, alignment=TA_CENTER)

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

def checklist(items):
    """Markdown-style checklist with [ ] bullets."""
    return [Paragraph(item, style_checklist, bulletText='[ ]') for item in items]

def make_table(data, col_widths=None, header=True, phase_col=None):
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
    # Phase column coloring
    if phase_col is not None:
        for i in range(1, len(data)):
            try:
                phase_num = int(str(data[i][phase_col]).strip())
                if phase_num in PHASE_COLORS:
                    style_cmds.append(('BACKGROUND', (phase_col, i), (phase_col, i), PHASE_COLORS[phase_num]))
                    style_cmds.append(('TEXTCOLOR', (phase_col, i), (phase_col, i), colors.white))
                    style_cmds.append(('FONTNAME', (phase_col, i), (phase_col, i), 'Mono-Bold'))
                    style_cmds.append(('FONTSIZE', (phase_col, i), (phase_col, i), 14))
                    style_cmds.append(('ALIGN', (phase_col, i), (phase_col, i), 'CENTER'))
                    style_cmds.append(('VALIGN', (phase_col, i), (phase_col, i), 'MIDDLE'))
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

# ===== Page decoration =====
def page_decoration(canv, doc):
    canv.saveState()
    canv.setFont('Mono', 8)
    canv.setFillColor(TEXT_MUTED)
    page_num = canv.getPageNumber()
    canv.drawString(20*mm, 12*mm, 'VNBOT // PLAN v1.0.0-draft')
    canv.drawRightString(190*mm, 12*mm, f'{page_num}')
    canv.setStrokeColor(BORDER)
    canv.setLineWidth(0.4)
    canv.line(20*mm, 15*mm, 190*mm, 15*mm)
    if page_num > 1:
        canv.setFont('Mono', 7.5)
        canv.setFillColor(TEXT_MUTED)
        canv.drawString(20*mm, 285*mm, 'VNBOT — Plan de Implementación')
        canv.drawRightString(190*mm, 285*mm, '04-PLAN-IMPLEMENTACION-VNBOT.md')
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
    'Este documento transforma la visión y la arquitectura de VNBOT en una secuencia concreta '
    'de trabajo. Define qué construir primero, qué dependencias existen, cómo comprobar cada '
    'fase, cómo organizar el repositorio, cómo gestionar releases y qué funcionalidades deben '
    'posponerse para evitar que el proyecto se vuelva inmanejable.'
))
story.append(p('El plan está diseñado para un proyecto open source que pueda evolucionar desde una demo estática hasta una plataforma distribuida con:'))
story.extend(bullet_list([
    'Web/PWA, APK Android, Desktop, Docker y CLI.',
    'Memoria personal basada en grafo.',
    'Recordatorios confiables.',
    'Múltiples LLM con router y fallback.',
    'Skills y agentes personalizables.',
    'MCP para herramientas externas.',
    'Integraciones oficiales (calendario, Telegram, Gmail, etc.).',
]))
story.append(callout(
    'La estrategia es incremental: cada fase debe dejar un producto ejecutable, demostrable '
    'y verificable. No se debe esperar a tener todos los agentes, canales o integraciones '
    'para publicar una primera versión.',
    color=ACCENT
))

# ===== 2. Estrategia general =====
add_heading('2. Estrategia general', style_h1, level=0, story=story)

add_heading('2.1. Orden de prioridades', style_h2, level=1, story=story)
story.append(p('El orden de prioridades es deliberado y refleja las dependencias reales entre capacidades:'))
story.append(code_block(
    'Confiabilidad de recordatorios\n'
    '        ↓\n'
    'Memoria editable y recuperable\n'
    '        ↓\n'
    'Testing y observabilidad (cross-cutting desde el inicio)\n'
    '        ↓\n'
    'Modo local y exportación\n'
    '        ↓\n'
    'Estrategia de sincronización (antes de multiplataforma)\n'
    '        ↓\n'
    'Workers, scheduler y Docker\n'
    '        ↓\n'
    'Audio, APK y desktop\n'
    '        ↓\n'
    'MCP y Graphify\n'
    '        ↓\n'
    'Agentes y skills\n'
    '        ↓\n'
    'Integraciones externas\n'
    '        ↓\n'
    'Autonomía avanzada'
))

add_heading('2.2. Principio de núcleo pequeño', style_h2, level=1, story=story)
story.append(p('El núcleo inicial de VNBOT tendrá únicamente:'))
story.extend(bullet_list([
    'Cuenta/modo local.',
    'Chat.',
    'Memoria.',
    'Grafo limitado.',
    'Recordatorios.',
    'Notificaciones básicas.',
    'Exportación.',
    'Diagnóstico.',
]))
story.append(p('El resto debe implementarse como módulos, adaptadores o plugins para evitar acoplamientos prematuros.'))

add_heading('2.3. Principio de una capacidad por vez', style_h2, level=1, story=story)
story.append(p('No se implementará simultáneamente:'))
story.extend(bullet_list([
    'Audio remoto.',
    'WhatsApp.',
    'Gmail.',
    'MCP externo.',
    'Multiagente.',
    'OCR.',
    'Sincronización.',
]))
story.append(p('Cada capacidad debe probarse individualmente antes de convertirse en una dependencia de otra.'))

add_heading('2.4. Definición de versión funcional', style_h2, level=1, story=story)
story.append(p('Una versión puede publicarse cuando cumple 8 criterios:'))
story.extend(bullet_list([
    'Se instala.',
    'Tiene documentación.',
    'Tiene migración si modifica datos.',
    'Tiene manejo de errores.',
    'Tiene pruebas automatizadas.',
    'Puede recuperarse de un fallo.',
    'No expone secretos.',
    'Tiene notas de release.',
]))

# ===== 3. Fases generales =====
add_heading('3. Fases generales', style_h1, level=0, story=story)
story.append(p('El plan se organiza en 11 fases secuenciales, cada una con un resultado verificable:'))

fases_data = [
    ['Fase', 'Nombre', 'Resultado'],
    ['0', 'Preparación', 'Repositorio, decisiones, licencia y CI'],
    ['1', 'Demo visual', 'GitHub Pages con experiencia simulada'],
    ['2', 'Núcleo local', 'Memoria y recordatorios sin backend remoto'],
    ['3', 'Backend privado', 'API, workers, scheduler y Docker'],
    ['4', 'Inteligencia', 'LLM Router, búsqueda y audio'],
    ['5', 'Plataformas', 'APK, desktop y CLI'],
    ['6', 'Grafo', 'Memoria visual y relaciones avanzadas'],
    ['7', 'MCP', 'Gateway, permisos y Graphify'],
    ['8', 'Agentes', 'Skills, mascotas y autonomía limitada'],
    ['9', 'Integraciones', 'Calendario, Telegram, Gmail y otros'],
    ['10', 'Estabilización', 'Seguridad, rendimiento, releases y comunidad'],
]
story.append(make_table(fases_data, col_widths=[18*mm, 35*mm, 117*mm], phase_col=0))

# ===== 4. Fase 0 — Preparación =====
add_heading('4. Fase 0 — Preparación del proyecto', style_h1, level=0, story=story)
story.append(p('Crear una base de repositorio que permita trabajar de forma ordenada antes de desarrollar funciones complejas. Esta fase no produce código de producto, pero sin ella el resto se vuelve caótico.'))

add_heading('4.1. Entregables', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Repositorio GitHub vnbot.',
    'Licencia MIT.',
    'README principal.',
    'CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md, CHANGELOG.md.',
    'THIRD_PARTY_NOTICES.md.',
    'Estructura monorepo.',
    'CI inicial.',
    'ADRs técnicos.',
    'Inventario de assets.',
]))

add_heading('4.2. Tareas — Identidad', style_h2, level=1, story=story)
story.extend(checklist([
    'Definir nombre oficial: VNBOT.',
    'Definir logo y wordmark.',
    'Reservar nombres de paquetes.',
    'Crear guía de nomenclatura.',
    'Migrar referencias antiguas de MinBot-Task.',
]))

add_heading('4.3. Tareas — Licencia', style_h2, level=1, story=story)
story.extend(checklist([
    'Añadir MIT para código.',
    'Documentar licencia de documentación.',
    'Documentar licencia de assets.',
    'Auditar repositorios de terceros.',
    'Crear inventario de modelos y datasets visuales.',
]))

add_heading('4.4. Tareas — Arquitectura (ADRs)', style_h2, level=1, story=story)
story.extend(checklist([
    'Crear ADR sobre frontend desacoplado.',
    'Crear ADR sobre SQLite/PostgreSQL.',
    'Crear ADR sobre workers.',
    'Crear ADR sobre MCP.',
    'Crear ADR sobre cifrado y privacidad.',
    'Crear ADR sobre distribución.',
]))

add_heading('4.5. Tareas — Calidad', style_h2, level=1, story=story)
story.extend(checklist([
    'Configurar formatter, linter y type checking.',
    'Configurar tests y pre-commit.',
    'Configurar Gitleaks y Semgrep.',
    'Configurar Trivy para imágenes.',
]))

add_heading('4.6. Tareas — Documentación y observabilidad', style_h2, level=1, story=story)
story.extend(checklist([
    'Crear documento de estrategia de sincronización (11-ESTRATEGIA-SYNC-VNBOT.md).',
    'Crear documento de testing y observabilidad (12-TESTING-Y-OBSERVABILIDAD-VNBOT.md).',
    'Crear documento de gobernanza (13-GOBERNANZA-DE-PROYECTO-VNBOT.md).',
    'Configurar axe-core en CI para accesibilidad.',
    'Configurar OpenTelemetry SDK en el proyecto base.',
    'Definir cobertura mínima de tests por módulo.',
    'Crear benchmarks automatizados para el grafo.',
]))

add_heading('4.7. Criterio de salida', style_h2, level=1, story=story)
story.append(callout(
    'Un contribuidor nuevo puede clonar el repositorio, instalar dependencias, ejecutar '
    'una comprobación básica y comprender la arquitectura leyendo el README.',
    color=SEM_SUCCESS
))

# ===== 5. Fase 1 — Demo visual =====
add_heading('5. Fase 1 — Demo visual en GitHub Pages', style_h1, level=0, story=story)
story.append(p('Publicar una demostración navegable del concepto sin backend, secretos ni datos reales. Esta demo sirve como referencia visual y de marketing open source.'))

add_heading('5.1. Alcance', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Landing.',
    'Onboarding simulado.',
    'Panel Hoy.',
    'Chat mock.',
    'Grafo con fixtures.',
    'Selector de agentes.',
    'Mascota principal y estados visuales.',
    'Vista de instalación.',
    'Links a GitHub, Docker y Releases.',
]))

add_heading('5.2. Tareas', style_h2, level=1, story=story)
story.extend(checklist([
    'Crear app Vite/React.',
    'Configurar base path de GitHub Pages.',
    'Implementar routing estático.',
    'Crear fixtures anónimos.',
    'Crear chat simulado y tarjetas de acción.',
    'Crear grafo demo.',
    'Añadir mascot states.',
    'Añadir responsive, high contrast y reduced motion.',
    'Configurar GitHub Action de deploy.',
]))

add_heading('5.3. Reglas', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Ninguna API key.',
    'Ningún correo real.',
    'Ningún dato del usuario guardado en un servidor.',
    'Debe indicar qué partes son simuladas.',
    'Debe poder cargar sin backend.',
]))

add_heading('5.4. Criterio de salida', style_h2, level=1, story=story)
story.append(callout(
    'La persona que visita la página entiende qué es VNBOT, ve el flujo principal y puede '
    'navegar por una experiencia consistente sin instalar nada.',
    color=SEM_SUCCESS
))

# ===== 6. Fase 2 — Núcleo local =====
add_heading('6. Fase 2 — Núcleo local', style_h1, level=0, story=story)
story.append(p(
    'Construir una versión utilizable para una sola persona, sin depender de un backend '
    'remoto ni de un proveedor LLM. Esta fase prueba que el ciclo Capturar→Interpretar→'
    'Confirmar→Ejecutar→Auditar funciona de punta a punta.'
))

add_heading('6.1. Alcance funcional', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Bóveda local.',
    'IndexedDB en PWA.',
    'SQLite en desktop/local.',
    'Chat.',
    'Heurística.',
    'Memorias, nodos y aristas básicos.',
    'Recordatorios locales.',
    'Notificaciones disponibles en plataforma.',
    'Exportación/importación.',
]))

add_heading('6.2. Implementación de almacenamiento', style_h2, level=1, story=story)
story.append(p('<b>PWA (IndexedDB):</b>'))
story.extend(checklist([
    'Crear esquema IndexedDB.',
    'Añadir migraciones de cliente.',
    'Crear repositorios.',
    'Crear índices por fecha/tipo.',
    'Separar plaintext en memoria de UI.',
    'Añadir expiración de datos temporales.',
]))
story.append(p('<b>Local/desktop (SQLite):</b>'))
story.extend(checklist([
    'Crear SQLite adapter.',
    'Crear migraciones Alembic o equivalente.',
    'Configurar backup.',
    'Crear bloqueo de archivo.',
    'Crear comando vnbot doctor.',
]))

add_heading('6.3. Memoria básica', style_h2, level=1, story=story)
story.extend(checklist([
    'Crear MemoryNode y MemoryEdge.',
    'Añadir procedencia, confianza y sensibilidad.',
    'Implementar CRUD y búsqueda textual.',
    'Implementar olvidar y exportación.',
]))

add_heading('6.4. Heurística', style_h2, level=1, story=story)
story.append(p('Debe detectar al menos los siguientes patrones de intención:'))
story.extend(bullet_list([
    '"Recuérdame".',
    '"Avísame".',
    '"Tengo que".',
    '"Necesito".',
    '"Guarda que".',
    '"Olvida que".',
    '"Añade a la lista".',
    'Fechas relativas comunes.',
    'Horas básicas.',
]))
story.append(callout(
    'La heurística debe indicar baja confianza cuando no pueda resolver una instrucción '
    'con seguridad. No debe inventar interpretaciones.',
    color=SEM_WARNING
))

add_heading('6.5. Recordatorios locales', style_h2, level=1, story=story)
story.extend(checklist([
    'Crear entidad Reminder y Occurrence.',
    'Resolver timezones.',
    'Implementar recurrencia.',
    'Implementar posponer, completar y cancelación.',
    'Evitar duplicados.',
    'Crear historial local.',
]))

add_heading('6.6. Criterio de salida', style_h2, level=1, story=story)
story.append(callout(
    'El usuario puede crear una memoria y un recordatorio, cerrar la aplicación, abrirla de '
    'nuevo, recuperar los datos y exportarlos sin conexión.',
    color=SEM_SUCCESS
))

# ===== 7. Fase 3 — Backend privado =====
add_heading('7. Fase 3 — Backend privado', style_h1, level=0, story=story)
story.append(p(
    'Convertir el núcleo local en una plataforma servidor con API, autenticación, workers, '
    'scheduler y Docker. Esta fase permite multi-dispositivo y prepara la base para escalado '
    'horizontal posterior.'
))

add_heading('7.1. API', style_h2, level=1, story=story)
story.extend(checklist([
    'Crear FastAPI.',
    'Crear /api/v1.',
    'Crear schemas Pydantic.',
    'Crear manejo de errores.',
    'Crear request_id/trace_id.',
    'Crear OpenAPI.',
    'Crear autenticación.',
    'Crear autorización por workspace.',
]))

add_heading('7.2. Persistencia', style_h2, level=1, story=story)
story.extend(checklist([
    'Crear SQLAlchemy y Alembic.',
    'Validar SQLite y PostgreSQL.',
    'Crear índices y transacciones.',
    'Crear soft delete.',
    'Crear backups.',
]))

add_heading('7.3. Redis y jobs', style_h2, level=1, story=story)
story.extend(checklist([
    'Añadir Redis.',
    'Definir job schema.',
    'Crear worker y scheduler.',
    'Crear locks.',
    'Crear reintentos y dead-letter queue.',
    'Crear endpoint de estado de jobs.',
]))

add_heading('7.4. Docker', style_h2, level=1, story=story)
story.extend(checklist([
    'Dockerfile API, worker y scheduler.',
    'Compose local y compose server.',
    '.env.example.',
    'Healthchecks y volúmenes.',
    'Usuario no root.',
]))

add_heading('7.5. Notificaciones', style_h2, level=1, story=story)
story.extend(checklist([
    'Notificación web.',
    'Notificación desktop.',
    'Notificación local Android posteriormente.',
    'Estado de delivery.',
    'Reintentos.',
    'Preferencias de usuario.',
]))

add_heading('7.6. Criterio de salida', style_h2, level=1, story=story)
story.append(callout(
    'Una instalación Docker puede registrar un usuario, guardar memorias, crear recordatorios, '
    'procesar jobs, reiniciarse y conservar el estado.',
    color=SEM_SUCCESS
))

# ===== 8. Fase 4 — Inteligencia y audio =====
add_heading('8. Fase 4 — Inteligencia y audio', style_h1, level=0, story=story)
story.append(p(
    'Añadir IA configurable sin convertirla en una dependencia obligatoria ni permitir que '
    'actúe sin validación. El LLM es un intérprete, no un decisor.'
))

add_heading('8.1. LLM Router', style_h2, level=1, story=story)
story.extend(checklist([
    'Definir interfaz común.',
    'Implementar Ollama.',
    'Implementar OpenAI-compatible.',
    'Implementar proveedor adicional.',
    'Añadir structured outputs.',
    'Añadir fallback, timeouts y circuit breaker.',
    'Añadir presupuesto.',
    'Añadir conteo de tokens agregado.',
]))

add_heading('8.2. Clasificación', style_h2, level=1, story=story)
story.extend(checklist([
    'Intent classifier.',
    'Extracción de fecha y entidades.',
    'Selección de skill.',
    'Confidence score.',
    'Detección de ambigüedad.',
    'Validación Pydantic.',
]))

add_heading('8.3. Búsqueda semántica', style_h2, level=1, story=story)
story.extend(checklist([
    'Elegir embedding local inicial.',
    'Crear índice.',
    'Asociar vector a nodo.',
    'Crear búsqueda híbrida.',
    'Añadir filtros.',
    'Invalidar embeddings al editar/borrar.',
    'Añadir fuentes a respuesta.',
]))

add_heading('8.4. Audio', style_h2, level=1, story=story)
story.extend(checklist([
    'UI de grabación.',
    'Endpoint temporal.',
    'Validación de audio.',
    'Job de transcripción.',
    'Whisper local.',
    'Revisión de transcript.',
    'Retención configurable.',
    'Borrado seguro.',
]))

add_heading('8.5. OCR posterior', style_h2, level=1, story=story)
story.extend(checklist([
    'Subida de imagen.',
    'Job OCR.',
    'Preview de extracción.',
    'Corrección manual.',
    'Conversión a memoria o recordatorio.',
]))

add_heading('8.6. Criterio de salida', style_h2, level=1, story=story)
story.append(callout(
    'El sistema puede interpretar instrucciones con un modelo local o externo, mostrar una '
    'propuesta estructurada, pedir aclaraciones y ejecutar solo después de validarla.',
    color=SEM_SUCCESS
))

# ===== 9. Fase 5 — APK, desktop y CLI =====
add_heading('9. Fase 5 — APK, desktop y CLI', style_h1, level=0, story=story)

add_heading('9.1. APK', style_h2, level=1, story=story)
story.extend(checklist([
    'Integrar PWA con Capacitor.',
    'Permisos de micrófono.',
    'Notificaciones locales.',
    'Estado de red.',
    'Filesystem local.',
    'Manejo de suspensión.',
    'Generar APK debug y release.',
    'Firmar APK.',
    'Pruebas en dispositivos reales.',
]))

add_heading('9.2. Desktop', style_h2, level=1, story=story)
story.extend(checklist([
    'Crear shell Tauri.',
    'Integrar frontend.',
    'Configurar SQLite local.',
    'Notificaciones nativas.',
    'Acceso a archivos autorizado.',
    'Auto-lock.',
    'Build Windows, Linux y macOS.',
    'Actualización firmada posteriormente.',
]))

add_heading('9.3. CLI', style_h2, level=1, story=story)
story.extend(checklist([
    'init, doctor, health.',
    'add, search, reminders.',
    'backup, restore.',
    'mcp.',
    'Salida JSON para automatizaciones.',
    'No mostrar secretos en argumentos.',
]))

add_heading('9.4. Criterio de salida', style_h2, level=1, story=story)
story.append(callout(
    'El mismo usuario puede acceder a sus memorias y recordatorios desde web, APK o desktop, '
    'respetando el modelo de permisos y sincronización definido.',
    color=SEM_SUCCESS
))

# ===== 10. Fase 6 — Grafo de memoria =====
add_heading('10. Fase 6 — Grafo de memoria', style_h1, level=0, story=story)
story.append(p(
    'Convertir la memoria básica en una representación relacional visible y útil. El grafo '
    'permite descubrir conexiones que la búsqueda textual no encuentra.'
))

add_heading('10.1. Tareas', style_h2, level=1, story=story)
story.extend(checklist([
    'Definir catálogo de tipos de nodo.',
    'Definir catálogo de relaciones.',
    'Crear resolución de entidades.',
    'Detectar duplicados.',
    'Crear búsqueda por relaciones.',
    'Añadir profundidad configurable.',
    'Crear grafo limitado.',
    'Añadir inspector.',
    'Crear modo lista.',
    'Añadir export JSON.',
    'Añadir corrección de aristas.',
    'Añadir expiración temporal.',
    'Añadir contradicciones.',
]))

add_heading('10.2. Graphify', style_h2, level=1, story=story)
story.extend(checklist([
    'Crear adaptador MCP.',
    'Registrar servidor.',
    'Mostrar tools/resources.',
    'Permitir solo graph.read al principio.',
    'Crear referencias cruzadas.',
    'No mezclar automáticamente datos personales.',
    'Crear opción de desconexión.',
]))

add_heading('10.3. Criterio de salida', style_h2, level=1, story=story)
story.append(callout(
    'El usuario puede buscar una entidad, ver sus relaciones relevantes, abrir la memoria '
    'origen, corregir una relación y eliminarla sin afectar datos no relacionados.',
    color=SEM_SUCCESS
))

# ===== 11. Fase 7 — MCP Gateway =====
add_heading('11. Fase 7 — MCP Gateway', style_h1, level=0, story=story)
story.append(p(
    'Crear una capa segura para conectar herramientas externas y exponer herramientas '
    'internas. MCP es el sistema de plugins con permisos granulares.'
))

add_heading('11.1. MCP interno', style_h2, level=1, story=story)
story.extend(checklist([
    'memory_search, memory_create, memory_update, memory_forget.',
    'graph_expand.',
    'reminder_create, reminder_complete, reminder_snooze.',
    'list_manage.',
]))

add_heading('11.2. Gateway', style_h2, level=1, story=story)
story.extend(checklist([
    'Registro de servidor.',
    'Transporte stdio y Streamable HTTP.',
    'Handshake y descubrimiento.',
    'Scopes y policy engine.',
    'Timeouts y rate limit.',
    'Healthcheck.',
    'Auditoría.',
    'Revocación.',
]))

add_heading('11.3. Herramientas por riesgo', style_h2, level=1, story=story)
riesgo_data = [
    ['Nivel', 'Ejemplos'],
    ['Bajo', 'Lectura de memoria autorizada, consulta de estado, búsqueda de nodos.'],
    ['Medio', 'Crear memoria, crear recordatorio, crear evento.'],
    ['Alto', 'Borrador de email, lectura de filesystem, compartir contenido.'],
    ['Crítico', 'Enviar email, escribir archivos, eliminar datos masivamente, acciones financieras (siempre fuera del MVP).'],
]
story.append(make_table(riesgo_data, col_widths=[22*mm, 148*mm]))

add_heading('11.4. Criterio de salida', style_h2, level=1, story=story)
story.append(callout(
    'Un servidor MCP puede conectarse, mostrar sus capacidades, recibir solo los scopes '
    'elegidos y ejecutar una herramienta con confirmación y auditoría.',
    color=SEM_SUCCESS
))

# ===== 12. Fase 8 — Agentes y skills =====
add_heading('12. Fase 8 — Agentes y skills', style_h1, level=0, story=story)
story.append(p(
    'Permitir personalización avanzada sin convertir las instrucciones en código arbitrario. '
    'Los agentes son configuraciones, no scripts.'
))

add_heading('12.1. Tareas', style_h2, level=1, story=story)
story.extend(checklist([
    'Crear Agent entity y Skill manifest.',
    'Crear selector de modelo, memoria y herramientas.',
    'Crear niveles de autonomía.',
    'Crear presupuesto por agente.',
    'Crear modo simulación.',
    'Crear auditoría por agente.',
    'Vincular mascota a agente.',
    'Implementar skills base.',
]))

add_heading('12.2. Skills iniciales', style_h2, level=1, story=story)
story.append(code_block(
    'memory.save\n'
    'memory.search\n'
    'memory.correct\n'
    'memory.forget\n'
    'reminder.create\n'
    'reminder.snooze\n'
    'reminder.complete\n'
    'list.manage\n'
    'briefing.daily\n'
    'graph.explore\n'
    'mcp.connect'
))

add_heading('12.3. Criterio de salida', style_h2, level=1, story=story)
story.append(callout(
    'El usuario puede crear un agente, asignarle skills y herramientas, revisar permisos, '
    'ejecutar una prueba controlada y revocarlo.',
    color=SEM_SUCCESS
))

# ===== 13. Fase 9 — Integraciones =====
add_heading('13. Fase 9 — Integraciones oficiales', style_h1, level=0, story=story)

add_heading('13.1. Orden recomendado', style_h2, level=1, story=story)
story.extend(numbered_list([
    'Calendario interno.',
    'Google Calendar.',
    'Telegram Bot API.',
    'Gmail lectura/borradores.',
    'Outlook.',
    'WhatsApp Business Cloud API.',
    'Discord bot oficial.',
]))

add_heading('13.2. Reglas', style_h2, level=1, story=story)
story.append(p('Cada integración debe documentar:'))
story.extend(bullet_list([
    'API oficial.',
    'Scopes.',
    'Datos leídos.',
    'Datos escritos.',
    'Costes.',
    'Límites.',
    'ToS.',
    'Revocación.',
    'Healthcheck.',
    'Fallback.',
]))

add_heading('13.3. Criterio de salida', style_h2, level=1, story=story)
story.append(callout(
    'La integración puede activarse, probarse, revocarse y operar sin que un fallo externo '
    'rompa el núcleo de VNBOT.',
    color=SEM_SUCCESS
))

# ===== 14. Fase 10 — Estabilización =====
add_heading('14. Fase 10 — Estabilización y comunidad', style_h1, level=0, story=story)

add_heading('14.1. Seguridad', style_h2, level=1, story=story)
story.extend(checklist([
    'Threat model actualizado.',
    'Pentest básico.',
    'SAST y DAST.',
    'Secret scanning.',
    'Escaneo de imágenes.',
    'Revisión MCP, archivos y backups.',
]))

add_heading('14.2. Rendimiento', style_h2, level=1, story=story)
story.extend(checklist([
    'Pruebas de 10.000 memorias.',
    'Pruebas de 1.000 recordatorios.',
    'Pruebas de workers.',
    'Pruebas de reconexión.',
    'Pruebas de grafo.',
    'Pruebas en Android de gama baja.',
    'Pruebas de consumo desktop.',
]))

add_heading('14.3. Releases', style_h2, level=1, story=story)
story.extend(checklist([
    'Versionado semántico.',
    'Checksums.',
    'SBOM.',
    'Firma de artefactos.',
    'Release notes.',
    'Migraciones.',
    'Canal beta y canal stable.',
]))

add_heading('14.4. Comunidad', style_h2, level=1, story=story)
story.extend(checklist([
    'Guía de contribución.',
    'Issue templates y PR template.',
    'CODEOWNERS.',
    'Documentación de plugins.',
    'Roadmap público.',
    'Inventario de assets.',
    'Política de seguridad.',
]))

# ===== 15. Backlog priorizado =====
add_heading('15. Backlog priorizado', style_h1, level=0, story=story)
story.append(p('El backlog se organiza en 5 prioridades que mapean a las fases:'))

backlog_data = [
    ['Prioridad', 'Nombre', 'Items principales'],
    ['P0', 'Bloqueante', 'Repositorio y licencia, modelo de dominio, memoria CRUD, recordatorio puntual, recurrencia, zona horaria, scheduler, idempotencia, notificación local, exportación, heurística, healthchecks, CI.'],
    ['P1', 'MVP público', 'Grafo limitado, búsqueda híbrida, PostgreSQL, Redis, worker, Docker, LLM Router, PWA, demo GitHub Pages, logs y auditoría.'],
    ['P2', 'Beta multiplataforma', 'APK, desktop, CLI, audio, embeddings locales, mascotas por agente, MCP interno, Graphify read-only.'],
    ['P3', 'Plataforma extensible', 'MCP externo completo, skills, agentes personalizados, Google Calendar, Telegram, Gmail borradores, sincronización, workspaces compartidos.'],
    ['P4', 'Escala y comunidad', 'Marketplace de skills, plugin SDK, observabilidad avanzada, Kubernetes, multi-región, agentes coordinados.'],
]
story.append(make_table(backlog_data, col_widths=[18*mm, 38*mm, 114*mm]))

# ===== 16. Milestones =====
add_heading('16. Milestones', style_h1, level=0, story=story)
story.append(p('Cada fase tiene un milestone con salida verificable:'))

milestones_data = [
    ['Milestone', 'Nombre', 'Salida'],
    ['M0', 'Repositorio listo', 'Estructura, licencia, CI, documentación y ADRs.'],
    ['M1', 'Demo pública', 'GitHub Pages navegable con chat, panel y grafo mock.'],
    ['M2', 'Local usable', 'Memoria y recordatorios offline.'],
    ['M3', 'Servidor privado', 'Docker con API, database, worker y scheduler.'],
    ['M4', 'Inteligencia controlada', 'LLM Router, structured outputs y búsqueda semántica.'],
    ['M5', 'Multiplataforma', 'APK y desktop instalables.'],
    ['M6', 'Grafo real', 'Relaciones, procedencia, filtros y exportación.'],
    ['M7', 'MCP seguro', 'Gateway, scopes, Graphify opcional y auditoría.'],
    ['M8', 'Agentes', 'Skills, mascotas y autonomía limitata.'],
    ['M9', 'Integraciones', 'Calendario, Telegram y correo limitado.'],
    ['M10', 'Release estable', 'Seguridad, performance, backups, SBOM y documentación.'],
]
story.append(make_table(milestones_data, col_widths=[22*mm, 45*mm, 103*mm]))

# ===== 17. Plan de branches =====
add_heading('17. Plan de branches y trabajo GitHub', style_h1, level=0, story=story)

add_heading('17.1. Branches', style_h2, level=1, story=story)
story.append(code_block(
    'main       → estable\n'
    'next       → integración de próxima versión\n'
    'feature/*  → funcionalidad\n'
    'fix/*      → corrección\n'
    'security/* → corrección sensible\n'
    'release/*  → preparación de release'
))

add_heading('17.2. Pull request', style_h2, level=1, story=story)
story.append(p('Cada PR debe incluir:'))
story.extend(bullet_list([
    'Problema.',
    'Solución.',
    'Archivos afectados.',
    'Tests.',
    'Capturas si modifica UI.',
    'Migración si modifica datos.',
    'Cambios de seguridad.',
    'Impacto en compatibilidad.',
]))

add_heading('17.3. CI mínima', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Lint.',
    'Type check.',
    'Unit tests.',
    'Integration tests.',
    'Build web.',
    'Build API.',
    'SAST.',
    'Secret scan.',
    'Dependency audit.',
]))

# ===== 18. Gestión de assets visuales =====
add_heading('18. Gestión de assets visuales', style_h1, level=0, story=story)

add_heading('18.1. Repositorio', style_h2, level=1, story=story)
story.append(code_block(
    'assets/\n'
    '├── mascot/\n'
    '├── agents/\n'
    '├── sprites/\n'
    '├── hud/\n'
    '├── icons/\n'
    '├── palettes/\n'
    '├── source/\n'
    '└── licenses/'
))

add_heading('18.2. Pipeline', style_h2, level=1, story=story)
story.append(code_block(
    'Generación conceptual\n'
    '→ selección\n'
    '→ limpieza manual\n'
    '→ palette lock\n'
    '→ sprite sheet\n'
    '→ revisión UI\n'
    '→ optimización\n'
    '→ inventario\n'
    '→ release'
))

add_heading('18.3. Reglas', style_h2, level=1, story=story)
story.extend(bullet_list([
    'No incluir watermarks.',
    'No utilizar assets de stock sin licencia.',
    'Guardar origen y modelo utilizado.',
    'Registrar licencia.',
    'Probar en 16/32/64/128 px.',
    'Mantener escalado nearest-neighbor.',
]))

# ===== 19. Seguridad durante el desarrollo =====
add_heading('19. Seguridad durante el desarrollo', style_h1, level=0, story=story)
story.extend(bullet_list([
    'Nunca subir .env.',
    'Ejecutar Gitleaks en cada PR.',
    'No usar datos reales en fixtures.',
    'Usar cuentas sandbox para integraciones.',
    'Rotar tokens de desarrollo.',
    'No incluir audios reales en tests.',
    'Mockear proveedores LLM.',
    'Crear MCP malicioso de prueba.',
    'Verificar aislamiento entre workspaces.',
    'Revisar dependencias nuevas.',
]))

# ===== 20. Definición de hecho =====
add_heading('20. Definición de hecho', style_h1, level=0, story=story)
story.append(p('Una tarea no está terminada solo porque funciona localmente. Debe cumplir 12 criterios:'))
story.extend(numbered_list([
    'Código implementado.',
    'Tests.',
    'Manejo de error.',
    'Estados de loading/offline.',
    'Permisos.',
    'Auditoría.',
    'Documentación.',
    'Compatibilidad definida.',
    'Migración si aplica.',
    'Revisión de seguridad.',
    'Capturas o pruebas visuales si aplica.',
    'Criterio de rollback.',
]))

# ===== 21. Pruebas por fase =====
add_heading('21. Pruebas por fase', style_h1, level=0, story=story)
story.append(p('Las pruebas se organizan por área y cubren escenarios críticos de cada fase:'))

add_heading('21.1. Núcleo', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Fecha ambigua.',
    'Zona horaria.',
    'Recurrencia.',
    'Cierre inesperado.',
    'Borrado.',
    'Exportación.',
]))

add_heading('21.2. Backend', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Reinicio API.',
    'Reinicio worker.',
    'Duplicación de jobs.',
    'Redis caído.',
    'Base de datos lenta.',
    'Delivery fallido.',
]))

add_heading('21.3. IA', style_h2, level=1, story=story)
story.extend(bullet_list([
    'JSON inválido.',
    'Prompt injection.',
    'LLM caído.',
    'Rate limit.',
    'Fallback heurístico.',
    'Memoria no autorizada.',
]))

add_heading('21.4. MCP', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Tool timeout.',
    'Scope insuficiente.',
    'Servidor malicioso.',
    'Revocación.',
    'Respuesta demasiado grande.',
    'Replay.',
]))

add_heading('21.5. Plataformas', style_h2, level=1, story=story)
story.extend(bullet_list([
    'APK sin permiso.',
    'Desktop sin conexión.',
    'PWA offline.',
    'Escalado pixelado.',
    'Reduced motion.',
    'Diferentes tamaños de pantalla.',
]))

# ===== 22. Criterios de release =====
add_heading('22. Criterios de release', style_h1, level=0, story=story)

release_data = [
    ['Canal', 'Características'],
    ['Alpha', 'Puede romperse, datos de prueba, sin promesa de compatibilidad, logs ampliados.'],
    ['Beta', 'Flujo núcleo estable, migraciones, backups, instaladores, reporte de errores.'],
    ['Stable', 'Suite de pruebas, seguridad revisada, documentación, compatibilidad definida, restore probado, releases firmados o con checksums.'],
]
story.append(make_table(release_data, col_widths=[22*mm, 148*mm]))

# ===== 23. Gestión de riesgos =====
add_heading('23. Gestión de riesgos del plan', style_h1, level=0, story=story)
story.append(p('Cada riesgo tiene una señal temprana detectable y una acción correctiva concreta:'))

riesgos_data = [
    ['Riesgo', 'Señal temprana', 'Acción'],
    ['Scope excesivo', 'Muchas features P0', 'Congelar alcance'],
    ['Backend monolítico', 'UI llama directamente a SDKs', 'Mover a adaptadores'],
    ['Scheduler poco fiable', 'Duplicados', 'Idempotencia y locks'],
    ['Coste LLM', 'Muchas llamadas por chat', 'Router y presupuesto'],
    ['MCP inseguro', 'Tools sin scopes', 'Policy engine obligatorio'],
    ['UI pesada', 'FPS bajo en móvil', 'Sprite sheets y fallback'],
    ['Licencias inciertas', 'Assets sin origen', 'Retirar y auditar'],
    ['Comunidad bloqueada', 'PRs difíciles de probar', 'CI y docs'],
    ['Pérdida de datos', 'Backups nunca restaurados', 'Prueba periódica'],
]
story.append(make_table(riesgos_data, col_widths=[45*mm, 60*mm, 65*mm]))

# ===== 24. Primer sprint =====
add_heading('24. Primer sprint recomendado', style_h1, level=0, story=story)

add_heading('24.1. Objetivo', style_h2, level=1, story=story)
story.append(p('Crear la primera rebanada vertical completa que demuestre el ciclo central de VNBOT:'))
story.append(code_block(
    'Chat\n'
    '→ interpretar recordatorio\n'
    '→ confirmar\n'
    '→ guardar\n'
    '→ programar\n'
    '→ notificar\n'
    '→ completar\n'
    '→ auditar'
))

add_heading('24.2. Tareas', style_h2, level=1, story=story)
story.extend(checklist([
    'Crear repositorio base.',
    'Crear modelo Reminder.',
    'Crear parser heurístico.',
    'Crear endpoint de propuesta.',
    'Crear confirmación.',
    'Crear SQLite.',
    'Crear scheduler local.',
    'Crear notificación mock.',
    'Crear panel Hoy mínimo.',
    'Crear test E2E.',
    'Crear estado visual del golem.',
]))

add_heading('24.3. Resultado', style_h2, level=1, story=story)
story.append(callout(
    'No se busca todavía una aplicación completa. Se busca demostrar que el ciclo más '
    'importante funciona de punta a punta sin perder datos ni confundir al usuario.',
    color=ACCENT
))

# ===== 25. Criterios de aceptación del plan =====
add_heading('25. Criterios de aceptación del plan', style_h1, level=0, story=story)
story.append(p('El plan se considera suficientemente definido cuando:'))
story.extend(bullet_list([
    'Cada módulo tiene una fase.',
    'Cada fase tiene entregables.',
    'Cada entregable tiene criterio de salida.',
    'Las dependencias están identificadas.',
    'El MVP tiene un backlog P0/P1.',
    'La distribución está contemplada desde el inicio.',
    'La seguridad aparece en cada fase.',
    'La UI y el backend tienen estados compatibles.',
    'Las tareas asíncronas tienen reintentos.',
    'La comunidad puede contribuir sin conocer todo el sistema.',
]))

# ===== 26. Conclusión =====
add_heading('26. Conclusión', style_h1, level=0, story=story)
story.append(p(
    'VNBOT debe implementarse como una secuencia de productos cada vez más capaces, no como '
    'un único lanzamiento gigantesco. La primera versión debe probar la confiabilidad del '
    'núcleo: capturar, estructurar, recordar y notificar.'
))
story.append(p(
    'Después se añaden IA, audio, plataformas, grafo, MCP, agentes e integraciones, siempre '
    'con interfaces estables, jobs auditables y permisos visibles.'
))
story.append(p('La estrategia de implementación queda resumida así:'))
story.append(code_block(
    'Primero confiabilidad.\n'
    'Después memoria.\n'
    'Luego distribución.\n'
    'Después extensibilidad.\n'
    'Finalmente autonomía.'
))
story.append(callout(
    'La autonomía avanzada solo será valiosa si el usuario puede saber qué ocurrió, por qué '
    'ocurrió, qué datos se utilizaron y cómo detener o revertir la acción.',
    color=ACCENT
))

# ===== 27. MVP comprimido =====
add_heading('27. MVP comprimido: 0.1 unificado', style_h1, level=0, story=story)

add_heading('27.1. Razón', style_h2, level=1, story=story)
story.append(p(
    'Las fases originales 0.1 (demo), 0.2 (núcleo local) y 0.3 (servidor) pueden fusionarse '
    'en un bloque que entregue valor real más rápido. Esto reduce el time-to-value sin '
    'sacrificar calidad.'
))

add_heading('27.2. Alcance del 0.1 unificado', style_h2, level=1, story=story)
story.extend(checklist([
    'Monorepo con CI (lint, typecheck, tests, secret scan).',
    'Web/PWA con chat.',
    'Backend embebido o Docker con SQLite.',
    'Fallback heurístico (sin LLM) documentado y testeado.',
    'Al menos 1 proveedor LLM configurado.',
    'Memorias CRUD con búsqueda textual.',
    'Recordatorios puntuales y recurrentes con scheduler.',
    'Grafo básico (CRUD de nodos y edges).',
    'Exportación e importación cifrada.',
    'Panel de auditoría básico.',
    'OpenTelemetry tracing en endpoints principales.',
    'Tests unitarios con 60% cobertura en core.',
    'axe-core en CI sin violaciones AA críticas.',
    'Demo estática en GitHub Pages (paralelo, no bloqueante).',
]))

add_heading('27.3. Lo que NO incluye el 0.1', style_h2, level=1, story=story)
story.extend(bullet_list([
    'APK, Desktop nativo, CLI nativo.',
    'MCP externo.',
    'Búsqueda semántica (requiere embeddings).',
    'Múltiples usuarios/workspaces.',
    'Sincronización multi-dispositivo.',
    'Audio.',
    'Agentes personalizables.',
]))

add_heading('27.4. Criterio de salida del 0.1', style_h2, level=1, story=story)
story.append(callout(
    'Una persona puede: crear una memoria, crear un recordatorio, buscar, exportar e '
    'importar — sin servidor externo. Los tests pasan en CI. El dashboard de observabilidad '
    'muestra métricas básicas. La documentación está actualizada.',
    color=SEM_SUCCESS
))

# ===== 28. Documentos adicionales de soporte =====
add_heading('28. Documentos adicionales de soporte', style_h1, level=0, story=story)
story.append(p('Los siguientes documentos deben existir antes de la implementación activa:'))

docs_data = [
    ['Documento', 'Propósito', 'Necesario antes de'],
    ['11-ESTRATEGIA-SYNC-VNBOT.md', 'Diseño de sincronización multi-dispositivo', 'Fase 0.3 (plataformas)'],
    ['12-TESTING-Y-OBSERVABILIDAD-VNBOT.md', 'Estrategia de tests y OpenTelemetry', 'Fase 0.1 (inicio de código)'],
    ['13-GOBERNANZA-DE-PROYECTO-VNBOT.md', 'Modelo de gobernanza y contribución', 'Fase 0 (preparación repo)'],
]
story.append(make_table(docs_data, col_widths=[60*mm, 60*mm, 50*mm]))

# ===== Build PDF =====
output_body = '/home/z/my-project/scripts/plan_body.pdf'
doc = TocDocTemplate(
    output_body,
    pagesize=A4,
    leftMargin=20*mm,
    rightMargin=20*mm,
    topMargin=22*mm,
    bottomMargin=22*mm,
    title='VNBOT — Plan de Implementación',
    author='VNBOT Project',
    subject='Plan de Implementación v1.0.0-draft — Fases, milestones, backlog y criterios',
    creator='Z.ai',
)
doc.multiBuild(story, onFirstPage=page_decoration, onLaterPages=page_decoration)
print(f'Body PDF generated: {output_body}')
print(f'Size: {os.path.getsize(output_body) / 1024:.1f} KB')
