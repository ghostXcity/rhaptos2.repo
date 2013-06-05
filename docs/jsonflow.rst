=================================
Documenting JSON flow of repo API
=================================


THe below is the output of restrest.py.
It documents HTTP conversations as they occur through 
the python requestsmodule. 

POST /module/
-------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000000
    Host: 127.0.0.1:8000
    Content-Length: 826
    Content-Type: application/json; charset=utf-8


Body::

    {
        "authors": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "body": "<h1>In CONGRESS, July 4, 1776.</h1>\n<p>The unanimous Declaration ...
        "copyrightHolders": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "id_": "cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126", 
        "maintainers": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "title": "Introduction"
    }


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 1131


::

    {"body": "<h1>In CONGRESS, July 4, 1776.</h1>\n<p>The u...


PUT /module/cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126
----------------------------------------------------------

NB - we are using session 000 for the initial PUT

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000000
    Host: 127.0.0.1:8000
    Content-Length: 384
    Content-Type: application/json; charset=utf-8


Body::

    {
        "acl": [
            "cnxuser:75e06194-baee-4395-8e1a-566b656f6921"
        ], 

            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            This is the useruri for a registered user, (ross)
            who we happen to know has a sessionID of 0001

        "authors": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "body": "<p> Shortened body in test_put_module", 
        "copyrightHolders": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "id_": "cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126", 
        "maintainers": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "title": "Introduction"
    }


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 676


::

    {"body": "<p> Shortened body in test_put_module", "id_"...


PUT /module/cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126
----------------------------------------------------------

Here we are using a different user, 001 (ross) that 
we added as a ACL in previous PUT.

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000001
    Host: 127.0.0.1:8000
    Content-Length: 382
    Content-Type: application/json; charset=utf-8


Body::

    {
        "acl": [
            "cnxuser:75e06194-baee-4395-8e1a-566b656f6921"
        ], 
        "authors": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "body": "<p> OTHERUSERSESSIONID has set this", 
        "copyrightHolders": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "id_": "cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126", 
        "maintainers": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "title": "Introduction"
    }


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 674


::

    {"body": "<p> OTHERUSERSESSIONID has set this", "id_": ...


POST /folder/
-------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000000
    Host: 127.0.0.1:8000
    Content-Length: 398
    Content-Type: application/json; charset=utf-8


Body::

    {
        "body": [
            "cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126", 
            "cnxmodule:350f7859-e6e7-11e1-928f-2c768ae4951b", 
            "cnxmodule:4ba18842-1bf8-485b-a6c3-f6e15dd762f6", 
            "cnxmodule:77a45e48-6e91-4814-9cca-0f28348a4aae", 
            "cnxmodule:e0c3cfeb-f2f2-41a0-8c3b-665d79b09389", 
            "cnxmodule:c0b149ec-8dd3-4978-9913-ac87c2770de8"
        ], 
        "id_": "cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707", 
        "title": "Declaration Folder"
    }


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 445


::

    {"body": [{"mediaType": "application/vnd.org.cnx.module...


PUT /folder/cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000000
    Host: 127.0.0.1:8000
    Content-Length: 247
    Content-Type: application/json; charset=utf-8


Body::

    {
        "acl": [
            "00000000-0000-0000-0000-000000000001"
        ], 
        "body": [
            "cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126", 
            "cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41127"
        ], 
        "id_": "cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707", 
        "title": "Declaration Folder"
    }


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 481


::

    {"body": [{"mediaType": "application/vnd.org.cnx.module...


GET /folder/cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000000
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 481
    Access-Control-Allow-Origin: *


::

    {"body": [{"mediaType": "application/vnd.org.cnx.module...


POST /collection/
-----------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000000
    Host: 127.0.0.1:8000
    Content-Length: 956
    Content-Type: application/json; charset=utf-8


Body::

    {
        "authors": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "body": "<ul><li><a href=\"cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126\"...
        "copyrightHolders": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "id_": "cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7", 
        "keywords": [
            "Life", 
            "Liberty", 
            "Happiness"
        ], 
        "language": "en", 
        "maintainers": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "subType": "Other Report", 
        "subjects": [
            "Social Sciences"
        ], 
        "summary": "No.", 
        "title": "United States Declaration Of Independance"
    }


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 1181


::

    {"body": "<ul><li><a href=\"cnxmodule:d3911c28-2a9e-415...


PUT /collection/cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7
------------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000000
    Host: 127.0.0.1:8000
    Content-Length: 683
    Content-Type: application/json; charset=utf-8


Body::

    {
        "acl": [
            "00000000-0000-0000-0000-000000000001"
        ], 
        "authors": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "body": "<ul><li><a href=\"cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126\"...
        "copyrightHolders": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "id_": "cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7", 
        "keywords": [
            "Life", 
            "Liberty", 
            "Happiness"
        ], 
        "language": "en", 
        "maintainers": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "subType": "Other Report", 
        "subjects": [
            "Social Sciences"
        ], 
        "summary": "No.", 
        "title": "United States Declaration Of Independance"
    }


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 895


::

    {"body": "<ul><li><a href=\"cnxmodule:d3911c28-2a9e-415...


GET /collection/cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7
------------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000000
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 895


::

    {"body": "<ul><li><a href=\"cnxmodule:d3911c28-2a9e-415...


PUT /collection/cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7
------------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000002
    Host: 127.0.0.1:8000
    Content-Length: 494
    Content-Type: application/json; charset=utf-8


Body::

    {
        "authors": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "body": [
            "cnxmodule:SHOULDNEVERHITDB0"
        ], 
        "copyrightHolders": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "id_": "cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7", 
        "keywords": [
            "Life", 
            "Liberty", 
            "Happiness"
        ], 
        "language": "en", 
        "maintainers": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "subType": "Other Report", 
        "subjects": [
            "Social Sciences"
        ], 
        "summary": "No.", 
        "title": "United States Declaration Of Independance"
    }


Response:: 

    Content-Type: text/html
    Content-Length: 227


::

    null


PUT /module/cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000000
    Host: 127.0.0.1:8000
    Content-Length: 368
    Content-Type: application/json; charset=utf-8


Body::

    {
        "acl": [
            "cnxuser:75e06194-baee-4395-8e1a-566b656f6921"
        ], 
        "authors": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "body": "Declaration test text", 
        "copyrightHolders": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "id_": "cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126", 
        "maintainers": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "title": "Introduction"
    }


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 660


::

    {"body": "Declaration test text", "id_": "cnxmodule:d39...


PUT /module/cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000002
    Host: 127.0.0.1:8000
    Content-Length: 359
    Content-Type: application/json; charset=utf-8


Body::

    {
        "acl": [
            "cnxuser:75e06194-baee-4395-8e1a-566b656f6921"
        ], 
        "authors": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "body": "NEVER HIT DB", 
        "copyrightHolders": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "id_": "cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126", 
        "maintainers": [
            "cnxuser:f9647df6-cc6e-4885-9b53-254aa55a3383"
        ], 
        "title": "Introduction"
    }


Response:: 

    Content-Type: text/html
    Content-Length: 223


::

    null


PUT /folder/cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000002
    Host: 127.0.0.1:8000
    Content-Length: 163
    Content-Type: application/json; charset=utf-8


Body::

    {
        "acl": [
            "00000000-0000-0000-0000-000000000001"
        ], 
        "body": [
            "THIS IS TEST"
        ], 
        "id_": "cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707", 
        "title": "Declaration Folder"
    }


Response:: 

    Content-Type: text/html
    Content-Length: 223


::

    null


GET /module/cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000001
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 660


::

    {"body": "Declaration test text", "id_": "cnxmodule:d39...


GET /folder/cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000000
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 481
    Access-Control-Allow-Origin: *


::

    {"body": [{"mediaType": "application/vnd.org.cnx.module...


GET /module/cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000002
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: text/html
    Content-Length: 223


::

    null


GET /workspace/
---------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000000
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 433
    Access-Control-Allow-Origin: *
    Access-Control-Allow-Credentials: true


::

    [{"mediaType": "application/vnd.org.cnx.module", "id": ...


DELETE /module/cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126
-------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000002
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: text/html
    Content-Length: 223


::

    null


DELETE /module/cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126
-------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000000
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 57


::

    cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126 is no mo...


DELETE /collection/cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7
---------------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000002
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: text/html
    Content-Length: 227


::

    null


DELETE /collection/cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7
---------------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000000
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 61


::

    cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7 is n...


DELETE /folder/cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707
-------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000002
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: text/html
    Content-Length: 223


::

    null


DELETE /folder/cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707
-------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000000000000
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 57


::

    cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707 is no mo...


