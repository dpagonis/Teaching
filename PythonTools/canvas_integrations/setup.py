from setuptools import setup, find_packages

setup(
    name="dp_canvas",
    version="0.1",
    packages=find_packages(),
    description="A package for ",
    author="Demetrios Pagonis",
    author_email="demetriospagonis@weber.edu",
    install_requires=[
        'pandas',
        'thefuzz',
        'requests'
    ],

)
