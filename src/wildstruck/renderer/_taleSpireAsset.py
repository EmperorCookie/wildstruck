import dataclasses as dc
from uuid import UUID as Uuid

from .._vec import Vec3


@dc.dataclass
class TaleSpireAsset:
    uuid: Uuid
    position: Vec3
    rotation: float

    @property
    def snappedRotation(self) -> int:
        return round(self.rotation / 15) * 15

    def copy(self) -> "TaleSpireAsset":
        return TaleSpireAsset(self.uuid, self.position, self.rotation)
