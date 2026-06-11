import numpy as np
from PIL import Image
from paddleocr import PaddleOCR


class OCRService:
    def __init__(self, lang="en"):
        self.lang = lang
        self._ocr = None

    def _engine(self):
        if self._ocr is None:
            self._ocr = PaddleOCR(use_angle_cls=True, lang=self.lang, show_log=False)
        return self._ocr

    def image_to_text(self, image: Image.Image) -> str:
        ocr = self._engine()
        result = ocr.ocr(np.array(image), cls=True)

        lines = []
        if result and result[0]:
            for item in result[0]:
                text = item[1][0]
                if text and text.strip():
                    lines.append(text.strip())
        return "\n".join(lines).strip()