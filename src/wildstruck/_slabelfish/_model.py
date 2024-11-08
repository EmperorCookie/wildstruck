from typing import Dict, List
from typing_extensions import Self
from uuid import UUID as Uuid

from pydantic import BaseModel, Field, field_validator, model_validator

from ._encoder import encode


class AssetTransform(BaseModel):
    x: int
    y: int
    z: int
    degree: int

    @field_validator("x", "y", "z")
    @classmethod
    def coordinates_constraint(cls, value: int) -> int:
        if value < 0:
            raise ValueError("Coordinates must be >= 0")
        return value

    @field_validator("degree")
    @classmethod
    def rotation_constraint(cls, value: int) -> int:
        return round((value % 360) / 15) * 15


class AssetData(BaseModel):
    uuid: Uuid
    instance_count: int
    instances: List[AssetTransform]

    @model_validator(mode="after")
    def validate(self) -> Self:
        if self.instance_count != len(self.instances):
            raise ValueError("Instance count must reflect actual number of instances")
        return self


class Slab(BaseModel):
    unique_asset_count: int
    asset_data: List[AssetData]

    @model_validator(mode="after")
    def validate(self) -> Self:
        if self.unique_asset_count != len(self.asset_data):
            raise ValueError("Unique asset count must reflect actual number of unique assets")
        return self

    def encode(self) -> bytes:
        return encode(self.model_dump_json(), validate=True, quiet=True)
