"""VNBOT API — Vision Language Model (VLM) integration.

Uses Z.AI glm-4.6v (no API key required) for image analysis.
Per ADR-0010: analyzes images extracted from documents, screenshots,
illustrations, diagrams, and photos.
"""

from __future__ import annotations

import base64
import logging
from dataclasses import dataclass

import httpx

from ...config import get_settings

logger = logging.getLogger("vnbot.api.vlm")

# Prompts by context (per ADR-0010 §3.3)
PROMPTS = {
    "document": "Extrae todo el texto de esta imagen. Preserva la estructura y formato.",
    "ui": "Describe la interfaz de usuario. Lista los elementos visibles, botones, campos de texto, y su disposición.",
    "error": "¿Qué error o mensaje se muestra? Describe el problema técnico visible.",
    "illustration": "Describe la ilustración: estilo, paleta de colores, composición, elementos principales, técnica digital.",
    "diagram": "Describe el diagrama. Identifica nodos, conexiones, flujo, y tipo (flowchart, mindmap, UML, etc.).",
    "code": "Extrae el código fuente visible en esta imagen. Preserva indentación y formato.",
    "general": "Describe esta imagen en detalle: objetos, personas, escena, colores, contexto, texto visible.",
}


@dataclass
class VLMResult:
    """Result of VLM analysis."""
    description: str
    model: str
    success: bool
    error: str | None = None


async def analyze_image(
    image_bytes: bytes,
    prompt: str = "general",
    mime_type: str = "image/png",
) -> VLMResult:
    """Analyze an image using Z.AI glm-4.6v.

    Args:
        image_bytes: Raw image bytes
        prompt: Either a prompt key (document, ui, error, illustration, diagram, code, general)
                or a custom prompt string.
        mime_type: MIME type of the image (image/png, image/jpeg, etc.)

    Returns:
        VLMResult with description or error.
    """
    settings = get_settings()

    if settings.llm_provider != "zai":
        return VLMResult(
            description="[VLM no disponible — proveedor no es Z.AI]",
            model="none",
            success=False,
            error="VLM only available with Z.AI provider",
        )

    # Resolve prompt
    actual_prompt = PROMPTS.get(prompt, prompt)

    # Encode image as base64
    b64 = base64.b64encode(image_bytes).decode("ascii")
    data_url = f"data:{mime_type};base64,{b64}"

    try:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if settings.llm_api_key:
            headers["Authorization"] = f"Bearer {settings.llm_api_key}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.llm_zai_base_url}/chat/completions",
                json={
                    "model": "glm-4.6v",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": actual_prompt},
                                {"type": "image_url", "image_url": {"url": data_url}},
                            ],
                        }
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500,
                },
                headers=headers,
            )

            if response.status_code != 200:
                logger.warning(f"VLM returned {response.status_code}: {response.text[:200]}")
                return VLMResult(
                    description=f"[VLM error: HTTP {response.status_code}]",
                    model="glm-4.6v",
                    success=False,
                    error=f"HTTP {response.status_code}",
                )

            data = response.json()
            description = data["choices"][0]["message"]["content"].strip()

            return VLMResult(
                description=description,
                model="glm-4.6v",
                success=True,
            )

    except httpx.TimeoutException:
        logger.warning("VLM request timed out")
        return VLMResult(
            description="[VLM timeout — imagen no analizada]",
            model="glm-4.6v",
            success=False,
            error="timeout",
        )
    except Exception as e:
        logger.warning(f"VLM request failed: {type(e).__name__}: {e}")
        return VLMResult(
            description=f"[VLM error: {type(e).__name__}]",
            model="glm-4.6v",
            success=False,
            error=str(e),
        )


async def analyze_images_batch(
    images: list[bytes],
    prompt: str = "general",
    mime_type: str = "image/png",
    max_images: int = 20,
) -> list[VLMResult]:
    """Analyze multiple images. Limits to max_images per ADR-0010 §4.

    Images beyond max_images are skipped.
    """
    results: list[VLMResult] = []
    for img in images[:max_images]:
        result = await analyze_image(img, prompt, mime_type)
        results.append(result)
    if len(images) > max_images:
        logger.info(f"Skipped {len(images) - max_images} images (max_images={max_images})")
    return results
