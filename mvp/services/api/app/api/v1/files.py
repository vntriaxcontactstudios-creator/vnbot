"""VNBOT API — File upload and analysis endpoints.

POST   /api/v1/files/read           — upload + read a file
GET    /api/v1/files/supported       — list supported extensions
POST   /api/v1/files/analyze-image   — analyze an image with VLM

Per ADR-0010: FileReader Registry with 80+ extensions + VLM vision.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from ...dependencies import get_workspace_id
from ...infrastructure.files import get_supported_extensions, read_file, FileContent
from ...infrastructure.files.vlm import analyze_image, analyze_images_batch, VLMResult

logger = logging.getLogger("vnbot.api.files")

router = APIRouter(tags=["files"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB per ADR-0010 §4


class FileReadResponse(BaseModel):
    filename: str
    extension: str
    mime_type: str
    text: str
    metadata: dict
    images_count: int
    vlm_descriptions: list[str]
    reader_used: str


class SupportedExtensionsResponse(BaseModel):
    extensions: list[str]
    total: int


class AnalyzeImageRequest(BaseModel):
    """Not used — image is sent as multipart upload."""


class AnalyzeImageResponse(BaseModel):
    description: str
    model: str
    success: bool
    error: str | None


@router.get("/files/supported", response_model=SupportedExtensionsResponse)
async def list_supported_extensions() -> SupportedExtensionsResponse:
    """List all supported file extensions."""
    exts = get_supported_extensions()
    return SupportedExtensionsResponse(extensions=exts, total=len(exts))


@router.post("/files/read", response_model=FileReadResponse)
async def upload_and_read_file(
    file: UploadFile = File(...),
    analyze_images: bool = True,
    workspace_id: str = Depends(get_workspace_id),
) -> FileReadResponse:
    """Upload a file and read its content.

    Supports 80+ extensions per ADR-0010.
    Images within documents are analyzed with VLM (Z.AI glm-4.6v).
    """
    # Check file size
    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB",
        )

    filename = file.filename or "unknown.txt"

    # Read file using registry
    try:
        content: FileContent = await read_file(data, filename)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(e),
        )

    # Analyze images with VLM if present and enabled
    vlm_descriptions: list[str] = []
    if analyze_images and content.images:
        logger.info(f"Analyzing {len(content.images)} images with VLM...")
        results = await analyze_images_batch(content.images, prompt="general")
        vlm_descriptions = [r.description for r in results if r.success]

    # Determine extension
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "unknown"

    return FileReadResponse(
        filename=filename,
        extension=ext,
        mime_type=content.mime_type,
        text=content.text,
        metadata=content.metadata,
        images_count=len(content.images),
        vlm_descriptions=vlm_descriptions,
        reader_used=content.reader_used,
    )


@router.post("/files/analyze-image", response_model=AnalyzeImageResponse)
async def analyze_image_endpoint(
    file: UploadFile = File(...),
    prompt: str = "general",
    workspace_id: str = Depends(get_workspace_id),
) -> AnalyzeImageResponse:
    """Analyze an image directly with VLM (Z.AI glm-4.6v).

    Prompt options: document, ui, error, illustration, diagram, code, general.
    """
    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image too large. Max size: {MAX_FILE_SIZE // (1024*1024)}MB",
        )

    mime_type = file.content_type or "image/png"

    result: VLMResult = await analyze_image(data, prompt=prompt, mime_type=mime_type)

    return AnalyzeImageResponse(
        description=result.description,
        model=result.model,
        success=result.success,
        error=result.error,
    )
