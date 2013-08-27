import psycopg2
import logging
import uuid
import datetime

lgr = logging.getLogger(__name__)



CONFD = {'pghost':'127.0.0.1',
'pgdbname' :'dbtest',
'pgpassword' :'repopass',
'pgusername': 'repo',
'pgpoolsize': 5
}



def insert_rows():
    """
    """
    conn = getconn()
    cur = conn.cursor()
    oneuser = str(uuid.uuid4())
    
    SQL = """INSERT INTO cnxacl
    (module_id, user_id, role_type) 
VALUES
(%s,
%s,
'aclrw')"""

    SQL2 = """INSERT INTO cnxmodule (id_, title)
    VALUES
    (%s, 'test');"""
    

    for i in range(10000):
        moduleid = str(uuid.uuid4())
        cur.execute(SQL, [moduleid,
                      oneuser])
        cur.execute(SQL2, [moduleid,])
        
        conn.commit()
        
    cur.close()
    conn.close()


def checkresponsetime():
    SQL = """select id_, title from cnxmodule WHERE EXISTS (SELECT 1 FROM cnxacl 
WHERE user_id = %s AND 
module_id = cnxmodule.id_)  """

    conn = getconn()
    cur = conn.cursor()
    userid = 'af3d3bd8-0b40-44ae-a54b-ab921742cc52'
    print datetime.datetime.today()
    cur.execute(SQL, [userid])
    print datetime.datetime.today()
    rs = cur.fetchall()
    print datetime.datetime.today()
    print len(rs)
    
    
    
    
def getconn():
    """returns a connection object based on global confd.


    """
    try:
        conn = psycopg2.connect(host=CONFD['pghost'],
                                database=CONFD['pgdbname'],
                                user=CONFD['pgusername'],
                                password=CONFD['pgpassword'])
    except psycopg2.Error, e:
        lgr.error("Error making pg conn - %s - config was %s" %
                  str(e), CONFD)
        raise e

    return conn

if __name__ == '__main__':
    #insert_rows()
    
    checkresponsetime()
