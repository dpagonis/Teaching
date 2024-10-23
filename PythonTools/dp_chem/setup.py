from setuptools import setup, find_packages

setup(
    name="dp_chem",
    version="0.1",
    packages=find_packages(),
    description="A package for handling common chemistry concepts, geared towards programmatic generation of question banks",
    author="Demetrios Pagonis",
    author_email="demetriospagonis@weber.edu",
    install_requires=[
        'numpy',
        'pandas',
        'jinja2',
        'scipy'
    ],
)