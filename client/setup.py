#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup, find_packages

setup(
    name='da_client',
    version='0.0.1',
    description='DevAssistant CLI Client',
    long_description=''.join(open('README.rst').readlines()),
    keywords='development',
    author='Tomas Radej, Miro Hroncok',
    author_email='tradej@redhat.com, mhroncok@redhat.com',
    license='GPLv2+',
    packages=find_packages(),
    install_requires=['devassistant'],
    entry_points={'console_scripts': ['da-cli=da_client:run']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        ]
)
