# -*- coding: utf-8 -*-
import sys
from setuptools import setup
from pip.req import parse_requirements

install_requires = parse_requirements("requirements.txt")
install_requires = [str(ir.req) for ir in install_requires]

setup(
    name="tektronix", 
    version='0.1',
    author='Giles Hall', 
    author_email="giles@polymerase.org",
    url='https://github.com/vishnubob/tektronix',
    description='Interface to Tektronix Scope',
    keywords=['Tektronix', 'scope', 'Data Acquisition'],
    requires=['pyvisa'],
    package_dir={"tektronix": "src"},
    packages=["tektronix"],
    install_requires=install_requires,
)
