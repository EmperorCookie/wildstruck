import json
from pathlib import Path

from .renderer.config import RendererConfig
from .renderer import Renderer
from . import BoardData


def load_renderer(configJsonPath: str | Path) -> Renderer:
    return Renderer(config=load_renderer_config(configJsonPath))


def load_renderer_config(configJsonPath: str | Path) -> RendererConfig:
    path = Path(configJsonPath)
    if path.suffix == ".json5":
        import pyjson5 as json5

        with path.open("r") as f:
            data = json5.loads(f.read())
        data = json.dumps(data)
    else:
        with path.open("r") as f:
            data = f.read()
    return RendererConfig.model_validate_json(data)


def load_board_data(biomeMapPath: str | Path, heightMapPath: str | Path | None = None) -> BoardData:
    """If no heightMap is provided, the alpha channel of the main image is used."""
    return BoardData.load(biomeMapPath, heightMapPath)
