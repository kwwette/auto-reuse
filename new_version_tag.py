"""Create new version tag."""

from pathlib import Path
from subprocess import run

import tomlkit

# Read pyproject.toml
pyproject_toml_path = Path("pyproject.toml")
with pyproject_toml_path.open("rt") as f:
    pyproject_toml = tomlkit.load(f)

# Get tag for current version
version = pyproject_toml["project"]["version"]
tag = "v" + version

# Check if tag exists
out = run(
    ["git", "tag", "-l", tag],
    check=True,
    capture_output=True,
    encoding="utf-8",
)
if out.stdout == "":

    # Create tag
    run(
        ["git", "tag", "-a", "-m", f"Version {version}", tag],
        check=True,
        capture_output=True,
        encoding="utf-8",
    )
