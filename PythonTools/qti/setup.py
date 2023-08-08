from setuptools import setup, find_packages

setup(
    name="dp_qti",
    version="0.1",
    packages=find_packages(),
    description="A package combining modules for generating QTI-formatted chemistry question banks",
    author="Demetrios Pagonis",
    author_email="demetriospagonis@weber.edu",
    install_requires=[
        'numpy',
        'pandas',
        'jinja2',
        'scipy',
        'lxml'
    ],

)
