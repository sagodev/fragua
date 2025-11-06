from setuptools import setup, find_packages

setup(
    name="fragua",
    version="0.1.0",
    author="SagoDev",
    description="Fragua ETL Framework",
    packages=find_packages(where=".", include=["fragua", "fragua.*"]),
    python_requires=">=3.10",
    install_requires=[
        "numpy",
        "pandas",
        "pytest",
        "typing_extensions",
    ],
)
