#!/usr/bin/env python3
"""Merge PRD cover + body into single final PDF. Normalizes page sizes."""
import sys
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

cover_path = '/home/z/my-project/scripts/prd_cover.pdf'
body_path = '/home/z/my-project/scripts/prd_body.pdf'
output_path = '/home/z/my-project/download/VNBOT_PRD.pdf'

# Target A4 size in points (matches ReportLab body)
A4_W = 595.275590551
A4_H = 841.889763780

writer = PdfWriter()

# Add cover — normalize to exact A4
cover_reader = PdfReader(cover_path)
for page in cover_reader.pages:
    # Force the page bounding box to exact A4 dimensions
    page.mediabox = RectangleObject((0, 0, A4_W, A4_H))
    page.cropbox = RectangleObject((0, 0, A4_W, A4_H))
    page.trimbox = RectangleObject((0, 0, A4_W, A4_H))
    page.bleedbox = RectangleObject((0, 0, A4_W, A4_H))
    page.artbox = RectangleObject((0, 0, A4_W, A4_H))
    writer.add_page(page)

# Add body
body_reader = PdfReader(body_path)
for page in body_reader.pages:
    writer.add_page(page)

# Set metadata
writer.add_metadata({
    '/Title': 'VNBOT — Product Requirements Document',
    '/Author': 'VNBOT Project',
    '/Subject': 'PRD v1.0.0-draft — Definición de producto, requisitos y criterios',
    '/Creator': 'Z.ai',
    '/Producer': 'Z.ai PDF Pipeline',
    '/Keywords': 'VNBOT, PRD, product requirements, open source, memory, agents, MCP',
})

with open(output_path, 'wb') as f:
    writer.write(f)

import os
size = os.path.getsize(output_path) / 1024
total_pages = len(cover_reader.pages) + len(body_reader.pages)
print(f'Final PDF: {output_path}')
print(f'Size: {size:.1f} KB')
print(f'Total pages: {total_pages} (1 cover + {len(body_reader.pages)} body)')

