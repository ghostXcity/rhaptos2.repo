=================================
Documenting JSON flow of repo API
=================================


THe below is the output of restrest.py.
It documents HTTP conversations as they occur through 
the python requestsmodule. 

POST /module/
-------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000
    Content-Length: 826
    Content-Type: application/json


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

    {"body": "<h1>In CONGRESS, July 4, 1776....


POST /module/
-------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000
    Content-Length: 826
    Content-Type: application/json


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

    {"body": "<h1>In CONGRESS, July 4, 1776....


PUT /module/cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000
    Content-Length: 432
    Content-Type: application/json


Body::

    {
        "acl": [
            "cnxuser:00000000-0000-0000-0000-000000000101", 
            "cnxuser:00000000-0000-0000-0000-000000000111"
        ], 
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
    Content-Length: 724


::

    {"body": "<p> Shortened body in test_put...


POST /folder/
-------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000
    Content-Length: 398
    Content-Type: application/json


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

    {"body": [{"mediaType": "application/vnd...


PUT /folder/cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000
    Content-Length: 303
    Content-Type: application/json


Body::

    {
        "acl": [
            "cnxuser:00000000-0000-0000-0000-000000000101", 
            "cnxuser:00000000-0000-0000-0000-000000000111"
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
    Content-Length: 537


::

    {"body": [{"mediaType": "application/vnd...


GET /folder/cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 537
    Access-Control-Allow-Origin: *


::

    {"body": [{"mediaType": "application/vnd...


POST /collection/
-----------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000
    Content-Length: 956
    Content-Type: application/json


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

    {"body": "<ul><li><a href=\"cnxmodule:d3...


PUT /collection/cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7
------------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000
    Content-Length: 739
    Content-Type: application/json


Body::

    {
        "acl": [
            "cnxuser:00000000-0000-0000-0000-000000000101", 
            "cnxuser:00000000-0000-0000-0000-000000000111"
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
    Content-Length: 951


::

    {"body": "<ul><li><a href=\"cnxmodule:d3...


GET /collection/cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7
------------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 951


::

    {"body": "<ul><li><a href=\"cnxmodule:d3...


PUT /module/cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000
    Content-Length: 416
    Content-Type: application/json


Body::

    {
        "acl": [
            "cnxuser:00000000-0000-0000-0000-000000000101", 
            "cnxuser:00000000-0000-0000-0000-000000000111"
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
    Content-Length: 708


::

    {"body": "Declaration test text", "id_":...


GET /folder/cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 537
    Access-Control-Allow-Origin: *


::

    {"body": [{"mediaType": "application/vnd...


GET /workspace/
---------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 433
    Access-Control-Allow-Origin: *
    Access-Control-Allow-Credentials: true


::

    [{"mediaType": "application/vnd.org.cnx....


DELETE /module/cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126
-------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 57


::

    cnxmodule:d3911c28-2a9e-4153-9546-f71d83...


DELETE /collection/cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7
---------------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 61


::

    cnxcollection:be7790d1-9ee4-4b25-be84-30...


DELETE /folder/cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707
-------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 57


::

    cnxfolder:c192bcaf-669a-44c5-b799-96ae00...


POST /module/
-------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000
    Content-Length: 826
    Content-Type: application/json


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

    {"body": "<h1>In CONGRESS, July 4, 1776....


PUT /module/cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000
    Content-Length: 432
    Content-Type: application/json


Body::

    {
        "acl": [
            "cnxuser:00000000-0000-0000-0000-000000000101", 
            "cnxuser:00000000-0000-0000-0000-000000000111"
        ], 
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
    Content-Length: 724


::

    {"body": "<p> Shortened body in test_put...


POST /folder/
-------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000
    Content-Length: 398
    Content-Type: application/json


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

    {"body": [{"mediaType": "application/vnd...


PUT /folder/cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000
    Content-Length: 303
    Content-Type: application/json


Body::

    {
        "acl": [
            "cnxuser:00000000-0000-0000-0000-000000000101", 
            "cnxuser:00000000-0000-0000-0000-000000000111"
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
    Content-Length: 537


::

    {"body": [{"mediaType": "application/vnd...


GET /folder/cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 537
    Access-Control-Allow-Origin: *


::

    {"body": [{"mediaType": "application/vnd...


POST /collection/
-----------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000
    Content-Length: 956
    Content-Type: application/json


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

    {"body": "<ul><li><a href=\"cnxmodule:d3...


PUT /collection/cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7
------------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000
    Content-Length: 739
    Content-Type: application/json


Body::

    {
        "acl": [
            "cnxuser:00000000-0000-0000-0000-000000000101", 
            "cnxuser:00000000-0000-0000-0000-000000000111"
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
    Content-Length: 951


::

    {"body": "<ul><li><a href=\"cnxmodule:d3...


GET /collection/cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7
------------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 951


::

    {"body": "<ul><li><a href=\"cnxmodule:d3...


PUT /module/cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000
    Content-Length: 416
    Content-Type: application/json


Body::

    {
        "acl": [
            "cnxuser:00000000-0000-0000-0000-000000000101", 
            "cnxuser:00000000-0000-0000-0000-000000000111"
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
    Content-Length: 708


::

    {"body": "Declaration test text", "id_":...


GET /folder/cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707
----------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 537
    Access-Control-Allow-Origin: *


::

    {"body": [{"mediaType": "application/vnd...


GET /workspace/
---------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 433
    Access-Control-Allow-Origin: *
    Access-Control-Allow-Credentials: true


::

    [{"mediaType": "application/vnd.org.cnx....


DELETE /module/cnxmodule:d3911c28-2a9e-4153-9546-f71d83e41126
-------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 57


::

    cnxmodule:d3911c28-2a9e-4153-9546-f71d83...


DELETE /collection/cnxcollection:be7790d1-9ee4-4b25-be84-30b7208f5db7
---------------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 61


::

    cnxcollection:be7790d1-9ee4-4b25-be84-30...


DELETE /folder/cnxfolder:c192bcaf-669a-44c5-b799-96ae00ef4707
-------------------------------------------------------------

::

    Cookie: cnxsessionid=00000000-0000-0000-0000-000...
    Host: 127.0.0.1:8000


Response:: 

    Content-Type: application/json; charset=utf-8
    Content-Length: 57


::

    cnxfolder:c192bcaf-669a-44c5-b799-96ae00...


