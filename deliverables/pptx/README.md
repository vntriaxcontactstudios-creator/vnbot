# PPTX Deliverables

Los archivos PPTX están excluidos del repo por tamaño (64MB + 82MB).

## Cómo regenerarlos

```bash
# UI/UX Design System (39 slides)
cd source/html-slides/uiux-design-system
node /path/to/batch_html2pptx.js . ../../deliverables/pptx/VNBOT_UIUX_DESIGN_SYSTEM.pptx

# App Flow (57 slides)
cd source/html-slides/app-flow
node /path/to/batch_html2pptx.js . ../../deliverables/pptx/VNBOT_APP_FLOW.pptx
```

Alternativamente, descarga los PPTX pre-generados desde GitHub Releases.
