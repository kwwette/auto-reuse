# SPDX-FileCopyrightText: 2025 Karl Wette
#
# SPDX-License-Identifier: MIT

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from subprocess import DEVNULL, PIPE, CalledProcessError, run

import tomlkit
from license_expression import Licensing

__author__ = "Karl Wette"


class NoAuthorError(Exception):
    pass


class NoLicenseError(Exception):
    pass


class UnusedLicenseError(Exception):
    pass


class MissingLicenseFileError(Exception):
    pass


def git_log_author_year(file_path):

    # Get Git authors of a file and years of commits
    out = run(
        ["git", "log", "--follow", "--pretty=format:%as-%aN", str(file_path)],
        check=True,
        stdout=PIPE,
        encoding="utf-8",
    )
    authors_years = {}
    for line in out.stdout.splitlines():
        year, _, _, author = line.split("-", maxsplit=3)
        if author not in authors_years:
            authors_years[author] = set()
        authors_years[author].add(int(year))

    return authors_years


def run_reuse_annotate(cmd, **kwargs):

    # Run reuse, print help if it fails
    cmd_base = ["reuse", "annotate"]
    try:
        run(cmd_base + cmd, **kwargs)
    except CalledProcessError as e:
        run(cmd_base + ["--help"], check=False)
        raise e


def reuse_annotate_add_licenses(file_path, licenses):

    # Check for any license
    if not licenses:
        msg = f"no license specified in REUSE.toml for {file_path}"
        raise NoLicenseError(msg)

    # Add license information to file
    cmd = []
    for lic in licenses:
        cmd.extend(["--license", lic])
    cmd.append(file_path)
    run_reuse_annotate(cmd, check=True, stdout=DEVNULL)


def reuse_annotate_add_authors(file_path, authors_years):

    # Add copyright to authors with given years
    for author, years in authors_years.items():
        cmd = [
            "--merge-copyrights",
            "--copyright",
            author,
        ]
        min_year = min(years)
        max_year = max(years)
        cmd.extend(["--year", str(min_year)])
        if min_year < max_year:
            cmd.extend(["--year", str(max_year)])
        cmd.append(file_path)
        run_reuse_annotate(cmd, check=True, stdout=DEVNULL)


def cli():

    # Set column width for reuse annotate --help
    os.environ["COLUMNS"] = "80"

    # For uncommitted files, use Git user as author (if available) and current date as year
    out = run(
        ["git", "config", "user.name"],
        stdout=PIPE,
        encoding="utf-8",
    )
    git_user = out.stdout.strip()
    current_year = datetime.now().year

    # Run reuse lint and parse JSON report
    out = run(["reuse", "lint", "--json"], stdout=PIPE, encoding="utf-8")
    report = json.loads(out.stdout)

    # Run through files to find missing copyright information
    all_licenses = set()
    for file in report["files"]:

        # Save list of all licenses
        licenses = [s["value"] for s in file["spdx_expressions"]]
        all_licenses.update(licenses)

        if not file["copyrights"]:

            # Add license information
            reuse_annotate_add_licenses(file["path"], licenses)

            # Add copyright to Git authors with years of commits
            authors_years = git_log_author_year(file["path"])
            if not authors_years:

                # Use Git user as author (if available)
                if git_user == "":

                    # No author available, give up
                    msg = f"copyright author missing from {file['path']}"
                    raise NoAuthorError(msg)

                authors_years = {git_user: [current_year]}

            reuse_annotate_add_authors(file["path"], authors_years)

    # Download missing licenses
    run(["reuse", "download", "--all"], check=True)

    # Run reuse linter
    run(["reuse", "lint"], check=True)

    # Read pyproject.toml
    pyproject_toml_path = Path("pyproject.toml")
    with pyproject_toml_path.open("rt") as f:
        pyproject_toml = tomlkit.load(f)

    # Check license consistency with pyproject.toml
    licensing = Licensing()
    pyproject_license_expression = pyproject_toml["project"]["license"]
    pyproject_licenses = licensing.license_keys(
        pyproject_license_expression, unique=True
    )
    for lic in pyproject_licenses:
        if lic not in all_licenses:
            msg = f"license {lic} appears in pyproject.toml but is not used to license any file"
            raise UnusedLicenseError(msg)

    # Duplicate primary license to top-level LICENSE file
    top_level_license = Path("LICENSE")
    pyproject_primary_license = licensing.primary_license_key(
        pyproject_license_expression
    )
    pyproject_primary_license_file = (
        Path("LICENSES") / f"{pyproject_primary_license}.txt"
    )
    if not pyproject_primary_license_file.is_file():
        msg = f"license {pyproject_primary_license} appears in pyproject.toml but {pyproject_primary_license_file} does not exist"
        raise MissingLicenseFileError(msg)
    shutil.copy(pyproject_primary_license_file, top_level_license)

    # Reference all required licenses in pyproject.toml
    pyproject_license_files = []
    for lic in pyproject_licenses:
        pyproject_license_file = Path("LICENSES") / f"{lic}.txt"
        if not pyproject_license_file.is_file():
            msg = f"license {lic} appears in pyproject.toml but {pyproject_license_file} does not exist"
            raise MissingLicenseFileError(msg)
        pyproject_license_files.append(pyproject_license_file)

    # Write license files to pyproject.toml
    pyproject_toml["project"]["license-files"] = [
        str(p) for p in pyproject_license_files
    ]
    pyproject_toml_tmp_path = pyproject_toml_path.with_suffix(".toml.tmp")
    with pyproject_toml_tmp_path.open("wt") as f:
        tomlkit.dump(pyproject_toml, f)
    pyproject_toml_tmp_path.replace(pyproject_toml_path)
