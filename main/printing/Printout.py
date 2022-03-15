from datetime import datetime
from typing import Tuple

from PIL import Image, ImageDraw, ImageOps
from pathlib import Path

class Printout:
    def __init__(self, image: Image, offset: Tuple[int, int]):
        self.image = image
        self.draw = ImageDraw.Draw(image)
        self.offset = offset

    def save(self, filename: str):
        now = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'output/{filename}_{now}.jpg'
        Path(Path(filename).parent).mkdir(parents=True, exist_ok=True)
        self.image = ImageOps.flip(self.image)
        self.image.save(filename)
