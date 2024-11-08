from abc import abstractmethod
import random
from typing import Any, Callable, Dict, Generic, Iterable, List, Tuple, TypeVar
from uuid import UUID as Uuid

from pydantic import BaseModel, Field

from .._taleSpireAsset import TaleSpireAsset

from ..._vec import Vec3


T = TypeVar("T")


def quantize_rotation(rotation: float, cardinal: bool) -> int:
    factor = 90 if cardinal else 15
    return round((rotation % 360) / factor) * factor


class RendererConfig(BaseModel):
    biomeMaps: List["BiomeMap"] = Field(default_factory=list, json_schema_extra={"minItems": 1})
    biomes: List["Biome"] = Field(default_factory=list)
    tiles: List["Tile"] = Field(default_factory=list)
    props: List["Prop"] = Field(default_factory=list)

    def model_post_init(self, __context):
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
    colors: Dict[str, str] = Field(
        json_schema_extra={
            "minProperties": 1,
            "patternProperties": {r"^[a-fA-F0-9]{6}$": {"title": "BiomeName", "type": "string"}},
        }
    )


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
    weight: float = Field(json_schema_extra={"minimum": 0})
    value: T


class Biome(Named):
    tiles: "WeightedVarying[BiomeTile]"


class BiomeTile(BaseModel):
    tileRef: "NamedRef"
    clutter: List["Clutter"] = Field(default_factory=list)


class Clutter(BaseModel):
    coverage: float = Field(json_schema_extra={"minimum": 0, "maximum": 1})
    randomMethod: str = Field(default="true", json_schema_extra={"enum": ["true", "jitter"]})
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
    yMin: float
    yMax: float
    zMin: float
    zMax: float
    degMin: float
    degMax: float

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
        return (
            position + self.vecMin + Vec3.Random() * self.vecRange,
            rotation + self.degMin + random.random() * self.degRange,
        )


def _generate_talespire_asset(
    source: "TaleSpireSource | TaleSpireTileSource", position: Vec3, rotation: float
) -> TaleSpireAsset:
    newPosition, newRotation = source.offset.apply(position, rotation)
    newRotation = round(newRotation / source.angleSnap) * source.angleSnap
    return TaleSpireAsset(source.uuid, newPosition, newRotation)


class TaleSpireSource(Source):
    uuid: Uuid
    angleSnap: float = Field(default=15)

    def generate_asset(self, position: Vec3, rotation: float) -> Any:
        return _generate_talespire_asset(self, position, rotation)


class TileSource(Source):
    size: int
    thickness: float


class TaleSpireTileSource(TileSource):
    uuid: Uuid
    angleSnap: float = Field(default=90)

    def generate_asset(self, position: Vec3, rotation: float) -> Any:
        return _generate_talespire_asset(self, position, rotation)


class Prop(Named):
    sources: "WeightedVarying[StackedSource]"


class StackedSource(Source):
    stack: List["WeightedVarying[TaleSpireSource]"]

    def generate_asset(self, position: Vec3, rotation: float, stackIndex: int) -> Any:
        variant = self.stack[stackIndex].choose()
        if variant is not None:
            return variant.value.generate_asset(position, rotation)
        return None

    def generate_assets(self, position: Vec3, rotation: float) -> List[Any]:
        newPosition, newRotation = self.offset.apply(position, rotation)
        assets = []
        for i in range(len(self.stack)):
            asset = self.generate_asset(newPosition, newRotation, i)
            if asset is not None:
                assets.append(asset)
        return assets
