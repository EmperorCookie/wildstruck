## [3.0.0](https://github.com/EmperorCookie/wildstruck/compare/v2.0.3...v3.0.0) (2024-11-14)


### ⚠ BREAKING CHANGES

* Fixed config validation silently ignoring invalid object keys
* Renamed 'sources' key to 'source' in config
* Moved snapping to random transform and added position snapping

### Features

* Added 'validate' command to CLI to remove the jsonschemavalidator.net middleman ([3992c3e](https://github.com/EmperorCookie/wildstruck/commit/3992c3e962c1c5ff3e69fefe7bba92bf57d5a091))
* Added support for TaleSpire copy-paste props, replace the 'stack' key with a 'data' key in the variants, the value should be a TaleSpire slab string ([562ebc4](https://github.com/EmperorCookie/wildstruck/commit/562ebc4c08d1c0393cc775e08e98771b692e11a6))
* Modified offset to be optional in config ([0898c5b](https://github.com/EmperorCookie/wildstruck/commit/0898c5ba216266ee86f4936523d7258a4ae549f3))
* Modified the renderer to use a random seed if none is provided ([4ca9f41](https://github.com/EmperorCookie/wildstruck/commit/4ca9f41ab2e3f6ebdfbff07e6630bba99a5b6b67))
* Moved snapping to random transform and added position snapping ([4f111d7](https://github.com/EmperorCookie/wildstruck/commit/4f111d73ca41528c32c01cbb266cca53bd6df24c))


### Bug Fixes

* Fixed certain config validations being ignored, which could've lead to crashes ([ba519c9](https://github.com/EmperorCookie/wildstruck/commit/ba519c921c63a2509d76456b0600ef1c22b97eb5))
* Fixed config validation silently ignoring invalid object keys ([207b074](https://github.com/EmperorCookie/wildstruck/commit/207b07494840eb355092dcf9e426eb9ae9b5fef8))
* Fixed issue where assets would not be included if they were outside of the terrain area ([2b06cdd](https://github.com/EmperorCookie/wildstruck/commit/2b06cdd9d45e4954994f517f1479676c71b52866))
* Fixed slabs sometimes not pasting due to assets being at invalid coordinates ([97ad02f](https://github.com/EmperorCookie/wildstruck/commit/97ad02f08826bd94b3be944525dff1b523e818b9))
* Fixed stacked assets not being properly rotated around the origin ([3450e54](https://github.com/EmperorCookie/wildstruck/commit/3450e54addaab8cd07d55bff539a108799366414))
* Renamed 'sources' key to 'source' in config ([fb28987](https://github.com/EmperorCookie/wildstruck/commit/fb289876bfbda367b844e5533f0d135a16fbe7fa))

## [2.0.3](https://github.com/EmperorCookie/wildstruck/compare/v2.0.2...v2.0.3) (2024-11-08)


### Bug Fixes

* Added descriptions to the schema and version CLI commands ([6086ad1](https://github.com/EmperorCookie/wildstruck/commit/6086ad17e85b83b098846a953580df610a6100dd))
* Added missing attribution for pygparse ([46366ec](https://github.com/EmperorCookie/wildstruck/commit/46366ecd88b9f4586d878eedccd200784b6cbdcb))

## [2.0.2](https://github.com/EmperorCookie/wildstruck/compare/v2.0.1...v2.0.2) (2024-11-08)


### Bug Fixes

* Fixed example in README ([825182c](https://github.com/EmperorCookie/wildstruck/commit/825182c6e5c5b4ce0adadad71b9ac26677dc8154))

## [2.0.0](https://github.com/EmperorCookie/wildstruck/compare/v1.0.0...v2.0.0) (2024-11-08)


### ⚠ BREAKING CHANGES

* Renamed 'exportChunkSize' to 'chunkSize' in CLI
* Modified CLI to use subcommands to avoid the problem with schema/version requiring a config and map

### Features

* Modified CLI to use subcommands to avoid the problem with schema/version requiring a config and map ([0221424](https://github.com/EmperorCookie/wildstruck/commit/02214240a081a40f79e51102adb7f1afd6469617))
* Renamed 'exportChunkSize' to 'chunkSize' in CLI ([5743324](https://github.com/EmperorCookie/wildstruck/commit/5743324ac09921efea481ad2a65076324449d9e0))


### Bug Fixes

* Fixed error in the config JSONSchema ([26e912d](https://github.com/EmperorCookie/wildstruck/commit/26e912dfd3ed514a5cfbf1d137a5a1ec9155193c))

## [1.0.0](https://github.com/EmperorCookie/wildstruck/compare/v0.0.5...v1.0.0) (2024-11-08)


### ⚠ BREAKING CHANGES

* Initial release

### Features

* Initial release ([ce63cd7](https://github.com/EmperorCookie/wildstruck/commit/ce63cd7b58c4a385cb839ea6a592e6701ab5c10b))


### Bug Fixes

* Removed version option that is not working, will readd later in a better way ([0e3f3a4](https://github.com/EmperorCookie/wildstruck/commit/0e3f3a4e7f3a985b038bb72fffe08caba9c37b9b))

## [0.0.5](https://github.com/EmperorCookie/wildstruck/compare/v0.0.4...v0.0.5) (2024-11-08)


### Bug Fixes

* Added missing pyperclip dependency ([323002f](https://github.com/EmperorCookie/wildstruck/commit/323002ff75712afa363ffe338a3b9ab9bc39cf76))

## [0.0.4](https://github.com/EmperorCookie/wildstruck/compare/v0.0.3...v0.0.4) (2024-11-08)


### Bug Fixes

* Include application name in version output ([8947593](https://github.com/EmperorCookie/wildstruck/commit/894759341827bc81f16db5aeaba3d3f60c066ea2))
