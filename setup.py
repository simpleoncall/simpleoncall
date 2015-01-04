#!/usr/bin/env python

from setuptools import setup, find_packages
import os

from simpleoncall import __version__


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

with open('./requirements.txt') as fp:
    requirements = fp.read()
    requirements = requirements.split('\n')


setup(
    name='simpleoncall',
    version=__version__,
    author='Brett Langdon',
    author_email='brett@blangdon.com',
    packages=find_packages(),
    install_requires=requirements,
    description='Open Source ops on-call scheduling django application',
    long_description=README,
    license='MIT',
    url='https://github.com/simpleoncall/simpleoncall',
    entry_points={
        'console_scripts': [
            'simpleoncall = simpleoncall.runner:main',
        ],
    },
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
    ],
)
