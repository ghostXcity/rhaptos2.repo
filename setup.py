# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

setup(
    name='rhaptos2.repo',
    version='0.1',
    author='Connexions team',
    author_email='info@cnx.org',
    long_description=README,
    license='LGPL, See also LICENSE.txt',
    url='https://github.com/Connexions/rhaptos2.repo',
    namespace_packages=['rhaptos2'],
    packages=find_packages(),
    description="Connexions unpublished repository",
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
    rhaptos2repo-initdb = rhaptos2.repo.run:initialize_database
    [paste.app_factory]
    main = rhaptos2.repo.run:paste_app_factory
    """,
    )
