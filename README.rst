=============
rhaptos2.repo
=============

This is an unpublished (or editable) repository implementation for working
with educational content. This web application allows for  the storage,
retrieval and modification of works in progress.

See the `Connexions development documentation
<http://connexions.github.com/>`_ for more information.

Getting started
---------------

This installation procedure attempts to cover two platforms,
the Mac and Debian based systems.
If you are using a platform other these,
attempt to muddle through the instructions,
then feel free to either file an
`issue <https://github.com/Connexions/rhaptos2.repo/issues/new>`_
or contact Connexions for further assistance.

Install the PostgreSQL database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This will require a ``PostgreSQL`` install
that is greater than or equal to version **9.3**.

On a Mac, use the `PostgresApp <http://postgresapp.com/>`_.

On Debian (and Ubuntu), issue the following command::

    apt-get install postgresql-9.3 postgresql-server-dev-9.3 postgresql-client-9.3 postgresql-contrib-9.3 postgresql-plpython-9.3

Verify the install and port by using ``pg_lscluster``. If the 9.3
cluster is not the first one installed (which it likely is not), note
the port and cluster name. For example, the second cluster installed
will end up by default with port 5433, and a cluster named ``main``.

Set the ``PGCLUSTER`` environment variable to make psql and other
postgresql command line tools connect to the appropriate server. For
the example above, use::

    export PGCLUSTER=9.3/main

Set up the database and user
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The default settings
for the database are setup to use the following credentials:

:database-name: rhaptos2repo
:database-user: rhaptos2repo
:database-password: rhaptos2repo

**Note**: Not that it needs to be said, but just in case...
In a production setting, you should change these values.

If you decided to change any of these default values,
please ensure you also change them in the application's configuration file,
which is discussed later in these instructions.

To set up the database, issue the following commands (these will use
the default cluster, as defined above)::

    psql -U postgres -d postgres -c "CREATE USER rhaptos2repo WITH SUPERUSER PASSWORD 'rhaptos2repo';"
    createdb -U postgres -O rhaptos2repo rhaptos2repo

**OSX Note:** You may need to create the ``postgres`` user: ``psql -d postgres -c "CREATE USER postgres WITH SUPERUSER;"``

Installing the application
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Note**: It's recommended that you use a virtual environment to
install this application. The installation and usage of virtualenv
is out of scope for this document, but you can follow the
instructions at `virtualenv.org <http://www.virtualenv.org>`_.

If you are working on a Debian distribution, it is a good idea that
you use the native system packages for some of the dependencies.
::

    apt-get install libxml2-dev
    apt-get install libxslt1-dev
    apt-get install python-psycopg2
Before installing rhaptos2.repo, you need to first install the
dependencies that have not been released to the public package repositories::

    git clone https://github.com/Connexions/rhaptos2.common.git
    cd rhaptos2.common
    python setup.py install
    cd ..

.. (pumazi) I don't think rhaptos2.common is required anymore???

To install the application itself::

    python setup.py install

This will install the package and a few application specific
scripts. One of these scripts is used to initialize the database with
the applications schema.
::

    rhaptos2repo-initdb develop.ini

This example uses the ``develop.ini``, which has been supplied with the
package. If you changed any of the database setup values, you'll also need to
change them in the configuration file.

Usage
~~~~~

**Note**: This should only be used in a development/testing environment.

To run the application in a standalone environment,
use the paster utility with the ``paster-develoment.ini`` paster configuration,
which uses the ``develop.ini`` application configuration.
::

    git clone https://github.com/Connexions/atc.git
    cd atc && npm install && cd ..
    pip install PasteScript PasteDeploy waitress
    paster serve paster-development.ini

The above installs ``atc`` relative to the ``paster-development.ini``.
You wouldn't want to run the application this way in production,
but for a standalone application it does the trick.

**TODO** We will in the future be supplying a wsgi file to allow easy
drop-in on web servers that support the Python WSGI standard.

About the configuration
-----------------------

An example configuration INI file can be found in in
the root of the rhaptos2.repo project as ``develop.ini``.

The application configuration can be found in this file under the ``app``
section. The following illustrates the settings used to connect to
the database.
::

    [app]
    pghost = localhost
    pgdbname = rhaptos2repo
    pgusername = rhaptos2repo
    pgpassword = rhaptos2repo
    ...

Tests
-----

.. image:: https://travis-ci.org/Connexions/rhaptos2.repo.png
   :target: https://travis-ci.org/Connexions/rhaptos2.repo

This is a **work-in-progress**.

Functional tests have been written in test_wsgi.py and 
are able to both run as tests of the output of an inprocess wsgi app 
(ie we call the app callable with our made up environ and start_repsonse)
It is also able to "reverse the flow through the gate" and generate HTTP 
requests which are pushed against a live server

Set up the test database:
::
    createdb -U postgres -O rhaptos2repo rhaptos2repo-testing
    rhaptos2repo-initdb testing.ini

To run the tests using wsgi:
::

    python setup.py test --test-type=wsgi

To run the tests using a local server:
::

    paster serve paster-testing.ini
    python setup.py test --test-type=localhost

To run the tests using beta.cnx.org: (This does not work at the moment)
::

    python setup.py test --test-type=fillet

License
-------

This software is subject to the provisions of
the GNU Affero General Public License Version 3.0 (AGPL).
See license.txt for details. Copyright (c) 2012 Rice University
