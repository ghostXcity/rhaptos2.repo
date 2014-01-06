# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
import os
from setuptools import setup, find_packages
from setuptools.command.test import test as SetuptoolsTest

class Rhaptos2RepoTest(SetuptoolsTest):

    user_options = SetuptoolsTest.user_options + [
            ('test-type=', None, 'test using wsgi, localhost or fillet (beta.cnx.org)'),
            ]

    def initialize_options(self):
        SetuptoolsTest.initialize_options(self)
        self.test_type = None

    def run_tests(self):
        import os
        import sys
        import subprocess

        # Update PYTHONPATH to include tests_require eggs that are installed
        # locally in the project directory
        environ = os.environ.copy()
        # sys.path contains all packages we need to run the tests, set by
        # setuptools.command.test
        environ['PYTHONPATH'] = ':'.join(sys.path)

        from rhaptos2.repo import tests
        cmd = ['nosetests', '--tc-file=testing.ini', '-x',
               os.path.join(os.path.dirname(tests.__file__), 'test_wsgi.py')]

        if self.test_type == 'localhost':
            cmd += ['--tc=HTTPPROXY:http://localhost:8000']
        elif self.test_type == 'fillet':
            cmd += ['--tc=HTTPPROXY:http://beta.cnx.org']
        else:
            cmd += ['-s']
        print cmd

        errno = subprocess.call(cmd, env=environ)
        raise SystemExit(errno)

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
        "psycopg2",
        "requests",
        "sqlalchemy",
        "webob",
        ],
    tests_require=(
        "nose",
        "nose-testconfig",
        "webtest",
        "WSGIProxy",
        ),
    test_suite='rhaptos2.repo',
    cmdclass = {
        'test': Rhaptos2RepoTest,
        },
    include_package_data=True,
    package_data={'rhaptos2.repo': ['templates/*.*',
                                    'tests/*.*'],
                  },
    entry_points = """\
    [console_scripts]
    rhaptos2repo-initdb = rhaptos2.repo.run:initialize_database
    [paste.app_factory]
    main = rhaptos2.repo.run:paste_app_factory
    """,
    )
