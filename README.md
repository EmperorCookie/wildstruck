# Wildstruck

A data-driven terrain generator for TaleSpire.

Procedural generators are good for when you don't know what you want. Modular tilesets are good for
when you know what you want, but it can be hard to create or find good ones, and they offer very
little granularity.

This tool is a sort of middleground between both options. You draw your map in any paint program and
the let Wildstruck generate your terrain for you.

# Installation

Find the [latest release](https://github.com/EmperorCookie/wildstruck/releases) and download
the zip file. There is no installation, the executable can just be ran.

To install the [Python library](https://pypi.org/project/wildstruck/), use `pip install wildstruck`,
but be aware that it does not inlcude the default config file nor the biomes-test file.

# Usage

Execute `wildstruck.exe` in a command-line to see the help.

## Example

```
wildstruck render wildstruck.json5 biomes-test.png --maxHeight 1
```

## Configuration

The included [`wildstruck.json5`](https://github.com/EmperorCookie/wildstruck/blob/main/wildstruck.json5)
configuration file comes with basic biomes and two ways to map colors to biomes.

To edit the file, simply follow the instructions given by the `schema` command.

### Biomes

See comments in the config file to know which biomes have been created so far.

### Configuration File Updates

IMPORTANT: New versions of the download file will not be created for updates that do not require a
version bump, therefore the latest version of these files will be found in the repository itself if
there is a discrepancy.

See the [commits for `wildstruck.json5`](https://github.com/EmperorCookie/wildstruck/commits/main/wildstruck.json5) for a detailed changelog.

# Roadmap

Roughly in order of priorities:

1. Finish biome presets
1. Add option to use nearest biome by color when missing
1. Water behavior (fill with tiles up to a specific height)
1. Tileset behavior (to allow for paths and walls to detect what's around them)
1. Support for the multi-paste mod
