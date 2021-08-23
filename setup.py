from setuptools import find_packages, setup

setup(
    name="django-polaris-custodial",
    description="A Django Polaris extension that adds Custodial Wallet support",
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
