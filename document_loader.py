"""
Plain Speak — Document loader.

Handles the three input modes we care about:
  1. PDF — extract text with pypdf (fast, no OCR needed for text PDFs).
  2. Image (jpg/png/etc.) — either passed directly to a vision-capable
     Gemma 4 model, or OCR'd with pytesseract for text-only variants.
  3. Plain text / pasted text — used as-is.

We deliberately keep this dependency-light: pypdf, Pillow, pytesseract.
Tesseract itself is an optional system dependency; if it's missing and
the user uploads an image with a text-only model, we fall back with a
clear error message instead of crashing.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Optional, Tuple

# Extensions we recognise as images (vs PDFs vs raw text).
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".gif"}
PDF_EXTS = {".pdf"}
TEXT_EXTS = {".txt", ".md"}


def classify(path: str) -> str:
    """Return 'image', 'pdf', 'text', or 'unknown' for a given file path."""
    ext = Path(path).suffix.lower()
    if ext in IMAGE_EXTS:
        return "image"
    if ext in PDF_EXTS:
        return "pdf"
    if ext in TEXT_EXTS:
        return "text"
    return "unknown"


def load_pdf_text(path: str) -> str:
    """Extract all text from a PDF, page by page, with light cleanup."""
    from pypdf import PdfReader  # local import keeps startup snappy

    reader = PdfReader(path)
    chunks = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            chunks.append(f"[Page {i}]\n{text}")
    if not chunks:
        raise ValueError(
            "Could not extract any text from this PDF. It may be a scanned "
            "image — try uploading it as an image file instead so the vision "
            "model can read it."
        )
    return "\n\n".join(chunks)


def load_image_bytes(path: str) -> bytes:
    """Read an image file as bytes (used for multimodal Gemma 4 calls)."""
    return Path(path).read_bytes()


def load_image_ocr(path: str) -> str:
    """OCR an image with Tesseract. Used when the chosen Gemma 4 model
    does not support vision. Raises a clear error if Tesseract is missing."""
    try:
        import pytesseract
        from PIL import Image
    except ImportError as e:
        raise RuntimeError(
            "OCR requires pytesseract and Pillow. Install with: "
            "pip install pytesseract pillow — and install the Tesseract "
            "binary for your OS (https://tesseract-ocr.github.io)."
        ) from e

    try:
        text = pytesseract.image_to_string(Image.open(path))
    except pytesseract.TesseractNotFoundError as e:
        raise RuntimeError(
            "Tesseract is not installed on this machine. Either install it "
            "(https://tesseract-ocr.github.io) or switch to a vision-capable "
            "Gemma 4 model like gemma4:9b in the sidebar."
        ) from e

    text = text.strip()
    if not text:
        raise ValueError(
            "OCR found no text in this image. Try a clearer photo, or use a "
            "vision-capable model that can interpret blurry documents."
        )
    return text


def load_text_file(path: str) -> str:
    """Read a .txt or .md file as UTF-8, falling back to latin-1."""
    p = Path(path)
    try:
        return p.read_text(encoding="utf-8").strip()
    except UnicodeDecodeError:
        return p.read_text(encoding="latin-1").strip()


def load_document(
    path: str, use_vision: bool
) -> Tuple[str, Optional[bytes], str]:
    """Top-level dispatch. Returns (text_for_prompt, image_bytes_or_none, kind).

    - text_for_prompt: the text we'll show to the model (empty string when
      sending an image to a vision model).
    - image_bytes_or_none: image bytes to attach to the chat call, or None.
    - kind: one of 'pdf', 'image-vision', 'image-ocr', 'text'.
    """
    kind = classify(path)
    if kind == "pdf":
        return load_pdf_text(path), None, "pdf"
    if kind == "image":
        if use_vision:
            return "", load_image_bytes(path), "image-vision"
        return load_image_ocr(path), None, "image-ocr"
    if kind == "text":
        return load_text_file(path), None, "text"
    raise ValueError(
        f"Unsupported file type: {Path(path).suffix}. Upload a PDF, image, "
        "or plain text file."
    )
