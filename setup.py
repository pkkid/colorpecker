#!/usr/bin/python3
# -*- coding: utf-8 -*-
from colorpicker import VERSION
from pkg_resources import parse_requirements
from setuptools import setup

readme = open('README.md', 'r').read()
with open('requirements.txt') as handle:
    requirements = [str(req) for req in parse_requirements(handle)]

setup(
    name='colorpicker',
    version=VERSION,
    description='Python based color picker written with PySide6 and QT.',
    author='Michael Shepanski',
    author_email='michael.shepanski@gmail.com',
    url='https://github.com/pkkid/python-colorpicker',
    packages=['colorpicker'],
    install_requires=requirements,
    python_requires='>=3.7',
    long_description=readme,
    keywords=['colorpicker', 'color', 'picker', 'hex', 'hsv', 'rgb',
        'rgba', 'eyedropper', 'palette'],
    classifiers=[
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
    ]
)
