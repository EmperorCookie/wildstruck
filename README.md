# Wildstruck

A terrain generator for TaleSpire.

Procedural generators are good for when you don't know what you want. Modular tilesets are good for
when you know what you want, but it can be hard to create or find good ones, and they offer very
little granularity.

This tool is a sort of middleground between both options. You draw your map in any paint program and
the let Wildstruck generate your terrain for you.

# Usage

Execute "wildstruck.exe" in a command-line to see the help.

## Example

```
wildstruck wildstruck.json5 biomes-test.png --maxHeight 1
```

## Configuration

The included `wildstruck.json5` configuration file comes with basic biomes and two ways to map
colors to biomes.

To edit the file, simply follow the instructions given by the `--configSchema` option.

### Biomes

See comments in the config file to know which biomes have been created so far.

# Roadmap

Roughly in order of priorities:

1. Create release pipeline
1. Add option to use nearest biome by color when missing
1. Support for TaleSpire slabs as props
1. Tileset behavior (to allow for paths and walls to detect what's around them)
1. Support for the multi-paste mod
