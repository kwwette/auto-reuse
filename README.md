# auto-reuse

[pre-commit] hook to add missing copyright information to a Python project. Uses
the [REUSE tool].

It requires [`REUSE.toml`][REUSE.toml] to specify

* which license to apply to files which should have a copyright/licensing header
  added to them, e.g. source files;

* complete copyright/licensing information for files which cannot have a header
  added to the files themselves, e.g. configuration and other files.

The following example `REUSE.toml` licenses source files under the [MIT
License], and configuration/other files under the [Creative Commons Zero v1.0
Universal (CC0-1.0)][CC0-1.0 License]:

```toml
version = 1

[[annotations]]
path = [
    ".gitignore",
    ".pre-commit-config.yaml",
    "pyproject.toml",
]
SPDX-FileCopyrightText = "NONE"
SPDX-License-Identifier = "CC0-1.0"

[[annotations]]
path = [
    "src/**/*.py",
]
SPDX-License-Identifier = "MIT"
```

The hook performs the following actions:

* Add missing copyright/licensing header to files as specified in `REUSE.toml`.

  * Author(s) and year(s) for the copyright line are taken from the Git
    repository history, except if the file has not yet been committed, in which
    case the Git user name and current year are used.

  * The copyright/licensing header comment style is determined from the file
    extension. Styles for custom/unknown extensions may be specified in the
    `[tool.auto-reuse.styles]` section of `pyproject.toml`, e.g.:
    ```toml
    [tool.auto-reuse.styles]
    ".script" = "python"   # .script files use Python-style (`#`) comments
    ```

* Missing license files are downloaded to the `LICENSES/` directory.

* The REUSE tool linter is run to check that all required copyright/licensing
  information is specified.

* The [`project.license` and `project.license-files`][license-and-license-files]
  fields are read from `pyproject.toml`.

* The `project.license` field is parsed as an [SPDX license expression], and is
  checked for any licenses which are missing from the `LICENSES/` directory.

* The `project.license-files` field is set to a list of any license files in the
  `LICENSES/` directory that are referred to in the `project.license` field.

* The top-level `LICENSE` file is set to a copy of the primary license file, as
  referred to in the `project.license` field.

To use the hook, add the following to `.pre-commit-hooks.yaml`:

```
repos:
  - repo: https://github.com/kwwette/auto-reuse.git
    rev: # see repository for latest tag
    hooks:
      - id: auto-reuse
```

[pre-commit]:                   https://pre-commit.com/
[REUSE tool]:                   https://reuse.software/dev/#tool
[REUSE.toml]:                   https://reuse.software/spec-3.3/#reusetoml
[MIT License]:                  https://spdx.org/licenses/MIT.html
[CC0-1.0 License]:              https://spdx.org/licenses/CC0-1.0.html
[license-and-license-files]:    https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license-and-license-files
[SPDX license expression]:      https://packaging.python.org/en/latest/glossary/#term-License-Expression
