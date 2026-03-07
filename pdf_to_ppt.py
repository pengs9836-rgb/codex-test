#!/usr/bin/env python3
"""Convert a PDF into a PPTX with one slide per page.

This converter is optimized for fidelity: each PDF page is rasterized at high DPI and
inserted as a full-slide image so that layout, fonts, charts, and graphics are kept.
"""

from __future__ import annotations

import argparse
import io
import math
import sys
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image
from pptx import Presentation
from pptx.util import Inches


DEFAULT_DPI = 300
# 16:9 widescreen default in python-pptx
DEFAULT_SLIDE_WIDTH_IN = 13.333
DEFAULT_SLIDE_HEIGHT_IN = 7.5


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert PDF to PPTX with high visual fidelity (one page per slide)."
    )
    parser.add_argument("pdf", type=Path, help="Input PDF path")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output PPTX path (default: same name as PDF)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=DEFAULT_DPI,
        help=f"Rasterization DPI (default: {DEFAULT_DPI})",
    )
    parser.add_argument(
        "--keep-temp-images",
        action="store_true",
        help="Do not delete intermediate PNG files",
    )
    return parser.parse_args()


def get_output_path(pdf_path: Path, output: Path | None) -> Path:
    if output:
        return output
    return pdf_path.with_suffix(".pptx")


def px_to_inches(px: int, dpi: int) -> float:
    return px / dpi


def configure_slide_size(prs: Presentation, page_rect: fitz.Rect) -> None:
    page_width_in = px_to_inches(math.ceil(page_rect.width), 72)
    page_height_in = px_to_inches(math.ceil(page_rect.height), 72)

    page_ratio = page_width_in / page_height_in
    default_ratio = DEFAULT_SLIDE_WIDTH_IN / DEFAULT_SLIDE_HEIGHT_IN

    if page_ratio >= default_ratio:
        prs.slide_width = Inches(DEFAULT_SLIDE_WIDTH_IN)
        prs.slide_height = Inches(DEFAULT_SLIDE_WIDTH_IN / page_ratio)
    else:
        prs.slide_height = Inches(DEFAULT_SLIDE_HEIGHT_IN)
        prs.slide_width = Inches(DEFAULT_SLIDE_HEIGHT_IN * page_ratio)


def convert_pdf_to_ppt(pdf_path: Path, output_path: Path, dpi: int) -> None:
    if dpi < 72:
        raise ValueError("DPI must be >= 72 for acceptable quality.")

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    doc = fitz.open(pdf_path)
    if doc.page_count == 0:
        raise ValueError("Input PDF has no pages.")

    prs = Presentation()
    blank_layout = prs.slide_layouts[6]

    first_page = doc.load_page(0)
    configure_slide_size(prs, first_page.rect)

    scale = dpi / 72
    matrix = fitz.Matrix(scale, scale)

    for i in range(doc.page_count):
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=matrix, alpha=False)

        image_bytes = pix.tobytes("png")
        image_stream = io.BytesIO(image_bytes)

        with Image.open(io.BytesIO(image_bytes)) as img:
            img_width_px, img_height_px = img.size

        img_width_in = px_to_inches(img_width_px, dpi)
        img_height_in = px_to_inches(img_height_px, dpi)

        slide = prs.slides.add_slide(blank_layout)

        slide_width_in = prs.slide_width / 914400
        slide_height_in = prs.slide_height / 914400

        img_ratio = img_width_in / img_height_in
        slide_ratio = slide_width_in / slide_height_in

        if img_ratio > slide_ratio:
            width = prs.slide_width
            height = int(prs.slide_width / img_ratio)
            left = 0
            top = int((prs.slide_height - height) / 2)
        else:
            height = prs.slide_height
            width = int(prs.slide_height * img_ratio)
            top = 0
            left = int((prs.slide_width - width) / 2)

        slide.shapes.add_picture(image_stream, left, top, width=width, height=height)

    prs.save(output_path)
    doc.close()


def main() -> int:
    args = parse_args()
    output_path = get_output_path(args.pdf, args.output)

    try:
        convert_pdf_to_ppt(args.pdf, output_path, args.dpi)
    except Exception as exc:  # pragma: no cover - CLI error path
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Converted: {args.pdf} -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
