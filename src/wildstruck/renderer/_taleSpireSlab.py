from collections import defaultdict
import dataclasses as dc
from math import ceil
from typing import Dict, Iterator, List, Tuple


from ._taleSpireAsset import TaleSpireAsset
from .. import _slabelfish as sf
from .._vec import Vec3


def make_chunks(data: list, chunks: int) -> Iterator[list]:
    chunkLength = len(data) // chunks + 1
    for i in range(0, len(data), chunkLength):
        yield data[i : i + chunkLength]


@dc.dataclass
class TaleSpireSlab:
    assets: List[TaleSpireAsset] = dc.field(default_factory=list)
    cellData: Dict[Tuple[int, int], dict] = dc.field(default_factory=lambda: defaultdict(dict))
    slabData: dict = dc.field(default_factory=dict)

    def _add_to_cells(self, value: int, x: int, y: int, w: int = 1, h: int = 1):
        for j in range(y, y + h):
            for i in range(x, x + w):
                cellData = self.cellData[(i, j)]
                cellData["occupancy"] = max(0, cellData.get("occupancy", 0) + value)

    def occupy_cells(self, x: int, y: int, w: int = 1, h: int = 1):
        self._add_to_cells(1, x, y, w, h)

    def unoccupy_cells(self, x: int, y: int, w: int = 1, h: int = 1):
        self._add_to_cells(-1, x, y, w, h)

    def cells_occupied(self, x: int, y: int, w: int = 1, h: int = 1) -> List[bool]:
        return [
            (self.cellData[(i, j)].get("occupancy", 0) > 0)
            for j in range(y, y + h)
            for i in range(x, x + w)
        ]

    def export_talespire(self, chunkSize: int = 32) -> List[bytes]:
        xMax, yMax = 0, 0
        for asset in self.assets:
            if asset.position.x > xMax:
                xMax = asset.position.x
            if asset.position.y > yMax:
                yMax = asset.position.y

        pastes = []
        remainingAssets = self.assets.copy()
        cxMax, cyMax = ceil(xMax / chunkSize), ceil(yMax / chunkSize)
        for cy in range(cxMax):
            for cx in range(cyMax):
                x1 = -chunkSize if cx == 0 else cx * chunkSize
                y1 = -chunkSize if cy == 0 else cy * chunkSize
                x2 = chunkSize * (cx + (2 if cx >= cxMax - 1 else 1))
                y2 = chunkSize * (cy + (2 if cy >= cyMax - 1 else 1))

                instances = defaultdict(list)
                unusedAssets = []
                lowestAsset = None
                for asset in remainingAssets:
                    if (
                        asset.position.x >= x1
                        and asset.position.x < x2
                        and asset.position.y >= y1
                        and asset.position.y < y2
                    ):
                        instances[asset.uuid].append(asset)
                        if lowestAsset is None or asset.position.z < lowestAsset.position.z:
                            lowestAsset = asset
                    else:
                        unusedAssets.append(asset)
                remainingAssets = unusedAssets

                if len(instances) == 0:
                    continue

                if lowestAsset is not None and lowestAsset.position.z != 0:
                    zeroAsset = lowestAsset.copy()
                    zeroAsset.position = Vec3(zeroAsset.position.x, zeroAsset.position.y, 0)
                    instances[zeroAsset.uuid].append(zeroAsset)

                slab = sf.Slab(
                    unique_asset_count=len(instances),
                    asset_data=[
                        sf.AssetData(
                            uuid=u,
                            instance_count=len(l),
                            instances=[
                                sf.AssetTransform(
                                    x=round((a.position.x - x1) * 100),
                                    y=round((a.position.y - y1) * 100),
                                    z=round(a.position.z * 100) + 300,
                                    degree=a.snappedRotation,
                                )
                                for a in l
                            ],
                        )
                        for u, l in instances.items()
                    ],
                )

                pastes.append(slab.encode())
        return pastes
