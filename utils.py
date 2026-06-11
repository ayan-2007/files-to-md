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


def is_gibberish(text: str) -> bool:
    if not text:
        return True
    text_clean = text.strip()
    if not text_clean:
        return True
    
    # Count control characters or private-use area characters (indicates bad encoding/font mapping)
    control_chars = sum(1 for c in text_clean if ord(c) < 32 and c not in "\n\r\t")
    private_use_chars = sum(1 for c in text_clean if 0xE000 <= ord(c) <= 0xF8FF)
    
    total_len = len(text_clean)
    if (control_chars + private_use_chars) / total_len > 0.05:
        return True
        
    # Check proportion of standard alphanumeric/space/common punctuation characters
    allowed_chars = sum(1 for c in text_clean if c.isalnum() or c.isspace() or c in ".,!?-:;()[]{}'\"/\\@#%&*+=_<>`~$|•")
    if (allowed_chars / total_len) < 0.7:
        return True
        
    # Must contain at least one alphanumeric character
    alphanumeric = sum(1 for c in text_clean if c.isalnum())
    if alphanumeric == 0:
        return True
        
    return False