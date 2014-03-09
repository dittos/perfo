# https://pythonhosted.org/setuptools/setuptools.html

from setuptools import setup, find_packages

setup(
    name='perfo',
    version='0.0.1',
    packages=find_packages(),

    install_requires=[
        'Flask>=0.10.1',
        'Flask-SQLAlchemy>=1.0',
        'SQLAlchemy>=0.9.3',
        'shortuuid>=0.4',
    ],
)
