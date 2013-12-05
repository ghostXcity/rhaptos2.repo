=============
rhaptos2.repo
=============

This is an unpublished (or editable) repository implementation for working
with educational content. This web application allows for the storage
and retrieval of works in progress.

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

To install the application itself::

    python setup.py install

This will install the package and a few application specific
scripts. One of these scripts is used to initialize the database with
the applications schema.
::

    rhaptos2repo-initdb development.ini

This example uses the ``development.ini``, which has been supplied with the
package. If you changed any of the database setup values, you'll also need to
change them in the configuration file.

To run the application use the run script::

    rhaptos2repo-run development.ini





Quick
~~~~~

::

    $ curl -O https://raw.github.com/Connexions/rhaptos2.repo/master/quickdownload.sh
    $ bash quickdownload.sh /tmp/testrepo1 # <- replace with any empty dir you like

.. If you need to make changes to quickdownload.sh, you will need to
   stop the script just before the buildvenv.sh script is run. This is
   a chicken and egg issue.
   After you have stopped the script--by commenting probably--you need
   to swap your local copy of the package in place of the cloned one
   before continuing the script--again, probably through commenting.

You'll need to launch the user server::

    cd /tmp/testrepo1/venvs/vrepo; source bin/activate
    cd /tmp/testrepo1/src/rhaptos2.user; python rhaptos2/user/run.py --config local.ini --port 8001

Then running these below to start the content repository instance::

    cd /tmp/testrepo1/venvs/vrepo;
    rhaptos2repo-run --debug --config=develop.ini














Complete
~~~~~~~~

To install the package mananually, checkout this package,
`rhaptos2.common <https://github.com/connexions/rhaptos2.common>`_,
and
`atc (authoring tools client) <https://github.com/connexions/atc>`_.

::

    git clone https://github.com/connexions/rhaptos2.repo.git
    git clone https://github.com/connexions/rhaptos2.common.git
    git clone https://github.com/connexions/atc.git

The ``atc`` project is a ``node.js`` project that will need installed
using ``npm`` as follows ::

    cd atc
    npm install .

(For more information and detailed instructions see the
`ATC project's readme file <https://github.com/connexions/atc>`_.)

Install these development packages into your Python environment::

    cd rhatpos2.common
    python setup.py develop
    cd rhaptos2.repo
    python setup.py develop

The installation will have supplied two scripts:

  * ``rhaptos2repo-run`` - a stand-alone server instance that
    can be used to bring up the application without a production
    worthy webserver.
  * ``rhaptos2repo-initdb`` - a script used to initialize the
    database tables.

To install the database schema, setup the database and note the
host, database name, user name and password in the applications
configuration file. (An example configuration file can be found in in
the root of the rhaptos2.repo project as ``develop.ini``.)

::

    [app]
    pghost = localhost
    pgdbname = rhaptos2repo
    pgusername = rhaptos2repo
    pgpassword = rhaptos2repo
    ...

After the database settings have been updated, you can call the
``rhaptos2repo-initdb`` utility to initialize the database. The
following command illustrates its usage. Make sure to swap in your
configuration file in place of the develop.ini mentioned here.

::

    $ rhaptos2repo-initdb --config=develop.ini

You will also need to tell the configuration where the copy of ``atc``
has been installed::

    [app]
    atc_directory = <location you cloned to>

Session Cache specific Issues

You will need to build a table in the postgres backend.  This is 
done as part of ``initdb`` but worth checking.

I would also recommend running tests/cleardb.py as this will populate the
session cache with three dummy accounts that can be claimed through /autosession

Also ensure that user database is up and contains a mapping from your openid
to a valid user uuid.


Usage
-----

For general usage, you can use the stand-alone server
implementation. This requires that you have cloned and configured a
copy of the ``atc`` project (see the install instructions for more
information). You will need to supply the command with a configuration
file. An example configuration file can be found in the root of this
project as the file named ``develop.ini``.

::

   rhaptos2repo-run --debug --config=develop.ini --port=8000
   * Running on http://127.0.0.1:8000/

A development version is also written, here there is at least one extra 
wsgi piece of middleware that will statically serve javascript etc.
This is expected to be the function of nginx in production, and is there
merely as a convenice for developers.

::

    $ python run.py --config=../../testing.ini --devserver --jslocation=/usr/home/pbrian/deploy/demo1/src/atc



Deployment
----------

This is designed to be deployed into environments as follows::

   cd ~/src  
   git clone https://github.com/Connexions/bamboo.recipies.git

   cd ~/venvs/dev
   . bin/activate
   (dev) cd ~/src/bamboo.scaffold/bamboo/scaffold/scripts/
   (dev) . ./repo_config.sh && python controller.py --recipie rhaptos2repo stage build test deploy

The above will stage (move files, apply patches), build, create a
venv, run unit tests, and deploy into the web servers set in config,
using sshkeys set in config etc.

Third Party code
----------------

We rely on third party code.  
Eventually we shall pull all dependancies out into a stageing process.
For now pretty much all dependnacies (ie bootstrap.css) is in the static folder of Flask.  However, we are developing in parallel with Aloha, 
so we track the cnx-master branch of that - to do so clone Aloha into
a directory and point Flask at it (Flask will serve that cloned dir from 
localhost) ::

  In local.ini set: rhaptos2repo_aloha_staging_dir=/my/path
  cd /my/path
  git clone https://github.com/wysiwhat/Aloha-Editor.git
  git checkout cnx-master



running Tests
-------------

Functional tests have been written in runtests.py and 
are able to both run as tests of the output of an inprocess wsgi app 
(ie we call the app callable with our made up environ and start_repsonse)
It is also able to "reverse the flow through the gate" and generate HTTP 
requests which are pushed against a live server


$ nosetests --tc-file=../../testing.ini runtests.py

$ python run.py --config=../../testing.ini --host=0.0.0.0 --port=8000
$ nosetests --tc-file=../../testing.ini --tc=HTTPPROXY:http://localhost:8000

`run_inprocess.sh` and `run_http.sh` run the nose tests against inprocess wsgi server (ie all HTTP calls are passed between paste.WebTest and the app, and run_http.sh which expects a running HTTP server on port specified in sh file.


License
-------

This software is subject to the provisions of the GNU Affero General Public License Version 3.0 (AGPL). See license.txt for details. Copyright (c) 2012 Rice University

