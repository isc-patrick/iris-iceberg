#!/usr/bin/env python
from setuptools import find_packages
from distutils.core import setup     

setup(name='irisiceberg',
      version='1.0',
      description='IRIS Iceberg library',
      author='Patrick Sulin',
      author_email='psulin@intersystems.com',
      url='',
      package_dir={'':'src', 'tests': 'tests'},
      packages=(find_packages(where="src")+['tests', 'tests.unit', 'tests.fixtures']),
      install_requires= ['pytest>=8.0', 'sqlalchemy-iris==0.12.0' ,'pyarrow==17.0.0', 'pandas==2.2.2',
                        'loguru==0.7.2',
                        'pyiceberg==0.7.1',
                        'pydantic==2.8.2',
                        'pydantic-settings==2.5.0',
                        'pydantic_core==2.20.1',
                        'sqlalchemy>=2.0', 
                        'adlfs==2024.7.0',
                        'pyodbc==5.1.0'],
      entry_points={
        'console_scripts': [
            'irice=irisiceberg.app:main'
        ]}
)