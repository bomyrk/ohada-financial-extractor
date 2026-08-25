from setuptools import setup, find_packages

setup(
    name="ohada-financial-extractor",
    version="0.1.6",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
