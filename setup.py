# -*- coding: utf-8 -*-
import sys
import os
from setuptools import setup

from pip.req import parse_requirements

install_requires = parse_requirements(os.path.join(os.path.split(__file__)[0], "requirements.txt"))
install_requires = [str(ir.req) for ir in install_requires]
package_data = [os.path.join(root[4:], fn) for (root, dirs, files) in list(os.walk("src/data")) for fn in files]
print package_data

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
    #install_requires=install_requires,
    #dependency_links=["https://github.com/hgrecco/pyvisa/archive/master.zip#egg=pyvisa-1.5.dev4"],
    package_data={"tektronix": package_data}
)
