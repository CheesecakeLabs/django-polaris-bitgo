from setuptools import find_packages, setup

with open("README.md", "r") as file:
    long_description = file.read()

setup(
    name="django-polaris-bitgo",
    description="A Django Polaris extension that adds BitGo's Custodial Wallet support",
    long_description=long_description,
    version="0.1.0",
    license="Apache license 2.0",
    include_package_data=True,
    packages=find_packages(),
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
