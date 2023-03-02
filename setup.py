import sys

from setuptools import setup

PACKAGE_NAME = "yacman"

# Ordinary dependencies
DEPENDENCIES = []
with open("requirements/requirements-all.txt", "r") as reqs_file:
    for line in reqs_file:
        if not line.strip():
            continue
        # DEPENDENCIES.append(line.split("=")[0].rstrip("<>"))
        DEPENDENCIES.append(line)

# Additional keyword arguments for setup().
extra = {}
extra["install_requires"] = DEPENDENCIES

with open("yacman/_version.py", "r") as versionfile:
    version = versionfile.readline().split()[-1].strip("\"'\n")

# Handle the pypi README formatting.
try:
    import pypandoc

    long_description = pypandoc.convert_file("README.md", "rst")
except (IOError, ImportError, OSError):
    print("Warning -- couldn't convert README to rst")
    long_description = open("README.md").read()

setup(
    name=PACKAGE_NAME,
    packages=[PACKAGE_NAME],
    version=version,
    description="A standardized configuration object for reference genome assemblies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    license="BSD2",
    keywords="bioinformatics, sequencing, ngs",
    url="https://github.com/databio/yacman",
    author="Nathan Sheffield, Michal Stolarczyk",
    author_email="nathan@code.databio.org",
    **extra
)
