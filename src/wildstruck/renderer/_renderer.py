import dataclasses as dc
from math import ceil
import random
from typing import Any, Callable, List, MutableMapping, Tuple, TypeVar


from .config import RendererConfig
from ._taleSpireSlab import TaleSpireSlab
from .._vec import Vec3
from .._boardData import BoardData


def alpha_height(alpha: str, maxHeight: int = 64) -> float:
    # Currently the maximum z precision in TaleSpire is 1/4 grid
    return int(alpha, 16) * (maxHeight / 256)


@dc.dataclass
class Renderer:
    config: RendererConfig

    def render(
        self,
        boardData: BoardData,
        maxHeight: int = 64,
        colorMapName: None | str = None,
        seed: int | str = 9001,
    ) -> TaleSpireSlab:
        if colorMapName is not None:
            self.config.activeBiomeMap = self.config.find_by_name(
                colorMapName, self.config.biomeMaps
            )
        slab = TaleSpireSlab()
        for y in range(boardData.height):
            for x in range(boardData.width):
                slab.assets.extend(self.generate_cell(slab, boardData, x, y, maxHeight, seed))
        return slab

    def generate_cell(
        self,
        slab: TaleSpireSlab,
        boardData: BoardData,
        x: int,
        y: int,
        maxHeight: int = 64,
        seed: int | str = 9001,
    ) -> List[Any]:

        assets = []

        # Cells could already be filled due to 2x2 tiles
        if all(slab.cells_occupied(x, y)):  # The all is just to avoid indexing the list of 1
            return assets

        # A set seed must be used for the entire cell process for repeatability
        random.seed(f"{seed}:{x},{y}")

        color, alpha = boardData.color_alpha(x, y)
        biome = self.config.find_by_name(
            self.config.activeBiomeMap.colors[color.upper()], self.config.biomes
        )
        z = alpha_height(alpha, maxHeight)

        biomeVariant = biome.tiles.choose()
        if biomeVariant is None:
            return assets
        biomeTile = biomeVariant.value
        tile = self.config.find_by_name(biomeTile.tileRef.name, self.config.tiles)

        # Placing 2x2 tiles must be prioritized otherwise the space might already be filled by 1x1s
        # 2x2 tiles also require that all 4 cells are of the same height
        tileSize = min(min(x + 2, boardData.width) - x, min(y + 2, boardData.height) - y)
        if tileSize > 1:
            data = [
                (boardData.color(hx, hy), alpha_height(boardData.alpha(hx, hy), maxHeight))
                for hy in range(y, y + tileSize)
                for hx in range(x, x + tileSize)
            ]
            if (
                not tile.twoByTwoAvailable
                or any(slab.cells_occupied(x, y, tileSize, tileSize))
                or not all(((c == color and h == z) for c, h in data))
            ):
                tileSize = 1
        tileSourceVariant = tile.sources.choose(lambda t: (t.value.size == tileSize))
        if tileSourceVariant is not None:
            tileSource = tileSourceVariant.value

            # The tile asset knows how to randomize the transform
            tileCenter = Vec3(x, y, z)
            assets.append(tileSource.generate_asset(tileCenter, 0))
            slab.occupy_cells(x, y, tileSize, tileSize)

            # Fill downwards to cover gaps in large z differences
            if tileSize == 2:
                toSample = ((1, 0), (2, 0), (1, 3), (2, 3), (0, 1), (0, 2), (3, 1), (3, 2))
            else:
                toSample = ((1, 0), (1, 2), (0, 1), (2, 1))
            minHeight = min(
                (
                    alpha_height(
                        boardData.alpha(
                            max(0, min(x + ox - 1, boardData.width - 1)),
                            max(0, min(y + oy - 1, boardData.height - 1)),
                        ),
                        maxHeight,
                    )
                    for ox, oy in toSample
                )
            )
            fillCenter = tileCenter - Vec3.Forward() * 0.5
            while fillCenter.z >= minHeight:
                assets.append(tileSource.generate_asset(fillCenter, 0))
                fillCenter -= Vec3.Forward() * 0.5

        # The biome tile may define props cluttering
        for ty in range(tileSize):
            for tx in range(tileSize):

                for ci, clutter in enumerate(biomeTile.clutter):
                    if clutter.randomMethod == "true":
                        # Reduced chance to spawn in true random due to the added dimension
                        if random.random() >= pow(clutter.coverage, 2):
                            continue

                    elif clutter.randomMethod == "jitter":
                        cx, cy = x + tx, y + ty
                        clutterPlacementKey = f"{biome.name}:{tile.name}:{ci}"
                        clutterPlacement = _get_factory(
                            _get_factory(slab.slabData, "clutterPlacement", dict),
                            clutterPlacementKey,
                            _jitter_clutter(
                                boardData.width, boardData.height, 1 / clutter.coverage
                            ),
                        )
                        if (cx, cy) not in clutterPlacement:
                            continue

                    else:
                        raise ValueError(f"Invalid random method '{clutter.randomMethod}'")

                    propRef = clutter.choose()
                    if propRef is None:
                        continue
                    propVariant = self.config.find_by_name(
                        propRef.name, self.config.props
                    ).sources.choose()
                    if propVariant is None:
                        continue
                    prop = propVariant.value

                    # Centered x/y, at the top of the tile
                    propAssets = prop.generate_assets(
                        Vec3(x + tx + 0.5, y + ty + 0.5, z + tileSource.thickness), 0
                    )
                    assets.extend(propAssets)
        return assets


T = TypeVar("T")


def _get_factory(mapping: MutableMapping, key: Any, factory: Callable[[], T]) -> T:
    if key not in mapping:
        mapping[key] = factory()
    return mapping[key]


def _jitter_clutter(width: int, height: int, minDist: float) -> Callable[[], List[Tuple[int, int]]]:
    def _inner() -> List[Tuple[int, int]]:
        halfDist = minDist * 0.5
        points = [
            (
                round(x * minDist + random.random() * max(minDist - 1, 1) - halfDist),
                round(
                    y * minDist
                    - (halfDist if x % 2 == 0 else 0)
                    + random.random() * max(minDist - 1, 1)
                    - halfDist
                ),
            )
            for y in range(-1, ceil(height / minDist) + 1)
            for x in range(-1, ceil(width / minDist) + 1)
        ]
        return points

    return _inner
