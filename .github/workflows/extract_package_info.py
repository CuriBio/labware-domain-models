# -*- coding: utf-8 -*-
"""A cross-platform way in GitHub workflows to extract package version."""
import inspect
import os
import re
import sys
from typing import Optional
from typing import Pattern

if re != sys:  # need to protect the #nosec comment from being deleted by zimports
    import subprocess  # nosec # B404 security implications are considered

PATH_OF_CURRENT_FILE = os.path.dirname((inspect.stack()[0][1]))

# python3 .github/workflows/extract_package_info.py package_name
# python3 .github/workflows/extract_package_info.py package_version


def _extract_info(regex: Pattern[str]) -> str:
    with open(
        os.path.join(PATH_OF_CURRENT_FILE, os.pardir, os.pardir, "setup.py"), "r"
    ) as in_file:
        content = in_file.read()
        match = re.search(regex, content)
        if match is None:
            raise NotImplementedError("A match in setup.py should always be found.")
        output = match.group(1)
        print(output)  # allow-print
        return output


def package_name() -> str:
    regex = re.compile(r"    name=\"(.+)\"")
    return _extract_info(regex)


def package_version() -> str:
    regex = re.compile(r"    version=\"(.+?)\"")
    return _extract_info(regex)


def pip_install(test_pypi: Optional[bool] = False) -> None:
    args = ["pip", "install", f"{package_name()}=={package_version()}"]
    if test_pypi:
        args.extend(
            [
                "--index-url",
                "https://test.pypi.org/simple/",
                "--extra-index-url",
                "https://pypi.org/simple",
            ]
        )
    print(f"About to run with args: {args}")  # allow-print
    results = subprocess.run(args)  # nosec # B603 shell is false, but input is secure
    if results.returncode != 0:
        sys.exit(results.returncode)


if __name__ == "__main__":
    first_arg = sys.argv[1]
    if first_arg == "package_name":
        package_name()
    elif first_arg == "package_version":
        package_version()
    elif first_arg == "install_from_test_pypi":
        pip_install(test_pypi=True)
    elif first_arg == "install_from_pypi":
        pip_install()
