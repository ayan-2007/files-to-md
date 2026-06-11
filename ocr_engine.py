import numpy as np
from PIL import Image
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self, lang="en"):
        self.lang = lang
        self._ocr = None
        self._use_fallback = False

        # Tesseract language mapping (defaults to input or "eng" if mapped)
        tess_lang_map = {
            "en": "eng",
            "ch": "chi_sim",
            "fr": "fra",
            "de": "deu",
            "es": "spa",
            "it": "ita",
            "pt": "por",
            "ru": "rus",
            "ja": "jpn",
            "ko": "kor"
        }
        self.tess_lang = tess_lang_map.get(self.lang, self.lang)

    def _engine(self):
        if self._ocr is not None or self._use_fallback:
            return self._ocr

        try:
            from paddleocr import PaddleOCR
            # Handle differences across PaddleOCR versions
            try:
                self._ocr = PaddleOCR(use_angle_cls=True, lang=self.lang, show_log=False)
            except (TypeError, ValueError):
                try:
                    self._ocr = PaddleOCR(use_angle_cls=True, lang=self.lang)
                except (TypeError, ValueError):
                    self._ocr = PaddleOCR(lang=self.lang)
            logger.info("PaddleOCR engine initialized successfully.")
        except Exception as e:
            logger.warning(f"PaddleOCR failed to initialize: {e}. Falling back to PyTesseract.")
            self._use_fallback = True
            try:
                import pytesseract
            except ImportError:
                logger.error("Neither PaddleOCR nor PyTesseract is available.")
                raise RuntimeError("OCR requested but no working OCR engine (PaddleOCR or PyTesseract) is installed.")
        
        return self._ocr

    def image_to_text(self, image: Image.Image) -> str:
        engine = self._engine()

        if self._use_fallback:
            import pytesseract
            try:
                logger.info(f"Performing OCR using PyTesseract (lang={self.tess_lang})...")
                return pytesseract.image_to_string(image, lang=self.tess_lang).strip()
            except Exception as e:
                logger.warning(f"PyTesseract OCR failed with lang={self.tess_lang}: {e}. Retrying with default 'eng'...")
                if self.tess_lang != "eng":
                    try:
                        return pytesseract.image_to_string(image, lang="eng").strip()
                    except Exception:
                        pass
                raise e

        logger.info("Performing OCR using PaddleOCR...")
        result = engine.ocr(np.array(image), cls=True)

        lines = []
        if result and result[0]:
            for item in result[0]:
                text = item[1][0]
                if text and text.strip():
                    lines.append(text.strip())
        return "\n".join(lines).strip()