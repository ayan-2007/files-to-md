import os
import tempfile
from PIL import Image
import fitz

from utils import normalize_whitespace
from ocr_engine import OCRService

try:
    from docx import Document
except Exception:
    Document = None

try:
    from markdownify import markdownify as mdify
except Exception:
    mdify = None

try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

try:
    from striprtf.striprtf import rtf_to_text
except Exception:
    rtf_to_text = None

try:
    from ebooklib import epub
    from ebooklib import ITEM_DOCUMENT
except Exception:
    epub = None
    ITEM_DOCUMENT = None


def extract_pdf_tables(page):
    try:
        words = page.get_text("words")
        if not words:
            return []

        rows = {}
        for w in words:
            x0, y0, x1, y1, txt, block, line, word_no = w
            key = round(y0 / 5) * 5
            rows.setdefault(key, []).append((x0, txt))

        lines = []
        for y in sorted(rows.keys()):
            parts = [t for _, t in sorted(rows[y], key=lambda x: x[0])]
            line = " | ".join(parts).strip()
            if line:
                lines.append(line)

        if len(lines) >= 2:
            cols = max(2, lines[0].count(" | ") + 1)
            md = []
            md.append("| " + lines[0] + " |")
            md.append("|" + "|".join([" --- "] * cols) + "|")
            for line in lines[1:]:
                md.append("| " + line + " |")
            return ["\n".join(md)]
    except Exception:
        pass
    return []


def extract_pdf_to_markdown(path, use_ocr=True, ocr_lang="en"):
    doc = fitz.open(path)
    ocr = OCRService(lang=ocr_lang)
    output = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        output.append(f"# Page {page_num + 1}\n")

        # First: try selectable text
        text = page.get_text("text").strip()

        if text:
            output.append(normalize_whitespace(text) + "\n")
        else:
            # Fallback: OCR for scanned/image PDFs
            if use_ocr:
                pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                    img_path = tmp.name
                try:
                    pix.save(img_path)
                    img = Image.open(img_path).convert("RGB")
                    text = ocr.image_to_text(img)
                    output.append(normalize_whitespace(text) + "\n")
                finally:
                    if os.path.exists(img_path):
                        os.remove(img_path)

        tables = extract_pdf_tables(page)
        if tables:
            output.append("\n".join(tables) + "\n")

        output.append("\n---\n")

    return normalize_whitespace("\n".join(output)) + "\n"


def txt_to_md_from_bytes(data):
    return normalize_whitespace(data.decode("utf-8", errors="replace")) + "\n"


def docx_to_md_from_bytes(data):
    if Document is None:
        raise RuntimeError("python-docx not installed.")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        doc = Document(tmp_path)
        lines = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            style = (para.style.name or "").lower()
            if "title" in style or "heading 1" in style:
                lines.append(f"# {text}")
            elif "heading 2" in style:
                lines.append(f"## {text}")
            elif "heading 3" in style:
                lines.append(f"### {text}")
            else:
                lines.append(text)
        return normalize_whitespace("\n\n".join(lines)) + "\n"
    finally:
        os.remove(tmp_path)


def html_to_md_from_bytes(data):
    if BeautifulSoup is None or mdify is None:
        raise RuntimeError("beautifulsoup4 and markdownify not installed.")
    html = data.decode("utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")
    return normalize_whitespace(mdify(str(soup), heading_style="ATX")) + "\n"


def rtf_to_md_from_bytes(data):
    if rtf_to_text is None:
        raise RuntimeError("striprtf not installed.")
    rtf = data.decode("utf-8", errors="replace")
    return normalize_whitespace(rtf_to_text(rtf)) + "\n"


def epub_to_md_from_bytes(data):
    if epub is None or ITEM_DOCUMENT is None:
        raise RuntimeError("ebooklib not installed.")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".epub") as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        book = epub.read_epub(tmp_path)
        parts = []
        for item in book.get_items():
            if item.get_type() == ITEM_DOCUMENT:
                html = item.get_content().decode("utf-8", errors="replace")
                if BeautifulSoup is not None and mdify is not None:
                    soup = BeautifulSoup(html, "html.parser")
                    parts.append(mdify(str(soup), heading_style="ATX"))
                else:
                    parts.append(html)
        return normalize_whitespace("\n\n---\n\n".join(parts)) + "\n"
    finally:
        os.remove(tmp_path)