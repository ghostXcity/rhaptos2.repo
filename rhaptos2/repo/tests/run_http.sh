python cleardb.py
nosetests --tc-file=../../../testing.ini -x --tc=HTTPPROXY:http://localhost:8000 test_wsgi.py
