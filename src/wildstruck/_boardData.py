import dataclasses as dc
from pathlib import Path
from typing import List, Sequence, Tuple


@dc.dataclass
class BoardData:
    width: int
    height: int

    def __post_init__(self):
        self._data = [["00000000" for _ in range(self.width)] for _ in range(self.height)]

    @property
    def data(self) -> List[List[str]]:
        """
        A copy of this Board's internal data with each cell's RGBA represented as a string of 4
        hexadecimal bytes.
        """
        return [r.copy() for r in self._data]

    @data.setter
    def data(self, value: Sequence[Sequence[str]]):
        self.set_range(0, 0, value)

    def color_alpha(self, x: int, y: int) -> Tuple[str, str]:
        return self.split(self._data[y][x])

    def color(self, x: int, y: int) -> str:
        return self.color_alpha(x, y)[0]

    def alpha(self, x: int, y: int) -> str:
        return self.color_alpha(x, y)[1]

    def set(self, x: int, y: int, color: str, alpha: str):
        self._data[y][x] = self.merge(color, alpha)

    def get(self, x: int, y: int) -> Tuple[str, str]:
        return self.split(self._data[y][x])

    def set_range(self, x: int, y: int, data: Sequence[Sequence[str | Tuple[str, str]]]):
        for y in range(y, min(self.height, len(data))):
            row = data[y]
            for x in range(x, min(self.width, len(row))):
                cell = row[x]
                if isinstance(cell, str):
                    color, alpha = self.split(cell)
                else:
                    color, alpha = cell
                self.set(x, y, color, alpha)

    @staticmethod
    def load(biomeMapPath: str | Path, heightMapPath: str | Path | None = None) -> "BoardData":
        from PIL import Image

        biomeMap = Image.open(biomeMapPath)
        h, w, c = biomeMap.height, biomeMap.width, len(biomeMap.mode)
        heightMap = biomeMap
        heightMapChannel = 3
        if heightMapPath is not None:
            heightMap = Image.open(heightMapPath).convert("L")
            hh, ww = heightMap.height, heightMap.width
            if hh != h or ww != w:
                raise ValueError("Biome map and height map must have the same size")
            heightMapChannel = 0
        elif c < 4:
            raise ValueError("Biome map must have an alpha channel if no height map is provided")
        board = BoardData(w, h)
        for y in range(h):
            for x in range(w):
                color = biomeMap.getpixel((x, y))[:3]  # type: ignore # Let it error out in bad case
                colorHex = (hex(color[0])[2:] + hex(color[1])[2:] + hex(color[2])[2:]).rjust(6, "0")
                height = heightMap.getpixel((y, x))[heightMapChannel]  # type: ignore
                heightHex = hex(height)[2:].rjust(2, "0")
                board.set(w - 1 - x, y, colorHex, heightHex)
        return board

    @staticmethod
    def split(colorAlpha: str) -> Tuple[str, str]:
        return colorAlpha[:6], colorAlpha[6:]

    @staticmethod
    def merge(color: str, alpha: str) -> str:
        return f"{color}{alpha}"
