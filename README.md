# translator

A small command-line translator built on
[deep-translator](https://pypi.org/project/deep-translator/). It translates
text passed on the command line, or `.txt` files, using Google, MyMemory or
Pons.

## Install

Requires Python 3.10+ with the `venv` module.

```sh
./build/install.sh
```

Choose:

- **1) Locally** – creates `venv/` in the repository and installs
  `build/requirements.txt` into it. Run the tool with `./build/translate.sh`.
- **2) System-wide** (uses `sudo`) – creates a venv in
  `/lib/python-venvs/translator-env`, copies `src/` to
  `/usr/local/share/translator/src` and installs the wrapper as
  `/usr/local/bin/translate`.

Remove it again with `./build/uninstall.sh`.

## Usage

```sh
translate "hola mundo" -l en          # or ./build/translate.sh for a local install
translate notes.txt -l german         # writes translated-notes.txt next to the input
translate --provider MyMemory         # change the provider permanently
```

- `-l/--language` accepts a language code or name supported by the provider
  (MyMemory uses region codes such as `es-ES`, or names such as `spanish`).
- `--provider` (alias `--source`) accepts `Google`, `MyMemory` or `Pons`; the
  choice is saved to `$XDG_CONFIG_HOME/translator/config.json`
  (default `~/.config/translator/config.json`).
- Only arguments that name an existing file ending in `.txt` are treated as
  files. Files are read and written as UTF-8 and sent in chunks that fit the
  provider's length limit.
- `-d/--detect-language` is not supported by any of the available providers
  and exits with an error.

Errors are printed to stderr and the command exits non-zero.

## Development

```sh
python3 -m venv venv
venv/bin/pip install -r build/requirements-dev.txt
venv/bin/ruff check .
venv/bin/shellcheck build/*.sh
venv/bin/pytest
venv/bin/pip-audit -r build/requirements.txt --ignore-vuln PYSEC-2022-252
```

The same checks run in GitHub Actions (`.github/workflows/ci.yml`).
