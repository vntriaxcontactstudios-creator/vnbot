#!/usr/bin/env python3
"""
VNBOT PRD — Body PDF generator (ReportLab)
Genera el cuerpo del documento PRD con TOC, todas las secciones, tablas y contenido rico.
"""
import sys, os, hashlib
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, Image, Flowable, HRFlowable, ListFlowable, ListItem
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfgen import canvas

# ===== Font registration =====
FONT_DIR = '/usr/share/fonts'
pdfmetrics.registerFont(TTFont('NotoSerifSC', f'{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Regular.ttf'))
pdfmetrics.registerFont(TTFont('NotoSerifSC-Bold', f'{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Bold.ttf'))
registerFontFamily('NotoSerifSC', normal='NotoSerifSC', bold='NotoSerifSC-Bold')

# Sans-serif heading font — use Sarasa (CJK-aware) for proper rendering
pdfmetrics.registerFont(TTFont('NotoSansSC', f'{FONT_DIR}/truetype/chinese/SarasaMonoSC-SemiBold.ttf'))
pdfmetrics.registerFont(TTFont('NotoSansSC-Bold', f'{FONT_DIR}/truetype/chinese/SarasaMonoSC-Bold.ttf'))
registerFontFamily('NotoSansSC', normal='NotoSansSC', bold='NotoSansSC-Bold')

# Mono font
pdfmetrics.registerFont(TTFont('Mono', f'{FONT_DIR}/truetype/dejavu/DejaVuSansMono.ttf'))
pdfmetrics.registerFont(TTFont('Mono-Bold', f'{FONT_DIR}/truetype/dejavu/DejaVuSansMono-Bold.ttf'))
registerFontFamily('Mono', normal='Mono', bold='Mono-Bold')

# ===== Palette (minimal mode, auto-generated) =====
PAGE_BG       = colors.HexColor('#FFFFFF')
SECTION_BG    = colors.HexColor('#eeedec')
CARD_BG       = colors.HexColor('#f7f6f4')
TABLE_STRIPE  = colors.HexColor('#efedea')
HEADER_FILL   = colors.HexColor('#1F2937')  # VNBOT dark navy
COVER_BLOCK   = colors.HexColor('#847852')
BORDER        = colors.HexColor('#d8d3c3')
ICON          = colors.HexColor('#8a7536')
ACCENT        = colors.HexColor('#0E7490')  # darker cyan for print
ACCENT_2      = colors.HexColor('#7152cb')
TEXT_PRIMARY  = colors.HexColor('#111827')
TEXT_MUTED    = colors.HexColor('#6B7280')
SEM_SUCCESS   = colors.HexColor('#047857')
SEM_WARNING   = colors.HexColor('#B45309')
SEM_ERROR     = colors.HexColor('#B91C1C')

TABLE_HEADER_COLOR = HEADER_FILL
TABLE_HEADER_TEXT  = colors.white
TABLE_ROW_EVEN     = colors.white
TABLE_ROW_ODD      = TABLE_STRIPE

# ===== Styles =====
styles = getSampleStyleSheet()

style_h1 = ParagraphStyle('H1', parent=styles['Heading1'],
    fontName='NotoSansSC-Bold', fontSize=22, leading=28,
    textColor=HEADER_FILL, spaceBefore=18, spaceAfter=14,
    keepWithNext=True, alignment=TA_LEFT)

style_h2 = ParagraphStyle('H2', parent=styles['Heading2'],
    fontName='NotoSansSC-Bold', fontSize=16, leading=22,
    textColor=ACCENT, spaceBefore=14, spaceAfter=10,
    keepWithNext=True, alignment=TA_LEFT)

style_h3 = ParagraphStyle('H3', parent=styles['Heading3'],
    fontName='NotoSansSC-Bold', fontSize=13, leading=18,
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
    spaceBefore=10, spaceAfter=10, borderColor=ACCENT,
    borderWidth=0, borderPadding=8, alignment=TA_LEFT,
    backColor=CARD_BG)

style_code = ParagraphStyle('Code', parent=styles['Code'],
    fontName='Mono', fontSize=9, leading=13,
    textColor=TEXT_PRIMARY, backColor=CARD_BG,
    leftIndent=12, rightIndent=12, spaceBefore=6, spaceAfter=6,
    borderColor=BORDER, borderWidth=0.5, borderPadding=8)

style_table_header = ParagraphStyle('TableHeader',
    fontName='NotoSansSC-Bold', fontSize=9, leading=12,
    textColor=colors.white, alignment=TA_LEFT)

style_table_cell = ParagraphStyle('TableCell',
    fontName='NotoSerifSC', fontSize=9, leading=12,
    textColor=TEXT_PRIMARY, alignment=TA_LEFT)

style_table_cell_mono = ParagraphStyle('TableCellMono',
    fontName='Mono', fontSize=8.5, leading=12,
    textColor=ACCENT, alignment=TA_LEFT)

style_meta = ParagraphStyle('Meta',
    fontName='Mono', fontSize=8.5, leading=12,
    textColor=TEXT_MUTED, alignment=TA_LEFT)

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
    """Build a list of bullet paragraphs. Returns list of Flowables."""
    s = style or style_bullet
    return [Paragraph(item, s, bulletText='•') for item in items]

def make_table(data, col_widths=None, header=True):
    """Build a styled table. data[0] = header row, rest = body."""
    if col_widths is None:
        col_widths = [None] * len(data[0])
    # Wrap cells in Paragraph for proper wrapping
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
                    # First column = mono ID
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
            ('BACKGROUND', (0,0), (-1,0), TABLE_HEADER_COLOR),
            ('TEXTCOLOR', (0,0), (-1,0), TABLE_HEADER_TEXT),
            ('FONTNAME', (0,0), (-1,0), 'NotoSansSC-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('TOPPADDING', (0,0), (-1,0), 7),
            ('BOTTOMPADDING', (0,0), (-1,0), 7),
        ])
        # Alternating rows
        for i in range(1, len(data)):
            if i % 2 == 0:
                style_cmds.append(('BACKGROUND', (0,i), (-1,i), TABLE_ROW_ODD))
    t.setStyle(TableStyle(style_cmds))
    return t

def callout(text, color=None):
    """A callout box with accent left border."""
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

def section_divider():
    return HRFlowable(width='100%', thickness=0.5, color=BORDER,
                      spaceBefore=12, spaceAfter=12)

# ===== Page decoration (header/footer) =====
def page_decoration(canv, doc):
    canv.saveState()
    # Footer
    canv.setFont('Mono', 8)
    canv.setFillColor(TEXT_MUTED)
    page_num = canv.getPageNumber()
    # Footer text
    canv.drawString(20*mm, 12*mm, 'VNBOT // PRD v1.0.0-draft')
    canv.drawRightString(190*mm, 12*mm, f'{page_num}')
    # Thin footer line
    canv.setStrokeColor(BORDER)
    canv.setLineWidth(0.4)
    canv.line(20*mm, 15*mm, 190*mm, 15*mm)
    # Header (skip on page 1 = TOC)
    if page_num > 1:
        canv.setFont('Mono', 7.5)
        canv.setFillColor(TEXT_MUTED)
        canv.drawString(20*mm, 285*mm, 'VNBOT — Product Requirements Document')
        canv.drawRightString(190*mm, 285*mm, '01-PRD-VNBOT.md')
        canv.line(20*mm, 283*mm, 190*mm, 283*mm)
    canv.restoreState()

# ===== Build story =====
story = []

# --- TOC Page ---
story.append(Paragraph('Tabla de Contenidos', style_toc_title))
story.append(HRFlowable(width='100%', thickness=1, color=ACCENT, spaceAfter=14))
toc = TableOfContents()
toc.levelStyles = [toc_level0, toc_level1]
story.append(toc)
story.append(PageBreak())

# ===== Section 1: Propósito del documento =====
add_heading('1. Propósito del documento', style_h1, level=0, story=story)
story.append(p(
    'Este documento define qué es VNBOT, para quién se construye, qué problemas resuelve, '
    'qué funcionalidades deben formar parte del producto, cuáles son sus límites y cómo se '
    'comprobará que cada versión cumple su propósito. Es la referencia canónica para evitar '
    'que el producto se convierta en una colección desordenada de funciones de IA.'
))
story.append(p(
    'El PRD no describe en detalle la implementación interna. Las decisiones de infraestructura, '
    'modelos, servicios, protocolos y despliegue se documentan principalmente en el TRD, el '
    'Esquema Backend y el Plan de Implementación. Este documento se centra en el "qué" y el '
    '"para quién", no en el "cómo".'
))
story.append(p('El producto puede crecer de manera amplia, pero cada capacidad debe estar subordinada a cuatro objetivos fundamentales:'))
story.extend(bullet_list([
    '<b>Capturar información</b> con el menor esfuerzo posible.',
    '<b>Convertirla</b> en memoria, tarea, evento o recordatorio útil.',
    '<b>Recuperarla</b> de forma confiable y contextual.',
    '<b>Mantener al usuario en control</b> de sus datos y de las acciones del asistente.',
]))

# ===== Section 2: Resumen ejecutivo =====
add_heading('2. Resumen ejecutivo', style_h1, level=0, story=story)
story.append(p(
    'VNBOT será un asistente personal open source, privado, autoalojable y extensible que '
    'funcionará como una capa de memoria y ejecución sobre las herramientas del usuario. El '
    'usuario podrá escribir, hablar, enviar una imagen o compartir un archivo. VNBOT '
    'interpretará la entrada y propondrá una estructura útil: memoria, recordatorio, tarea, '
    'lista, evento, relación entre entidades, borrador de acción o consulta sobre información previa.'
))
story.append(p(
    'La memoria personal se representará mediante un grafo limitado de nodos y relaciones. El '
    'usuario podrá inspeccionarlo, corregirlo, eliminarlo y exportarlo. Para ampliar la '
    'información fuera del núcleo, VNBOT podrá conectarse a herramientas externas mediante MCP, '
    'incluyendo calendarios, correo, archivos y repositorios de código como Graphify.'
))
story.append(p('La identidad visual será propia y reconocible, combinando pixel art de alta calidad con un golem informático como mascota principal. Cada agente tendrá su variante coherente de la familia de golems, con estados visuales sincronizados con el funcionamiento real del sistema. Los paneles HUD cyberpunk angulares y la interfaz legible优先izan la accesibilidad sin depender de glassmorphism o blur.'))
story.append(p('VNBOT se distribuirá mediante múltiples canales para alcanzar distintos perfiles de usuario:'))
story.extend(bullet_list([
    'Demo estática en GitHub Pages para evaluación sin instalación.',
    'Aplicación web/PWA para uso diario en navegador.',
    'APK Android para dispositivos móviles.',
    'Aplicación de escritorio para Windows, macOS y Linux.',
    'Imágenes Docker para servidores privados.',
    'CLI para usuarios avanzados y administradores.',
]))

# ===== Section 3: Visión del producto =====
add_heading('3. Visión del producto', style_h1, level=0, story=story)

add_heading('3.1. Visión a largo plazo', style_h2, level=1, story=story)
story.append(p(
    'VNBOT aspira a ser una plataforma personal de memoria y agentes donde cada usuario pueda '
    'decidir qué información se almacena, qué se olvida, qué modelo de IA se utiliza, qué '
    'agentes existen, qué herramientas puede usar cada agente, qué acciones necesitan '
    'confirmación, dónde viven sus datos y si el procesamiento se realiza localmente o mediante '
    'un proveedor externo.'
))
story.append(p(
    'La visión no es crear una caja negra que actúe de manera ilimitada sin supervisión. La '
    'visión es crear una plataforma abierta y modular que permita capacidades muy amplias con '
    'permisos visibles, revocables y auditables. La autonomía avanzada se implementará después '
    'de que la memoria, los recordatorios, los jobs y la auditoría sean confiables.'
))

add_heading('3.2. Declaración de valor', style_h2, level=1, story=story)
story.append(callout(
    'VNBOT ayuda al usuario a sacar información de su cabeza, convertirla en estructuras útiles '
    'y volver a encontrarla en el momento correcto, sin obligarlo a entregar el control total '
    'de sus datos a un servicio cerrado.',
    color=ACCENT
))

add_heading('3.3. Promesa principal del MVP', style_h2, level=1, story=story)
story.append(callout(
    'Escribe o dicta una instrucción en lenguaje natural; VNBOT la entiende, te muestra lo que '
    'va a hacer, la guarda correctamente y te la presenta cuando corresponda.',
    color=SEM_WARNING
))

# ===== Section 4: Problema =====
add_heading('4. Problema que se desea resolver', style_h1, level=0, story=story)

add_heading('4.1. Fragmentación de información', style_h2, level=1, story=story)
story.append(p(
    'Las personas guardan información en múltiples lugares: aplicaciones de notas, mensajería, '
    'correo electrónico, calendarios, capturas de pantalla, archivos locales, historial del '
    'navegador, documentos y memoria informal. El problema no es solamente que existan muchas '
    'aplicaciones. El problema es que cada aplicación conserva una parte aislada del contexto '
    'y el usuario debe recordar dónde guardó cada cosa.'
))
story.append(p(
    'VNBOT aborda esta fragmentación ofreciendo un único punto de captura que luego distribuye '
    'la información a las estructuras apropiadas (memoria, recordatorio, tarea, lista) según '
    'la intención del usuario. La información sigue viviendo en su formato natural, pero el '
    'punto de entrada y recuperación es único y consultable.'
))

add_heading('4.2. Recordatorios débiles', style_h2, level=1, story=story)
story.append(p(
    'Las aplicaciones tradicionales suelen requerir que el usuario complete formularios, elija '
    'una fecha, seleccione una repetición y defina una notificación. Esto funciona para tareas '
    'planificadas, pero falla cuando la idea aparece en medio de una conversación. Además, un '
    'recordatorio aislado no siempre contiene el contexto necesario: con quién está relacionado, '
    'por qué importa, qué ocurrió antes, qué debe suceder después y qué canal es adecuado.'
))

add_heading('4.3. Asistentes sin continuidad', style_h2, level=1, story=story)
story.append(p(
    'La mayoría de los chats de IA pueden responder bien en una sesión, pero olvidan con '
    'facilidad las preferencias del usuario, las relaciones entre personas, las decisiones '
    'anteriores, las reglas de trabajo, las tareas pendientes y las correcciones hechas '
    'anteriormente. VNBOT debe tratar la memoria como una entidad visible y administrable, no '
    'como contexto invisible acumulado sin controles.'
))

add_heading('4.4. Falta de control y privacidad', style_h2, level=1, story=story)
story.append(p(
    'Los usuarios pueden enviar información sensible a un asistente sin saber qué se almacena, '
    'qué proveedor lo procesa, cuánto tiempo se conserva, qué integraciones tienen acceso, qué '
    'datos se usan para generar embeddings y qué acciones puede ejecutar el sistema. VNBOT debe '
    'hacer visible esta información y ofrecer un modo local o autoalojable como alternativa '
    'real al cloud cerrado.'
))

add_heading('4.5. Automatizaciones frágiles', style_h2, level=1, story=story)
story.append(p(
    'Una automatización incorrecta puede crear una fecha equivocada, enviar un correo a la '
    'persona equivocada, exponer información privada, crear recordatorios duplicados o borrar '
    'y modificar datos sin intención. Por eso, VNBOT debe separar claramente las fases del '
    'ciclo de operación para que ninguna acción se ejecute sin validación y confirmación '
    'explícita cuando tiene consecuencias.'
))
story.append(callout(
    'Ciclo de operación: Interpretar → Proponer → Validar → Confirmar → Ejecutar → Auditar',
    color=ACCENT
))

# ===== Section 5: Objetivos =====
add_heading('5. Objetivos del producto', style_h1, level=0, story=story)

add_heading('5.1. Objetivos del MVP', style_h2, level=1, story=story)

objetivos = [
    ('O-01', 'Captura rápida', 'Permitir que un usuario registre una idea, tarea o recordatorio en lenguaje natural sin aprender comandos especiales.', 'Un usuario nuevo debe poder crear su primer recordatorio sin consultar documentación.'),
    ('O-02', 'Recordatorios confiables', 'Crear un sistema de recordatorios que sobreviva a cierres, reinicios, fallos temporales y reintentos del worker.', 'No deben producirse duplicados cuando un job sea reintentado.'),
    ('O-03', 'Memoria controlable', 'Permitir guardar, consultar, editar, corregir y olvidar memorias.', 'El usuario debe poder identificar por qué existe una memoria y eliminarla sin intervención administrativa.'),
    ('O-04', 'Grafo comprensible', 'Representar relaciones personales de forma visual y limitada, sin convertir el panel en un diagrama ilegible.', 'Una consulta debe mostrar únicamente el subgrafo relevante, con alternativa en forma de lista.'),
    ('O-05', 'Privacidad verificable', 'Ofrecer diferentes modos de procesamiento y explicar claramente qué datos salen del dispositivo.', 'Cada integración y proveedor debe indicar el tipo de datos que puede recibir.'),
    ('O-06', 'Independencia de proveedor', 'Permitir usar un LLM local, un proveedor externo o un endpoint compatible con OpenAI.', 'El núcleo debe funcionar con heurísticas básicas incluso sin LLM.'),
    ('O-07', 'Base extensible', 'Permitir que agentes, skills y conectores MCP se añadan sin modificar todo el núcleo.', 'Una integración nueva debe implementarse como adaptador o plugin sin reescribir memoria y recordatorios.'),
    ('O-08', 'Distribución multiplataforma', 'Preparar el producto para web, APK, desktop, Docker y CLI.', 'Las interfaces deben consumir contratos API comunes y no duplicar las reglas de negocio.'),
]

obj_data = [['ID', 'Objetivo', 'Descripción', 'Criterio de éxito']]
for oid, name, desc, crit in objetivos:
    obj_data.append([oid, name, desc, crit])
story.append(make_table(obj_data, col_widths=[18*mm, 32*mm, 65*mm, 55*mm]))
story.append(Spacer(1, 10))

add_heading('5.2. Objetivos posteriores al MVP', style_h2, level=1, story=story)
story.append(p('Una vez consolidado el MVP, VNBOT incorporará gradualmente las siguientes capacidades:'))
story.extend(bullet_list([
    'Procesamiento de voz local y remoto con transcripción editable.',
    'OCR e interpretación de imágenes para captura visual.',
    'Briefings diarios y semanales generados desde la memoria.',
    'Integración oficial con calendarios ICS/CalDAV.',
    'Lectura y borradores de correo (no envío automático en MVP).',
    'Telegram y WhatsApp Business API como canales de notificación.',
    'Agentes personalizados con mascota, skills y presupuesto propios.',
    'Skills comunitarias firmadas con sistema de revisión.',
    'Grafo temporal avanzado con línea de tiempo.',
    'Sincronización entre dispositivos con resolución de conflictos.',
    'Espacios familiares o de equipo con permisos granulares.',
]))

# ===== Section 6: No objetivos =====
add_heading('6. No objetivos del MVP', style_h1, level=0, story=story)
story.append(p(
    'Los siguientes elementos quedan fuera del primer lanzamiento aunque se contemplen en la '
    'visión futura. Cada exclusión es deliberada y responde a principios de seguridad, '
    'estabilidad o madurez del producto.'
))

no_objetivos = [
    ('6.1', 'Agente autónomo general', 'VNBOT no podrá navegar libremente por el sistema del usuario ni ejecutar cualquier acción disponible. La autonomía se añadirá gradualmente y estará limitada por herramientas, scopes, presupuesto y confirmaciones.'),
    ('6.2', 'Mensajería automática a terceros', 'El MVP no enviará mensajes a familiares, compañeros o clientes sin una configuración explícita y una política de consentimiento.'),
    ('6.3', 'Acceso completo al correo', 'La primera integración de correo debe comenzar con lectura limitada o creación de borradores. El envío automático no será parte del MVP.'),
    ('6.4', 'Operaciones financieras', 'No se permitirán pagos, transferencias, compras ni acciones bancarias. Esta restricción es permanente por seguridad.'),
    ('6.5', 'Vigilancia continua del micrófono', 'La captura de audio será explícita y visible. No habrá escucha permanente en segundo plano en la primera versión.'),
    ('6.6', 'Grafo ilimitado', 'El grafo visible tendrá límites de profundidad, cantidad de nodos y filtros. La escalabilidad de datos no implica renderizar todos los nodos simultáneamente.'),
    ('6.7', 'Marketplace abierto de skills', 'Primero se necesita un sistema seguro de manifest, permisos, versionado y revisión. El marketplace queda para una etapa posterior.'),
]

no_obj_data = [['#', 'No objetivo', 'Justificación']]
for num, name, desc in no_objetivos:
    no_obj_data.append([num, name, desc])
story.append(make_table(no_obj_data, col_widths=[12*mm, 50*mm, 108*mm]))

# ===== Section 7: Usuarios objetivo =====
add_heading('7. Usuarios objetivo', style_h1, level=0, story=story)
story.append(p('VNBOT se construye para siete perfiles principales. Cada perfil tiene necesidades distintas y el producto debe servirlos sin convertirse en una herramienta solo para técnicos ni solo para casuales.'))

usuarios = [
    ('7.1', 'Usuario personal con alta carga mental', 'Necesita recordar citas, pagos, compras, compromisos, ideas y tareas pequeñas. Valora una captura rápida y notificaciones confiables.'),
    ('7.2', 'Profesional o freelancer', 'Gestiona proyectos, clientes, entregas, reuniones y seguimientos. Necesita relacionar personas, tareas y fechas en un mismo espacio.'),
    ('7.3', 'Estudiante', 'Guarda apuntes, fechas de exámenes, temas de estudio, enlaces y recordatorios recurrentes. Beneficiado por la organización automática.'),
    ('7.4', 'Usuario técnico', 'Quiere integrar VNBOT con repositorios, terminal, servidores, modelos locales y MCP. Valora la CLI, los logs estructurados y la auditabilidad.'),
    ('7.5', 'Usuario orientado a privacidad', 'Prefiere ejecutar el sistema en su propio equipo o servidor, elegir el modelo y exportar todos sus datos. El modo local estricto es su flujo principal.'),
    ('7.6', 'Administrador autoalojado', 'Necesita Docker, healthchecks, backups, logs, migraciones y una instalación reproducible. Documentación clara de despliegue es esencial.'),
    ('7.7', 'Usuarios fuera del foco inicial', 'No se priorizan: grandes empresas con compliance corporativo, automatización bancaria, atención médica automatizada, supervisión de empleados, comunicación masiva y sistemas críticos de seguridad física.'),
]

usr_data = [['#', 'Perfil', 'Necesidades principales']]
for num, name, desc in usuarios:
    usr_data.append([num, name, desc])
story.append(make_table(usr_data, col_widths=[12*mm, 50*mm, 108*mm]))

# ===== Section 8: Casos de uso =====
add_heading('8. Casos de uso principales', style_h1, level=0, story=story)
story.append(p('Los siguientes 10 casos de uso definen los recorridos críticos que VNBOT debe soportar desde el MVP. Cada caso tiene una entrada típica y un resultado esperado que debe cumplirse para considerar la funcionalidad terminada.'))

casos = [
    ('CU-01', 'Crear un recordatorio', '"Recuérdame pagar la electricidad mañana a las 8 de la mañana."',
     'Detectar intención, resolver zona horaria, mostrar fecha completa, solicitar confirmación si falta información, crear recordatorio y ocurrencia, confirmar al usuario.'),
    ('CU-02', 'Recordatorio recurrente', '"Todos los lunes recuérdame revisar el presupuesto."',
     'Crear regla de recurrencia (no lista de recordatorios duplicados). La regla debe poder pausarse, modificarse y cancelarse.'),
    ('CU-03', 'Guardar una memoria', '"Guarda que Daniel prefiere que las reuniones sean por la tarde."',
     'Crear o actualizar nodos de persona y preferencia, relacionarlos con procedencia explícita y permitir editar el hecho.'),
    ('CU-04', 'Consultar contexto', '"¿Qué tenía pendiente con Daniel?"',
     'Buscar memorias, tareas y recordatorios relacionados, mostrar fuentes y distinguir hechos confirmados de inferencias.'),
    ('CU-05', 'Captura por audio', 'Nota de voz del usuario.',
     'Solicitar permisos, transcribir, mostrar texto editable y ejecutar el mismo flujo del chat. El sistema no debe actuar sobre una transcripción no revisada si la acción tiene riesgo medio o alto.'),
    ('CU-06', 'Explorar el grafo', 'El usuario abre Memoria/Grafo.',
     'Mostrar mapa limitado de nodos, filtros, búsqueda, detalle, procedencia y acción de olvidar/corregir.'),
    ('CU-07', 'Conectar Graphify', 'El usuario añade un servidor MCP de Graphify.',
     'Mostrar origen, transporte, herramientas, scopes, healthcheck, riesgos y confirmación antes de activar. Graphify no debe recibir datos personales sin permiso específico.'),
    ('CU-08', 'Crear un agente', 'El usuario configura un agente de estudio.',
     'Seleccionar mascota, instrucciones, modelo, skills, memoria permitida, herramientas y nivel de autonomía. El sistema debe mostrar un resumen de permisos antes de activar.'),
    ('CU-09', 'Modo offline', 'El usuario pierde conexión.',
     'Crear capturas y recordatorios locales, marcar sincronización pendiente y sincronizar posteriormente con idempotency keys.'),
    ('CU-10', 'Exportar y olvidar', 'El usuario solicita exportar y eliminar su cuenta.',
     'Generar backup cifrado, pedir confirmación fuerte, revocar integraciones, eliminar datos activos y presentar el resultado de la operación.'),
]

cu_data = [['ID', 'Caso de uso', 'Entrada típica', 'Resultado esperado']]
for cid, name, entrada, resultado in casos:
    cu_data.append([cid, name, entrada, resultado])
story.append(make_table(cu_data, col_widths=[16*mm, 38*mm, 50*mm, 66*mm]))

# ===== Section 9: Requisitos funcionales =====
add_heading('9. Requisitos funcionales', style_h1, level=0, story=story)
story.append(p('Los requisitos funcionales se organizan en siete categorías. La prioridad sigue el modelo MoSCoW: Must (imprescindible para MVP), Should (importante, puede esperar al MVP+1), Could (deseable si hay tiempo).'))

# 9.1 Cuenta
add_heading('9.1. Cuenta y espacios', style_h2, level=1, story=story)
fr_cuenta = [
    ['ID', 'Requisito', 'Prioridad'],
    ['FR-001', 'Permitir modo local sin cuenta remota', 'Must'],
    ['FR-002', 'Permitir cuenta en servidor privado', 'Must'],
    ['FR-003', 'Separar usuarios y workspaces', 'Must'],
    ['FR-004', 'Configurar zona horaria e idioma', 'Must'],
    ['FR-005', 'Bloquear automáticamente la bóveda', 'Should'],
    ['FR-006', 'MFA/WebAuthn', 'Should'],
]
story.append(make_table(fr_cuenta, col_widths=[22*mm, 120*mm, 28*mm]))
story.append(Spacer(1, 8))

# 9.2 Chat
add_heading('9.2. Chat', style_h2, level=1, story=story)
fr_chat = [
    ['ID', 'Requisito', 'Prioridad'],
    ['FR-010', 'Chat de texto', 'Must'],
    ['FR-011', 'Mostrar estado del agente', 'Must'],
    ['FR-012', 'Mostrar acción propuesta', 'Must'],
    ['FR-013', 'Editar propuesta antes de ejecutar', 'Must'],
    ['FR-014', 'Mostrar fuentes y memorias utilizadas', 'Must'],
    ['FR-015', 'Adjuntar audio', 'Should'],
    ['FR-016', 'Adjuntar imagen/documento', 'Could'],
    ['FR-017', 'Streaming de respuesta', 'Should'],
]
story.append(make_table(fr_chat, col_widths=[22*mm, 120*mm, 28*mm]))
story.append(Spacer(1, 8))

# 9.3 Memoria
add_heading('9.3. Memoria y grafo', style_h2, level=1, story=story)
fr_memoria = [
    ['ID', 'Requisito', 'Prioridad'],
    ['FR-020', 'Crear memoria explícita', 'Must'],
    ['FR-021', 'Crear nodos y relaciones', 'Must'],
    ['FR-022', 'Buscar por texto', 'Must'],
    ['FR-023', 'Buscar semánticamente', 'Should'],
    ['FR-024', 'Ver procedencia', 'Must'],
    ['FR-025', 'Editar nodo', 'Must'],
    ['FR-026', 'Corregir contradicción', 'Should'],
    ['FR-027', 'Olvidar nodo y relaciones', 'Must'],
    ['FR-028', 'Ver subgrafo limitado', 'Must'],
    ['FR-029', 'Vista alternativa en lista', 'Must'],
    ['FR-030', 'Importar/exportar grafo', 'Must'],
]
story.append(make_table(fr_memoria, col_widths=[22*mm, 120*mm, 28*mm]))
story.append(Spacer(1, 8))

# 9.4 Recordatorios
add_heading('9.4. Recordatorios', style_h2, level=1, story=story)
fr_rec = [
    ['ID', 'Requisito', 'Prioridad'],
    ['FR-040', 'Crear recordatorio puntual', 'Must'],
    ['FR-041', 'Crear recurrencia', 'Must'],
    ['FR-042', 'Resolver zona horaria', 'Must'],
    ['FR-043', 'Detectar ambigüedad', 'Must'],
    ['FR-044', 'Posponer', 'Must'],
    ['FR-045', 'Completar', 'Must'],
    ['FR-046', 'Cancelar', 'Must'],
    ['FR-047', 'Reintentar entrega', 'Must'],
    ['FR-048', 'Evitar duplicados', 'Must'],
    ['FR-049', 'Historial de entregas', 'Should'],
    ['FR-050', 'Ventanas de silencio', 'Should'],
]
story.append(make_table(fr_rec, col_widths=[22*mm, 120*mm, 28*mm]))
story.append(Spacer(1, 8))

# 9.5 Agentes
add_heading('9.5. Agentes y skills', style_h2, level=1, story=story)
fr_ag = [
    ['ID', 'Requisito', 'Prioridad'],
    ['FR-060', 'Crear agente', 'Should'],
    ['FR-061', 'Seleccionar modelo', 'Should'],
    ['FR-062', 'Asignar skills', 'Should'],
    ['FR-063', 'Asignar herramientas', 'Should'],
    ['FR-064', 'Limitar memoria accesible', 'Should'],
    ['FR-065', 'Definir autonomía', 'Should'],
    ['FR-066', 'Mostrar permisos antes de activar', 'Must'],
    ['FR-067', 'Revocar herramienta', 'Must'],
]
story.append(make_table(fr_ag, col_widths=[22*mm, 120*mm, 28*mm]))
story.append(Spacer(1, 8))

# 9.6 MCP
add_heading('9.6. MCP e integraciones', style_h2, level=1, story=story)
fr_mcp = [
    ['ID', 'Requisito', 'Prioridad'],
    ['FR-070', 'Registrar servidor MCP', 'Should'],
    ['FR-071', 'Realizar handshake/healthcheck', 'Should'],
    ['FR-072', 'Mostrar tools y resources', 'Should'],
    ['FR-073', 'Seleccionar scopes', 'Should'],
    ['FR-074', 'Confirmar operaciones de riesgo', 'Must'],
    ['FR-075', 'Desconectar y revocar credenciales', 'Must'],
    ['FR-076', 'Registrar ejecución', 'Must'],
]
story.append(make_table(fr_mcp, col_widths=[22*mm, 120*mm, 28*mm]))
story.append(Spacer(1, 8))

# 9.7 Distribución
add_heading('9.7. Distribución', style_h2, level=1, story=story)
fr_dist = [
    ['ID', 'Requisito', 'Prioridad'],
    ['FR-080', 'Demo mock en GitHub Pages', 'Must'],
    ['FR-081', 'Docker Compose local', 'Must'],
    ['FR-082', 'Build APK', 'Should'],
    ['FR-083', 'Build desktop', 'Should'],
    ['FR-084', 'CLI de diagnóstico', 'Should'],
    ['FR-085', 'Exportación portable', 'Must'],
]
story.append(make_table(fr_dist, col_widths=[22*mm, 120*mm, 28*mm]))

# ===== Section 10: Requisitos no funcionales =====
add_heading('10. Requisitos no funcionales', style_h1, level=0, story=story)

add_heading('10.1. Privacidad', style_h2, level=1, story=story)
story.extend(bullet_list([
    'El modo local no debe enviar contenido fuera del dispositivo salvo activación explícita.',
    'Cada proveedor externo debe estar identificado con nombre, modelo y política de datos.',
    'No se debe presentar como zero-knowledge un flujo donde el proveedor pueda leer plaintext.',
    'El usuario debe poder eliminar memorias, archivos, embeddings y logs asociados.',
]))

add_heading('10.2. Seguridad', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Contraseñas con Argon2id y parámetros robustos.',
    'Cookies seguras (HttpOnly, Secure, SameSite) y sesiones revocables.',
    'Validación de todos los payloads entrantes con schema estricto.',
    'CSP y sanitización de contenido generado por LLM para prevenir XSS.',
    'Protección SSRF para webhooks y conexiones MCP salientes.',
    'Rate limiting distribuido en servidor (por IP, por usuario, por endpoint).',
    'Tokens de integración separados por scope y rotables.',
    'Auditoría de acciones con timestamp, actor y resultado.',
    'Escaneo de dependencias y secretos en CI.',
]))

add_heading('10.3. Disponibilidad', style_h2, level=1, story=story)
story.append(p('Un recordatorio confirmado debe sobrevivir a los siguientes eventos sin perderse ni duplicarse:'))
story.extend(bullet_list([
    'Reinicio de API.',
    'Reinicio de worker.',
    'Reintento del job después de un fallo temporal.',
    'Pérdida temporal de red.',
    'Actualización de contenedor.',
]))

add_heading('10.4. Rendimiento', style_h2, level=1, story=story)
story.append(p('Objetivos iniciales de rendimiento para una instalación personal razonable:'))
perf_data = [
    ['Métrica', 'Objetivo'],
    ['Primera respuesta de interfaz local', '< 200 ms (con datos en cache)'],
    ['Búsqueda textual local', 'P95 < 300 ms para 10.000 memorias'],
    ['Búsqueda híbrida (textual + semántica)', 'P95 < 1 segundo'],
    ['Creación de job de audio', '< 500 ms (transcripción asíncrona)'],
    ['Grafo inicial', '< 1 segundo para hasta 100 nodos visibles'],
]
story.append(make_table(perf_data, col_widths=[90*mm, 80*mm]))

add_heading('10.5. Accesibilidad', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Contraste mínimo AA (4.5:1 texto normal, 3:1 texto grande).',
    'Navegación completa por teclado (Tab, Enter, Esc, atajos).',
    'Etiquetas ARIA para todos los controles interactivos.',
    'Estados no comunicados solo por color (icono + texto).',
    'Respeto a prefers-reduced-motion.',
    'Alternativa de lista para el grafo visual.',
    'Texto legible en pantallas pequeñas (mínimo 14px móvil).',
]))

add_heading('10.6. Portabilidad', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Chrome, Firefox y Edge modernos (últimas 2 versiones mayores).',
    'Android soportado por el APK definido para cada release.',
    'Windows, Linux y macOS según matriz de builds publicada.',
    'Docker en Linux x64 y ARM64 cuando sea posible.',
    'SQLite para modo local y desktop.',
    'PostgreSQL para servidor.',
]))

# ===== Section 11: Privacidad del producto =====
add_heading('11. Diseño de privacidad del producto', style_h1, level=0, story=story)
story.append(p(
    'VNBOT debe presentar tres modos comprensibles de operación. La elección del modo es '
    'explícita por parte del usuario durante el onboarding y se puede cambiar posteriormente '
    'en la configuración. Cada modo tiene implicaciones claras que deben comunicarse sin '
    'ambigüedad.'
))

add_heading('11.1. Modo Local Estricto', style_h2, level=1, story=story)
story.append(p('Todas las operaciones se realizan en el dispositivo del usuario. Sin dependencias externas.'))
story.extend(bullet_list([
    'Memoria almacenada en dispositivo (SQLite o IndexedDB).',
    'Embeddings generados localmente.',
    'Audio procesado localmente.',
    'LLM local vía Ollama, llama.cpp o modelo integrado.',
    'Sin sincronización remota por defecto.',
    'Exportación manual para transferir datos.',
]))

add_heading('11.2. Modo Servidor Privado', style_h2, level=1, story=story)
story.append(p('Instalación propia en servidor elegido por el usuario. Sync entre dispositivos.'))
story.extend(bullet_list([
    'API y base de datos en servidor elegido por el usuario.',
    'El administrador del servidor puede tener acceso técnico al proceso.',
    'Debe explicarse la diferencia entre servidor propio y zero-knowledge.',
    'Integraciones y backups controlados por el propietario del servidor.',
]))

add_heading('11.3. Modo LLM Externo', style_h2, level=1, story=story)
story.append(p('Uso de proveedores LLM externos (OpenAI, Anthropic, etc.) con contexto mínimo.'))
story.extend(bullet_list([
    'El proveedor LLM recibe el contexto mínimo necesario para la operación.',
    'El usuario selecciona proveedor y modelo explícitamente.',
    'Se muestran proveedor, modelo y política de datos del proveedor.',
    'Se pueden bloquear memorias sensibles para proveedores externos.',
]))

# ===== Section 12: Experiencia visual =====
add_heading('12. Experiencia visual como requisito de producto', style_h1, level=0, story=story)
story.append(p(
    'La estética no será una capa decorativa añadida al final. Será parte de la identidad '
    'funcional de VNBOT. La mascota, los estados visuales, los paneles HUD y la tipografía '
    'comunican información operativa real, no solo decoración.'
))

add_heading('12.1. Mascota principal', style_h2, level=1, story=story)
story.append(p(
    'El golem informático será la representación de VNBOT. Debe ser reconocible a 32x32, 64x64 '
    'y 128x128 píxeles. La mascota es el feedback visual principal del estado del sistema y '
    'debe cambiar su pose, visor y animación según las operaciones en curso.'
))

add_heading('12.2. Mascotas por agente', style_h2, level=1, story=story)
story.append(p('Cada agente tendrá una variante coherente de la familia de golems. La variación se expresa mediante:'))
story.extend(bullet_list([
    'Visor (color y patrón).',
    'Accesorio (antena, escudo, lentes, drones).',
    'Paleta (cyan, amber, magenta, violet, green, blue, white).',
    'Silueta secundaria (proporciones del cuerpo).',
    'Animación (idle, hover, processing).',
]))

add_heading('12.3. Estados de la mascota', style_h2, level=1, story=story)
story.append(p('La mascota indicará el estado real del sistema mediante 10 estados visuales:'))
story.extend(bullet_list([
    'Escuchando (listening) — captura de audio/entrada activa.',
    'Pensando (thinking) — clasificación o recuperación en curso.',
    'Procesando (processing) — job activo con anillo multicolor.',
    'Esperando confirmación (waiting_confirmation) — propuesta pendiente.',
    'Ejecutando (executing) — acción en curso.',
    'Completado (success) — operación finalizada con éxito.',
    'Advertencia (warning) — resultado parcial o configuración requerida.',
    'Error (error) — job fallido, postura de alerta.',
    'Desconectado (offline) — sin conexión, visor apagado.',
    'Durmiendo (sleeping) — baja actividad, pose compacta.',
]))
story.append(callout('Toda animación debe acompañarse de texto accesible o estado ARIA. La mascota nunca es el único canal de información.', color=ACCENT))

add_heading('12.4. UI y paneles HUD', style_h2, level=1, story=story)
story.append(p(
    'Los paneles HUD, las retículas y los marcos pixel art no deben impedir la lectura. Los '
    'mensajes, formularios, permisos y logs deben priorizar claridad sobre decoración. La '
    'interfaz prioriza legibilidad, accesibilidad y rendimiento en dispositivos móviles.'
))

# ===== Section 13: Métricas de éxito =====
add_heading('13. Métricas de éxito', style_h1, level=0, story=story)

add_heading('13.1. Métricas de producto', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Tiempo hasta el primer recordatorio (TTFR).',
    'Porcentaje de usuarios que completan onboarding.',
    'Porcentaje de recordatorios creados correctamente en el primer intento.',
    'Tasa de memorias encontradas en consultas de prueba.',
    'Número de memorias corregidas o eliminadas por el usuario.',
    'Uso de exportación (frecuencia y alcance).',
    'Activación de modo local vs servidor.',
    'Número de agentes configurados por usuario.',
]))

add_heading('13.2. Métricas de confiabilidad', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Entregas correctas (porcentaje de ocurrencias entregadas a tiempo).',
    'Duplicados por cada 10.000 ocurrencias (objetivo: 0).',
    'Jobs perdidos (objetivo: 0).',
    'Jobs reintentados con éxito (tasa de recuperación).',
    'Tiempo medio de recuperación (MTTR) tras fallo.',
    'Estado de backups (última verificación exitosa).',
]))

add_heading('13.3. Métricas de comunidad', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Contribuidores activos por mes.',
    'Pull requests aceptados por mes.',
    'Issues resueltos por mes.',
    'Plugins/skills revisados y publicados.',
    'Instalaciones Docker activas (opt-in telemetry).',
    'Descargas de Releases por plataforma.',
    'Documentación consultada (páginas más visitadas).',
]))
story.append(callout(
    'Ninguna métrica de producto debe requerir enviar el contenido privado del usuario a un '
    'servicio de analítica. Las métricas agregadas son opt-in y nunca incluyen contenido de memorias.',
    color=SEM_WARNING
))

# ===== Section 14: Riesgos =====
add_heading('14. Riesgos de producto y mitigaciones', style_h1, level=0, story=story)
story.append(p('Cada riesgo identificado tiene una mitigación concreta. Los riesgos de impacto alto requieren mitigación obligatoria antes del lanzamiento del MVP.'))

riesgos = [
    ['Riesgo', 'Impacto', 'Mitigación'],
    ['Fecha mal interpretada', 'Alto', 'Fecha completa visible y confirmación explícita antes de crear recordatorio.'],
    ['Memoria inventada por alucinación del LLM', 'Alto', 'Procedencia obligatoria, confianza calculada y respuesta basada en fuentes verificadas.'],
    ['Exceso de notificaciones', 'Medio', 'Ventanas de silencio, agrupación y aprendizaje controlado de preferencias.'],
    ['Costes LLM descontrolados', 'Medio', 'Router con fallback a modelos locales, límites por usuario y presupuestos por agente.'],
    ['MCP malicioso', 'Alto', 'Allowlist de servidores, scopes granulares, sandbox y revocación inmediata.'],
    ['Complejidad excesiva', 'Alto', 'MVP pequeño y arquitectura por plugins. Cada nueva capacidad pasa por revisión.'],
    ['Assets incompatibles con licencias', 'Medio', 'Inventario y auditoría de licencias antes de cada release.'],
    ['Pérdida de datos', 'Alto', 'Backups automáticos, exportación manual y pruebas de restore verificadas.'],
    ['Falsa promesa de privacidad', 'Alto', 'Documentar claramente cada modo sin usar zero-knowledge como marketing genérico.'],
    ['Dependencia de una plataforma', 'Medio', 'Adaptadores y canales oficiales. Núcleo no acoplado a un solo proveedor.'],
]
story.append(make_table(riesgos, col_widths=[58*mm, 22*mm, 90*mm]))

# ===== Section 15: Roadmap =====
add_heading('15. Roadmap de producto', style_h1, level=0, story=story)
story.append(p('El roadmap se organiza en 8 versiones desde la demo hasta la plataforma estable. Cada versión tiene criterios de salida claros y no se avanza sin validar la anterior.'))

roadmap = [
    ['Versión', 'Nombre', 'Entregables principales'],
    ['0.1', 'Demo', 'Landing en GitHub Pages, chat simulado, grafo con datos ficticios, mascota y estados visuales, documentación inicial.'],
    ['0.2', 'Local', 'PWA, IndexedDB, bóveda local, recordatorios locales, heurística sin LLM, exportación.'],
    ['0.3', 'Backend privado', 'FastAPI, SQLite/PostgreSQL, worker, scheduler, Docker, healthchecks, LLM Router.'],
    ['0.4', 'Plataformas', 'APK, desktop, CLI, notificaciones nativas, GitHub Releases.'],
    ['0.5', 'Memoria', 'Grafo real, búsqueda híbrida, procedencia, correcciones, expiración.'],
    ['0.6', 'MCP', 'MCP interno, gateway externo, permisos, Graphify opcional, calendario opcional.'],
    ['0.7', 'Agentes', 'Skills, agentes especializados, mascotas por agente, presupuestos, auditoría.'],
    ['1.0', 'Plataforma estable', 'Instalación documentada, backups verificados, releases firmados, plugin SDK, suite de pruebas, guía de seguridad.'],
]
story.append(make_table(roadmap, col_widths=[18*mm, 32*mm, 120*mm]))

# ===== Section 16: Criterios MVP =====
add_heading('16. Criterios de lanzamiento del MVP', style_h1, level=0, story=story)
story.append(p('VNBOT podrá considerarse listo para una primera versión pública cuando se cumplan los siguientes 12 criterios:'))
criterios = [
    'Un usuario pueda instalarlo sin editar código fuente.',
    'El flujo de captura funcione sin LLM mediante heurística básica.',
    'Los recordatorios sean persistentes e idempotentes.',
    'Exista una vista clara de tareas y recordatorios.',
    'La memoria tenga edición, eliminación y procedencia.',
    'El grafo tenga una alternativa textual.',
    'El modo local no dependa de servicios cloud.',
    'El sistema tenga healthchecks y diagnóstico CLI.',
    'Exista exportación y restauración probada.',
    'Los errores no expongan secretos ni contenido privado en logs.',
    'El repositorio tenga CI, licencia, seguridad y guía de contribución.',
    'La demo de GitHub Pages no solicite datos reales.',
]
for i, c in enumerate(criterios, 1):
    story.append(p(f'<b>{i:02d}.</b> {c}', style_body_left))

# ===== Section 17: Backlog =====
add_heading('17. Backlog inicial priorizado', style_h1, level=0, story=story)

add_heading('P0 — Imprescindible', style_h3, level=1, story=story)
story.extend(bullet_list([
    'Crear monorepo.',
    'Implementar modelo de dominio.',
    'Crear almacenamiento local SQLite/IndexedDB.',
    'Crear chat base.',
    'Crear parser heurístico de recordatorios.',
    'Crear scheduler y ocurrencias.',
    'Crear notificación local.',
    'Crear CRUD de memoria.',
    'Crear exportación.',
    'Crear healthchecks.',
    'Crear demo mock para GitHub Pages.',
]))

add_heading('P1 — Necesario para beta', style_h3, level=1, story=story)
story.extend(bullet_list([
    'FastAPI.',
    'PostgreSQL.',
    'Redis y workers.',
    'LLM Router.',
    'Búsqueda híbrida.',
    'Grafo visual.',
    'Docker Compose.',
    'Audio.',
    'APK.',
    'Desktop.',
]))

add_heading('P2 — Expansión', style_h3, level=1, story=story)
story.extend(bullet_list([
    'MCP Gateway.',
    'Graphify adapter.',
    'Calendario.',
    'Skills.',
    'Agentes personalizados.',
    'Briefings.',
    'Telegram.',
    'Gmail como borrador.',
]))

add_heading('P3 — Comunidad y escala', style_h3, level=1, story=story)
story.extend(bullet_list([
    'Plugin SDK.',
    'Marketplace de skills.',
    'Sincronización multi-dispositivo.',
    'Espacios compartidos.',
    'Grafo temporal avanzado.',
    'Métricas agregadas opt-in.',
]))

# ===== Section 18: Fallback heurístico =====
add_heading('18. Fallback heurístico sin LLM — Experiencia mínima aceptable', style_h1, level=0, story=story)
story.append(p(
    'VNBOT debe funcionar sin un proveedor LLM conectado. El fallback heurístico define el '
    'piso de experiencia cuando no hay IA disponible. Este piso no es un modo degradado: es '
    'una experiencia completa y útil para las operaciones más comunes.'
))

add_heading('18.1. Alcance del fallback', style_h2, level=1, story=story)
story.append(p('El sistema heurístico debe cubrir al menos las siguientes intenciones sin LLM:'))

fallback_data = [
    ['Intención', 'Método', 'Ejemplo'],
    ['Crear recordatorio', 'Regex + parsing de fecha/hora natural', '"recuérdame llamar a Ana mañana a las 5" → recordatorio puntual'],
    ['Crear memoria', 'Captura directa sin estructura', '"mi código postal es 1040" → memoria tipo fact'],
    ['Consultar memorias', 'Búsqueda textual exacta y fuzzy', '"buscar Daniel" → coincidencias por texto'],
    ['Listar recordatorios', 'Query directa a storage', '"¿qué tengo hoy?" → recordatorios del día'],
    ['Completar recordatorio', 'Match por ID o texto parcial', '"ya llamé a Ana" → marcar completado'],
    ['Crear lista', 'Comando estructurado', '"lista de compras: leche, pan" → lista con items'],
]
story.append(make_table(fallback_data, col_widths=[38*mm, 50*mm, 82*mm]))

add_heading('18.2. Límites del fallback', style_h2, level=1, story=story)
story.append(p('Lo que el fallback NO debe intentar:'))
story.extend(bullet_list([
    'Inferir relaciones entre memorias (requiere embeddings o reglas complejas).',
    'Interpretar imágenes o audio (requiere modelos específicos).',
    'Generar resúmenes o briefings.',
    'Operar herramientas MCP.',
    'Manejar contexto conversacional multi-turno complejo.',
]))
story.append(p(
    'Cuando el fallback no pueda interpretar una intención, debe responder con un mensaje '
    'claro: "No pude interpretar eso sin un modelo de IA conectado. [Instrucciones para '
    'configurar un proveedor]."'
))

add_heading('18.3. Criterios de aceptación', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Un usuario puede crear, consultar y completar recordatorios sin LLM.',
    'Un usuario puede capturar y buscar memorias sin LLM.',
    'La experiencia sin LLM está documentada en el onboarding.',
    'El fallback tiene tests unitarios con al menos 20 casos de entrada documentados.',
    'El mensaje de "no disponible sin LLM" incluye enlace a configuración.',
]))

# ===== Section 19: Accesibilidad =====
add_heading('19. Requisitos de accesibilidad', style_h1, level=0, story=story)

add_heading('19.1. Estándar objetivo', style_h2, level=1, story=story)
story.append(p(
    'VNBOT debe cumplir WCAG 2.2 nivel AA como mínimo en todas sus interfaces. El nivel AAA '
    'es un objetivo aspiracional para componentes críticos (chat, recordatorios, confirmaciones '
    'de acciones).'
))

add_heading('19.2. Métricas concretas', style_h2, level=1, story=story)
a11y_data = [
    ['Métrica', 'Requisito', 'Verificación'],
    ['Contraste de texto', 'Mínimo 4.5:1 (AA), 3:1 para texto grande', 'Lighthouse + axe-core en CI'],
    ['Contraste de paneles HUD', 'Mínimo 3:1 entre borde de panel y fondo adyacente', 'Manual + herramienta'],
    ['Tamaño mínimo de texto', '14px en móvil, 12px solo en labels no esenciales', 'Design tokens'],
    ['Touch targets', 'Mínimo 44×44px en móvil (WCAG 2.5.8)', 'Layout tests'],
    ['Navegación por teclado', 'Todas las funciones accesibles sin ratón', 'Testing manual e2e'],
    ['Screen reader', 'Labels ARIA en todos los componentes interactivos', 'axe-core + manual'],
    ['Reduced motion', 'Respetar prefers-reduced-motion: reduce', 'CSS + tests visuales'],
    ['Focus visible', 'Indicador de foco visible en todos los elementos interactivos', 'Automated + manual'],
]
story.append(make_table(a11y_data, col_widths=[42*mm, 70*mm, 58*mm]))

add_heading('19.3. Plan de auditoría de accesibilidad', style_h2, level=1, story=story)
story.extend(bullet_list([
    'Auditoría inicial antes de v0.2.',
    'Auditoría por cada release minor (0.x).',
    'axe-core automatizado en CI para cada PR.',
    'Auditoría manual con screen reader (NVDA/VoiceOver) antes de cada release major.',
    'Test con usuarios con discapacidades antes de v1.0.',
]))

# ===== Section 20: Definición de "hecho" =====
add_heading('20. Definición de "hecho" de una funcionalidad', style_h1, level=0, story=story)
story.append(p('Una funcionalidad se considera terminada cuando cumple los siguientes 12 criterios. Ninguno es opcional:'))
def_hecho = [
    'Tiene requisito identificado (FR-xxx).',
    'Tiene diseño UX aprobado.',
    'Tiene contrato de datos/API definido.',
    'Tiene estados de error definidos.',
    'Tiene política de permisos definida.',
    'Tiene pruebas unitarias con cobertura mínima.',
    'Tiene prueba de integración.',
    'Tiene documentación de usuario y técnica.',
    'Tiene comportamiento offline o degradado definido.',
    'No filtra secretos en logs.',
    'Funciona en el entorno objetivo.',
    'Tiene criterio de rollback o migración si modifica datos.',
]
for i, c in enumerate(def_hecho, 1):
    story.append(p(f'<b>{i:02d}.</b> {c}', style_body_left))

# ===== Section 21: Decisiones abiertas =====
add_heading('21. Decisiones abiertas', style_h1, level=0, story=story)
story.append(p('Estas decisiones deberán cerrarse en documentos técnicos posteriores (TRD, Esquema Backend, Plan de Implementación):'))

decisiones = [
    'SQLite local con SQLAlchemy o una capa Rust/SQLite para desktop.',
    'Capacitor frente a React Native si aumentan las funciones nativas.',
    'Celery/Dramatiq frente a un worker Rust.',
    'pgvector frente a un índice vectorial local dedicado.',
    'WebAuthn en el MVP o en una release posterior.',
    'Formato final de skills: Markdown + YAML o JSON Schema + Markdown.',
    'Transporte MCP principal: stdio local y Streamable HTTP remoto.',
    'Sistema de actualización automática de desktop.',
    'Política final de retención de audios.',
    'Compatibilidad exacta de licencias para assets generados y repositorios de referencia.',
]
for i, d in enumerate(decisiones, 1):
    story.append(p(f'<b>{i:02d}.</b> {d}', style_body_left))

# ===== Section 22: Relación con otros documentos =====
add_heading('22. Relación con otros documentos', style_h1, level=0, story=story)
story.append(p('El PRD es parte de un conjunto documental coherente. Cada documento cubre una dimensión específica del proyecto:'))

docs_rel = [
    ['Documento', 'Cobertura'],
    ['Documento Maestro (00)', 'Visión canónica y decisiones generales del proyecto.'],
    ['PRD (01)', 'Este documento. Definición de producto, requisitos y criterios.'],
    ['TRD (02)', 'Decisiones técnicas y requisitos de infraestructura.'],
    ['Esquema Backend (03)', 'Servicios, API, jobs y eventos del backend.'],
    ['Plan de Implementación (04)', 'Fases y ejecución detallada del desarrollo.'],
    ['Diseño UI/UX (05)', 'Interfaz, mascotas y sistema visual completo.'],
    ['App Flow (06)', 'Recorridos, estados y transiciones de usuario.'],
    ['Modelo de Datos (07)', 'Entidades, relaciones y persistencia.'],
    ['Seguridad y Privacidad (08)', 'Amenazas, controles y privacidad por diseño.'],
    ['MCP y Skills (09)', 'Herramientas, agentes y permisos.'],
    ['Roadmap (10)', 'Releases, prioridades y dependencias temporales.'],
]
story.append(make_table(docs_rel, col_widths=[55*mm, 115*mm]))

# ===== Section 23: Conclusión =====
add_heading('23. Conclusión', style_h1, level=0, story=story)
story.append(p(
    'VNBOT debe empezar como un sistema pequeño y fiable, no como un agente omnipotente. El '
    'núcleo del producto es la relación entre captura, memoria y recordatorio. Los LLM, MCP, '
    'agentes, canales y assets visuales deben ampliar ese núcleo sin ocultar su funcionamiento '
    'ni debilitar la privacidad.'
))
story.append(p('La primera pregunta para cada nueva funcionalidad debe ser:'))
story.append(callout(
    '¿Ayuda al usuario a recordar, encontrar o ejecutar algo de manera más confiable y '
    'controlable?',
    color=ACCENT
))
story.append(p(
    'Si la respuesta es afirmativa, la funcionalidad puede incorporarse mediante un módulo, '
    'skill, integración o agente con permisos claros. Si la respuesta es negativa, debe '
    'permanecer fuera del núcleo aunque sea técnicamente atractiva. La disciplina en esta '
    'pregunta es lo que separa a VNBOT de una colección desordenada de funciones de IA.'
))

# ===== Build PDF =====
output_body = '/home/z/my-project/scripts/prd_body.pdf'
doc = TocDocTemplate(
    output_body,
    pagesize=A4,
    leftMargin=20*mm,
    rightMargin=20*mm,
    topMargin=22*mm,
    bottomMargin=22*mm,
    title='VNBOT — Product Requirements Document',
    author='VNBOT Project',
    subject='PRD v1.0.0-draft',
    creator='Z.ai',
)
doc.multiBuild(story, onFirstPage=page_decoration, onLaterPages=page_decoration)
print(f'Body PDF generated: {output_body}')
print(f'Size: {os.path.getsize(output_body) / 1024:.1f} KB')
