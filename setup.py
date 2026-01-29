"""
Setup configuration for asInventory package
"""
from setuptools import setup, find_packages
import os

# Read version from __init__.py
with open("__init__.py", "r", encoding="utf-8") as fh:
    for line in fh:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"')
            break

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="asinventory",
    version=version,
    author="UAlbany Archives",
    author_email="",
    description="Manage file-level ArchivesSpace inventories with spreadsheets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/UAlbanyArchives/asInventory",
    packages=find_packages(),
    py_modules=[
        "asDownload",
        "asUpload",
        "asValidate",
        "aspace_helpers",
        "aspace_templates",
        "ua_locations"
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "asdownload=asDownload:main",
            "asupload=asUpload:main",
            "asvalidate=asValidate:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.xlsx", "*.cfg"],
    },
)
