# 🌈 Queemoji Scripts

[![Python Version](https://img.shields.io/badge/python-3.11-blue)](https://github.com/nuztalgia/queemoji/blob/main/scripts/pyproject.toml)
[![Build Status](https://img.shields.io/github/actions/workflow/status/nuztalgia/queemoji/build.yml?branch=main)](https://github.com/nuztalgia/queemoji/actions/workflows/build.yml)
[![CodeQL Status](https://img.shields.io/github/actions/workflow/status/nuztalgia/queemoji/codeql.yml?branch=main&label=scan)](https://github.com/nuztalgia/queemoji/actions/workflows/codeql.yml)
[![CodeFactor](https://img.shields.io/codefactor/grade/github/nuztalgia/queemoji/main)](https://www.codefactor.io/repository/github/nuztalgia/queemoji)
[![Libraries.io Dependencies](https://img.shields.io/librariesio/github/nuztalgia/queemoji)](https://libraries.io/github/nuztalgia/queemoji)

The `queemoji-scripts` Python package contains various scripts for automating
parts of the [Queemoji](https://github.com/nuztalgia/queemoji) project.

If you're just looking to use the finished images, you can head over to the
[`assets`] directory for instructions on how to download them.

The rest of this `README` file is targeted at those who would like to use
(and/or contribute to) the [`scripts`] contained in this package.

[`assets`]: https://github.com/nuztalgia/queemoji/tree/main/assets
[`scripts`]: https://github.com/nuztalgia/queemoji/tree/main/scripts

## Requirements

- `git` - https://git-scm.com/downloads
- `python` (version **3.11.0** or higher) - https://www.python.org/downloads/
- `pip` (usually auto-installed with Python) -
  https://pip.pypa.io/en/stable/installation/
- Basic familiarity with the [terminal or "command line"] on your system

[terminal or "command line"]:
  https://developer.mozilla.org/en-US/docs/Learn/Tools_and_testing/Understanding_client-side_tools/Command_line#welcome_to_the_terminal

## Installation

1. [Clone] this repository (i.e. download the code).

   ```
   git clone https://github.com/nuztalgia/queemoji.git
   ```

2. [Install] the Python package contained in this subdirectory.

   ```
   pip install -e queemoji/scripts
   ```

**Note:** The `-e` flag produces an [editable install]. Any code changes you make
will immediately take effect when you run the program locally.

</details>

[clone]:
  https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository
[install]:
  https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-from-a-local-src-tree
[editable install]:
  https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs

## Usage

Once you've installed this package, you can view its help menu by using this
command from any directory:

```
queemoji
```

<details>
<summary>
If everything was set up correctly, you should see something like this...
<i>(click to expand)</i>
</summary><br>

```
╭──────────────────────────────────────────────────────────────────╮
│                                                  __ __           │
│          .-----.--.--.-----.-----.--------.-----|__|__|          │
│          |  _  |  |  |  -__|  -__|  .  .  |  _  |  |  |          │
│          |__   |_____|_____|_____|__|__|__|_____|  |__|          │
│             |__|    queemoji-scripts 0.1.0    |____|             │
│                                                                  │
│    Various scripts to automate parts of the Queemoji project.    │
│                                                                  │
│  Command                    Description                          │
│  ...                        ...                                  │
╰──────────────────────────────────────────────────────────────────╯
```

</details>

## License

Copyright © 2023 [Nuztalgia]. Released under the [MIT License].

[mit license]: https://github.com/nuztalgia/queemoji/blob/main/scripts/LICENSE
[nuztalgia]: https://github.com/nuztalgia
