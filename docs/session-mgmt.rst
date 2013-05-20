Session Management
==================

Summary
=======

Session management in the repo has been poor for a long time, and it 
has made testing of the various functionalities more awkward and 
requiring more brain use by developer and test suite than needed.

There is a branch (session-cookie-approach) that hopefully fixes this.

We shall provide sensible, secure session management (to decide if a browser has
previously authenticated) and linked to that flow-control that makes decisions
based on the session management such as presenting a login screen, a
registration screen or whatever we need.


Overview
--------

The session shall be activated after a registered user logs in to the repo (via
openid) and the session will be assigned a UUID, which shall be stored on the
users browser as a cookie, and also cached in a postgres dbase where the users
details will be the value to the UUID key.

Every time the user represents their cookie we shall look up the user details in
the cache, take any appropriate flow-control action (session timed out ?
relogin?) and then store the user details in the request for later use.

Issues such as deleting sessions, retrieving the correct dicts etc are also handled, with some known issues (see below).


Sessions
~~~~~~~~

Please see :mod:`sessioncache` for details.

Authentication flow and sessions.
---------------------------------

Sessions are just a convenient way of allowing a user to signon once only.
The flow of authentication is a little more convulited 

please see :func:`rhaptos2.repo.auth.handle_user_authentication`




Difference between ``session sign on`` and ``Single Sign On``
-------------------------------------------------------------

The ``repo`` manages its own login (openid) and sessions (sessioncache) The user
will sign in once and then be given a sessionid.  We will lookup the user from
the the id as long as the session is valid.

If another service (``transformations``) receives a request from the user how
should we validate the user request - should the session cookie be tested
against the repo session cache locally?

What if the repo calls the transformation serivce to act on behalf of the user
- what should we send from repo to transformations - the sessionid? Another api
token created alongside sseession? Where does the lookup occur.



THere are two main phases

* validate already set-up sessions and proceed correctly

* Create and destroy sessions, existing or none (ie login and out)

Known issues
============

I am not handling the situation of user signing in twice.
I am not handling registraftion (co-ordinate with michael)
I am not setting cookie expires ...
I *am* setting httponly


What is wrong with current setup?
---------------------------------

1. NO session cache, which was to be redis but never came in.  We are storing
   the users OpenID identifier.  This is a massive security hole.

2. reliance on Flask security session implementation.  THere are a number of
   reasons to be disatissfied with this, the first is the secret key is a single
   phrase, in config.

3. No clear migration away from Flask.

4. The awful temptation to put more and more stuff in session cookies for "ease" and "scalbility".

Primarily I am frustrated in testing ACLs, and in creating /resources/ - whoch would be again reliant on a broken session implementation.



What about API Tokens?
----------------------

Did we not discuss these at the Sprint?
Yes.  "Single Sign On" is better decribed as "Once Only Sign On, many systems"
A session is a once-only sign on for a single (local) system.
We shall need to have an alternative API token approach for other systems
taht want to use the same sign on as authentication.  Examples wanted.



Testing issues
--------------

* Creation of a "fake-login-API". During testing *only* (ie a flag set)
  we can visit a API page, and get a valid session cookie for one of a
  number of pre-defined users.
  
  This now exists as ``/autosession``.

  

Why do you not encrypt the session ID in the cookie?
----------------------------------------------------

Mostly because I know bupkiss about encryption.  No really I can do AES with
OpenSSH just fine, but did I do it right? Did I rotate my encryption keys with
each user? Did I use cyclic or block level encryption? Which one is which again?
Am I handing out an oracle? (The last one is yes)

Here is a simple argument - I contend that to correctly and securely encrypt
anything sent client side, when any one client could be an attacker, one should have a salt/key unique to each user.

This simple and reasonable request destroys the main argument for sticking
session details like isAdmin and UserName into a encrypted cookie - that it
simplifies distributed architecture (I can let client connect to any web server,
and I will still have the session state in the cookie, *no need for a database
lookup*)

Well the minute we need to get a unique salt for a user, we are back to database
lookups, and just as frequently as session lookups.

Anyway, enough round the houses, I don't know enough about securing encrypted
services with part of the service under complete control of the attacker, to be
sure I have not screwed it up.  So I wont do it till I do, and even then *all we
should store* is the session ID.


A neat trick
~~~~~~~~~~~~

Sometimes it is desireable to set a cookie in your browser - chrome enables us
to do this as follows:

1. navigate to the domain & path desired (i.e. "/" in most cases)
2. enter ``javascript:document.cookie="name=value"`` in the address bar & return
3. you should then revisit the domain, and hey presto you have a cookie


Thanks to http://blog.nategood.com/quickly-add-and-edit-cookies-in-chrome


