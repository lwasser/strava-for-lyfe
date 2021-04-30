# A basic setup file to allow someone to install my modules and run in their envt
from setuptools import setup, find_packages

setup(
    name='example',
    version='0.0.1',
    packages=find_packages(include=['process_strava'])
)