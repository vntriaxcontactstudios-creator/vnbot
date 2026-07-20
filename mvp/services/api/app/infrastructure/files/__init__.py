"""VNBOT API — Files infrastructure."""

from .registry import (
    FileContent,
    SUPPORTED_EXTENSIONS,
    get_supported_extensions,
    read_file,
    register_reader,
)

__all__ = [
    "FileContent",
    "SUPPORTED_EXTENSIONS",
    "get_supported_extensions",
    "read_file",
    "register_reader",
]
