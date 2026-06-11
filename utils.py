import re
import os

SUPPORTED_EXTENSIONS = {
    ".pdf", ".txt", ".docx", ".html", ".htm", ".rtf", ".epub",
    ".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"
}


def safe_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]+', "_", name)
    name = name.strip().strip(".")
    return name if name else "untitled"


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()