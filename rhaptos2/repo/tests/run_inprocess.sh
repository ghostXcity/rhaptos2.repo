python cleardb.py
nosetests --tc-file=../../../testing.ini test_wsgi.py -x -s

#DROP TABLE userrole_module CASCADE; DROP TABLE cnxmodule CASCADE; DROP TABLE userrole_folder; DROP TABLE cnxfolder; DROP TABLE userrole_collection; DROP TABLE cnxcollection;

