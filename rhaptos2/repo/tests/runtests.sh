
### Run the wsgi based, webTest based functional tests that verify
### the API is working ok.

case "$1" in
          wsgi)
            nosetests --tc-file=../../../testing.ini test_wsgi.py -x -s
          ;;
          
          localhost)
            nosetests --tc-file=../../../testing.ini -x --tc=HTTPPROXY:http://localhost:8000 test_wsgi.py
          ;;

          fillet)
           nosetests --tc-file=../../../testing.ini -x --tc=HTTPPROXY:http://beta.cnx.org test_wsgi.py
          ;;

          *)
          echo "useage: runtests.sh wsgi|localhost|fillet"
          exit 1

esac


#DROP TABLE userrole_module CASCADE; DROP TABLE cnxmodule CASCADE; DROP TABLE userrole_folder; DROP TABLE cnxfolder; DROP TABLE userrole_collection; DROP TABLE cnxcollection;
