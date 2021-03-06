#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except:
    from distutils.core import setup

import re, os

def find_packages(path='.'):
    ret = []
    for root, dirs, files in os.walk(path):
        if '__init__.py' in files:
            ret.append(re.sub('^[^A-z0-9_]+', '', root.replace('/', '.')))
    return ret

setup(
    name='da_server',
    version='0.0.1',
    description='DevAssistant Server',
    long_description=''.join(open('README.rst').readlines()),
    keywords='development',
    author='Tomas Radej, Miro Hroncok',
    author_email='tradej@redhat.com, mhroncok@redhat.com',
    license='GPLv2+',
    packages=find_packages(),
    install_requires=['devassistant>=0.12.0a1'],
    entry_points={'console_scripts': ['da-server=da_server:run']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        ]
)
