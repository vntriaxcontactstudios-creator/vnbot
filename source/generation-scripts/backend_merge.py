#!/usr/bin/env python3
"""Merge Esquema Backend cover + body into single final PDF."""
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

cover_path = '/home/z/my-project/scripts/backend_cover.pdf'
body_path = '/home/z/my-project/scripts/backend_body.pdf'
output_path = '/home/z/my-project/download/VNBOT_ESQUEMA_BACKEND.pdf'

A4_W = 595.275590551
A4_H = 841.889763780

writer = PdfWriter()

cover_reader = PdfReader(cover_path)
for page in cover_reader.pages:
    page.mediabox = RectangleObject((0, 0, A4_W, A4_H))
    page.cropbox = RectangleObject((0, 0, A4_W, A4_H))
    page.trimbox = RectangleObject((0, 0, A4_W, A4_H))
    page.bleedbox = RectangleObject((0, 0, A4_W, A4_H))
    page.artbox = RectangleObject((0, 0, A4_W, A4_H))
    writer.add_page(page)

body_reader = PdfReader(body_path)
for page in body_reader.pages:
    writer.add_page(page)

writer.add_metadata({
    '/Title': 'VNBOT — Esquema Backend',
    '/Author': 'VNBOT Project',
    '/Subject': 'Esquema Backend v1.0.0-draft — Servicios, API, jobs, scheduler, MCP, observabilidad',
    '/Creator': 'Z.ai',
    '/Producer': 'Z.ai PDF Pipeline',
    '/Keywords': 'VNBOT, backend, API, MCP, LLM, scheduler, observability, jobs, idempotency',
})

with open(output_path, 'wb') as f:
    writer.write(f)

import os
size = os.path.getsize(output_path) / 1024
total_pages = len(cover_reader.pages) + len(body_reader.pages)
print(f'Final PDF: {output_path}')
print(f'Size: {size:.1f} KB')
print(f'Total pages: {total_pages} (1 cover + {len(body_reader.pages)} body)')
