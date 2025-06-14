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
  Author(s) and year(s) for the copyright line are taken from the Git repository
  history, except if the file has not yet been committed, in which case the Git
  user name and current year are used.

* Missing license files are downloaded to the `LICENSES/` directory.

* The REUSE tool linter is run to check that all required copyright/licensing
  information is specified.

* `pyproject.toml` is read, and the `project.license` field is parsed as an
  [SPDX license expression].

* `project.license` is checked for any licenses which are missing from the
  `LICENSES/` directory.

* The `project.license-files` field is set to the list of license files in the
  `LICENSES/` directory.

* The top-level `LICENSE` file is set to a copy of the primary license file
  defined in `project.license`.

To use the hook, add the following to `.pre-commit-hooks.yaml`:

```
repos:
  - repo: https://github.com/kwwette/auto-reuse.git
    rev: v0.2
    hooks:
      - id: auto-reuse
```

[pre-commit]:                   https://pre-commit.com/
[REUSE tool]:                   https://reuse.software/dev/#tool
[REUSE.toml]:                   https://reuse.software/spec-3.3/#reusetoml
[MIT License]:                  https://spdx.org/licenses/MIT.html
[CC0-1.0 License]:              https://spdx.org/licenses/CC0-1.0.html
[SPDX license expression]:      https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license-and-license-files
