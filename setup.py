#!/usr/bin/env python
#! -*- coding: utf-8 -*-

###
# Copyright (c) Rice University 2012-13
# This software is subject to
# the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
###


""" setup.py - rhaptos2.repo package setup


"""

from setuptools import setup, find_packages
import os, glob

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()



def get_version():
    """ return a version number, or error string.
    
    We are assuming a file version.txt always exists. By convention
    populate that file with output of git describe
    """

    try:
        v = open("version.txt").read().strip()
    except:
        v = "UNABLE_TO_FIND_RELEASE_VERSION_FILE"
    return v



setup(
    name='rhaptos2.repo',
    version=get_version(),
    packages=find_packages(),
    namespace_packages=['rhaptos2'],
    author='See AUTHORS.txt',
    author_email='info@cnx.org',
    url='https://github.com/Connexions/rhaptos2.repo',
    long_description=README,
    license='LICENSE.txt',
    description="New editor / repo / system for cnx.org " \
                "-rhaptos2.readthedocs.org",
    install_requires=[
        "flask >= 0.9",
        "Flask-OpenID==1.0.1",
        ],
    include_package_data=True,
    package_data={'rhaptos2.repo': ['templates/*.*',
                                    'static/*.*',
                                    'tests/*.*'],
                  },
    entry_points = """\
    [console_scripts]
    rhaptos2repo-run = rhaptos2.repo.run:main
    rhaptos2repo-initdb = rhaptos2.repo.run:initialize_database
    rhaptos2repo-showconf = rhaptos2.repo.run:show_conf
    """,
    )
