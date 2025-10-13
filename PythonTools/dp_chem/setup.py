from setuptools import setup, find_packages

setup(
    name="dp_chem",
    version="1.0",
    packages=find_packages(),
    description="A package for handling chemistry concepts and data",
    author="Demetrios Pagonis",
    author_email="demetriospagonis@weber.edu",
    install_requires=[
        'numpy',
        'pandas',
        'jinja2',
        'scipy',
        'matplotlib',
        'xarray',
        'requests',
        'cartopy',
        'shapely',
        'geopandas',
        'zipfile',
    ],
)