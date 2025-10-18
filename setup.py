from setuptools import setup, find_packages

setup(
    name="fragua",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "pytest",
        "typing_extensions",
    ],
)
