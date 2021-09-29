import os.path

import codecs
from setuptools import find_packages, setup


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), "r") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delimiter = '"' if '"' in line else "'"
            return line.split(delimiter)[1]
    raise RuntimeError("Unable to find version string.")


setup(
    name="django-polaris-bitgo",
    description="A Django Polaris extension that adds BitGo's Custodial Wallet support",
    long_description=read("README.md"),
    version=get_version("polaris_bitgo/__init__.py"),
    license="Apache License 2.0",
    include_package_data=True,
    packages=find_packages(exclude=["tests*"]),
    keywords=[
        "stellar",
        "sdf",
        "anchor",
        "server",
        "polaris",
        "sep-24",
        "sep24",
        "sep-31",
        "sep31",
        "bitgo",
        "custodial",
        "wallet",
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=[
        "django-polaris>=1.4.1",
        "pycryptodome==3.10.1",
    ],
    python_requires=">=3.7",
)
