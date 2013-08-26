#!/usr/bin/env python
"""
Build script for yum-autoclean
"""
from setuptools import setup, find_packages

setup (name = "yum-autoclean",
    version = '0.1',
    packages = find_packages(), 
    description = "Yum plugin for cleaning up old packages in cache",
    author = 'Arnel A. Borja',
    author_email = 'kyoushuu@yahoo.com',
    license = 'GPLv2+',
    platforms=["Linux"],

    data_files=[('/usr/lib/yum-plugins/', ['autoclean.py']),
                ('/etc/yum/pluginconf.d/', ['autoclean.conf'])],

    classifiers=['License :: OSI Approved ::  GNU General Public License (GPL)',
                 'Operating System :: Unix',
                 'Programming Language :: Python',
                 ],
)
