from abc import abstractmethod
from enum import Enum
from annotated_types import Ge, Le
from math import inf, radians as deg2rad
import random
from typing import Annotated, Any, Callable, Dict, Generic, Iterable, List, Tuple, TypeVar
from uuid import UUID as Uuid

from pydantic import BaseModel, Field, StringConstraints

from .._taleSpireAsset import TaleSpireAsset
from ..._vec import Vec2, Vec3


T = TypeVar("T")


def quantize_rotation(rotation: float, cardinal: bool) -> int:
    factor = 90 if cardinal else 15
    return round((rotation % 360) / factor) * factor


class RendererConfig(BaseModel):
    biomeMaps: List["BiomeMap"] = Field(default_factory=list, min_length=1)
    biomes: List["Biome"] = Field(default_factory=list)
    tiles: List["Tile"] = Field(default_factory=list)
    props: List["Prop"] = Field(default_factory=list)

    def model_post_init(self, _):
        self._activeBiomeMap = self.biomeMaps[0]

    @property
    def activeBiomeMap(self) -> "BiomeMap":
        return self._activeBiomeMap

    @activeBiomeMap.setter
    def activeBiomeMap(self, value: "BiomeMap"):
        if value not in self.biomeMaps:
            raise ValueError(f"BiomeMap '{value.name}' is not in this config's biomeMaps")
        self._activeBiomeMap = value

    def find_by_name(self, name: str, findIn: Iterable["AnyNamed"]) -> "AnyNamed":
        for item in findIn:
            if item.name == name:
                return item
        raise ValueError(f"No item named '{name}' was found")


class Named(BaseModel):
    name: str


AnyNamed = TypeVar("AnyNamed", bound=Named)


class BiomeMap(Named):
    colors: Dict[
        Annotated[str, StringConstraints(to_upper=True, pattern=r"^[a-fA-F0-9]{6}$")],
        str,
    ] = Field(min_length=1)


class WeightedVarying(BaseModel, Generic[T]):
    variants: List["WeightedVariant[T]"] = Field(default_factory=list)

    def choose(
        self, variantFilter: Callable[["WeightedVariant[T]"], bool] | None = None
    ) -> "WeightedVariant[T] | None":
        if len(self.variants) == 0:
            return None
        variants = self.variants
        if variantFilter is not None:
            variants = list(filter(variantFilter, variants))
        return random.choices(variants, [v.weight for v in variants])[0]


class WeightedVariant(BaseModel, Generic[T]):
    weight: Annotated[float, Ge(0)]
    value: T


class Biome(Named):
    tiles: "WeightedVarying[BiomeTile]"


class BiomeTile(BaseModel):
    tileRef: "NamedRef"
    clutter: List["Clutter"] = Field(default_factory=list)


class RandomMethod(str, Enum):
    TRUE = "true"
    JITTER = "jitter"


class Clutter(BaseModel):
    coverage: Annotated[float, Ge(0), Le(1)]
    randomMethod: RandomMethod = Field(default=RandomMethod.TRUE)
    props: "WeightedVarying[NamedRef]"

    def choose(self) -> "NamedRef | None":
        variant = self.props.choose()
        if variant is not None:
            return variant.value
        return None


class NamedRef(BaseModel):
    name: str


class Tile(Named):
    sources: "WeightedVarying[TaleSpireTileSource]"

    @property
    def twoByTwoAvailable(self) -> bool:
        return any((v.value.size == 2 for v in self.sources.variants))


class Source(BaseModel):
    offset: "RandomTransform"

    @abstractmethod
    def generate_asset(self, position: Vec3, rotation: float) -> Any:
        pass


class RandomTransform(BaseModel):
    xMin: float
    xMax: float
    xSnap: float | None = Field(default=None)
    yMin: float
    yMax: float
    ySnap: float | None = Field(default=None)
    zMin: float
    zMax: float
    zSnap: float | None = Field(default=None)
    degMin: float
    degMax: float
    degSnap: float | None = Field(default=None)

    @property
    def vecMin(self) -> Vec3:
        return Vec3(self.xMin, self.yMin, self.zMin)

    @property
    def vecMax(self) -> Vec3:
        return Vec3(self.xMax, self.yMax, self.zMax)

    @property
    def vecRange(self) -> Vec3:
        return self.vecMax - self.vecMin

    @property
    def degRange(self) -> float:
        return self.degMax - self.degMin

    def apply(self, position: Vec3, rotation: float) -> Tuple[Vec3, float]:
        outPos = position + self.vecMin + Vec3.Random() * self.vecRange
        outPos = Vec3(
            *(
                (outPos[i] if snap is None else _snap(outPos[i], snap))  # type: ignore # Linter bug
                for i, snap in enumerate((self.xSnap, self.ySnap, self.zSnap))
            )
        )
        outRot = rotation + self.degMin + random.random() * self.degRange
        if self.degSnap is not None:
            outRot = _snap(outRot, self.degSnap)
        return outPos, outRot


def _snap(value: float, snap: float) -> float:
    return round(value / snap) * snap


class TaleSpireSource(Source):
    uuid: Uuid

    def generate_asset(self, position: Vec3, rotation: float) -> TaleSpireAsset:
        return TaleSpireAsset(self.uuid, *self.offset.apply(position, rotation))


class TileSource(Source):
    size: int
    thickness: float


class TaleSpireTileSource(TileSource):
    uuid: Uuid

    def generate_asset(self, position: Vec3, rotation: float) -> TaleSpireAsset:
        return TaleSpireAsset(self.uuid, *self.offset.apply(position, rotation))


class Prop(Named):
    sources: "WeightedVarying[StackedSource]"


class StackedSource(Source):
    stack: List["WeightedVarying[TaleSpireSource]"]

    def generate_asset(self, position: Vec3, rotation: float) -> List[TaleSpireAsset]:
        newPosition, newRotation = self.offset.apply(position, rotation)
        assets = []
        for i in range(len(self.stack)):
            variant = self.stack[i].choose()
            if variant is not None:
                asset = variant.value.generate_asset(Vec3.Zero(), newRotation)
                asset.position = newPosition + _offset_rotate(asset.position, newRotation)
                assets.append(asset)
        return assets


def _offset_rotate(position: Vec3, rotation: float) -> Vec3:
    """Rotates `position` around (0, 0) by `rotation` degrees, counter-clockwise."""
    return Vec3(*Vec2(position.x, position.y).rotate(deg2rad(rotation)), position.z)
