from pathlib import Path

from ._pygparse import Cli, Flag


def wildstruck(
    configPath: Path,
    mapPath: Path,
    *,
    heightmapPath: Path | None = None,
    biomeMap: str | None = None,
    maxHeight: int = 64,
    seed: int | str = 9001,
    exportChunkSize: int = 32,
    configSchema: bool = False,
) -> int:
    """
    Converts biome map and heightmap images into TaleSpire slabs to be pasted in-game.

    Positional:
        configPath:
            Path to the json config file. Supports JSON5.

        mapPath:
            Path to the map image. Unless heightmapPath is specified, the image must have a
            transparency channel which will be used as a heightmap.

    Options:
        heightmapPath:
            Path to the heightmap file. Color images will be converted to grayscale, and the
            transparency channel is ignored.

        biomeMap:
            The name of the biome map to use from the config file. The first in the list is used by
            default.

        maxHeight:
            Determines what a height of 100% corresponds to in TaleSpire.

        seed:
            The seed to use for random operations like rotation and placement.

        exportChunkSize:
            The size of each paste in tiles.

        configSchema:
            If specified, outputs the jsonschema for the config file and exits. Use in conjunction
            with jsonschemavalidator.net to make changes to the config file.
    """
    if configSchema:
        import json

        from .renderer.config import RendererConfig

        print(json.dumps(RendererConfig.model_json_schema()))
        return 0
    import pyperclip as cb

    from ._helper import load_board_data, load_renderer

    renderer = load_renderer(configPath)
    boardData = load_board_data(mapPath, heightmapPath)

    print("Rendering...")
    slab = renderer.render(boardData, maxHeight=maxHeight, colorMapName=biomeMap, seed=seed)

    print("Exporting...")
    pastes = slab.export_talespire(exportChunkSize)
    for i, paste in enumerate(pastes, 1):
        cb.copy(paste.decode())
        message = f"{i}/{len(pastes)} copied to clipboard..."
        if i < len(pastes):
            input(message)
        else:
            print(message)

    print("Done")
    return 0


def _int_or_str(value: str) -> int | str:
    try:
        return int(value)
    except:
        return value


cli = Cli(
    wildstruck,
    aliases={
        "hm": "heightmapPath",
    },
    constructors=dict(
        heightmapPath=Path,
        biomeMap=str,
        seed=_int_or_str,
        configSchema=Flag(),
        version=Flag(),
    ),
    autoAliases=True,
)
