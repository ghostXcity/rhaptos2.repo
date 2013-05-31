======
Config
======

After the great configuration debates I am reluctant to touch this too
much but nosetests has rather forced our hands.

noestests is a useful piece of kit but has one major problem - its
really awkward to pass configuration *into* to test.  Doug Hellman has
a generally accepted soklution - nose-testconfig.

THis effectively takes the config file given on command line and
parses it into a python dict and presents it as a variable named
"config"::

    from testconfig import config
    main_server = config['foo']['bar']

The current Configuration setup uses the convention of moving all keys
under the [app] section into the top level of the dict and then
everything else lives under "globals".  It returns a Mapping object
that acts like a dict.  Pretty quickly this is read off into the
app.config object which also acts like a dict.

To satisfy this I muck around with nosetest ini file I find this
unsatisfaotry but survieable for now - ultimately I think just
producing a dict out of a ini file and being done with it will work.
God knows how I drove to a different conclusion at any time.

Ultimately its pretty hacky so there may wel lbe a break somewhere
down the line.

Future notes
------------

nose-testconfig supports YAML and python files so is not particularly
limiting, and we can change this again - I did not particularly want
to as it seemed churlish rehashing old stuff but its become a RRPIA.




