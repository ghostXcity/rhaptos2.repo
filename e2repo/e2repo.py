from flask import Flask, request,  url_for
import datetime
import reflector
import datetime
import md5, random
import os
import flask
import statsd

from frozone import conf

app = Flask(__name__)


from logging import FileHandler
fh = FileHandler(filename=os.path.join(conf.remote_e2repo, 'e2repo.log'))
app.logger.addHandler(fh)


def getfilehash(moduletxt):
    '''from a html5 string get some sort of hash '''
    h = random.randint(1,1000)
    return h

def callstatsd(dottedcounter):
    ''' '''
    c = statsd.StatsClient(conf.statsd_host, conf.statsd_port)
    c.incr(dottedcounter)
    #todo: really return c and keep elsewhere for efficieny I suspect

def qlog(msg):
    d = datetime.datetime.today().isoformat()
    fo = open('/tmp/e2repo.log','a')
    fo.write('%s %s \n' % (d, msg))
    fo.close()


def asjson(pyobj):
    '''just placeholder '''
    return 'JSON:: %s' % repr(pyobj)

def gettime():
    return datetime.datetime.today().isoformat()

@app.route("/module/", methods=['POST'])
def modulePOST():
    qlog('postcall here')
    app.logger.info('test')
    callstatsd('frozone.e2repo.POST')
    try:

        html5 = request.form['moduletxt']
        myhash = getfilehash(html5)
        open(os.path.join(REPO, str(myhash)),'w').write(html5)

    except Exception, e:
        qlog(str(e))
        raise(e)

    s = asjson(myhash)
    resp = flask.make_response(s)    
    resp.headers["Access-Control-Allow-Origin"]= "*"
    return resp

  

@app.route("/module/<mhash>", methods=['GET'])
def moduleGET(mhash):
    qlog('getcall %s' % mhash)
    try:
        html5 = open(os.path.join(REPO, str(mhash))).read()
    except Exception, e:
        raise e

    s = asjson(html5)
    resp = flask.make_response(s)    
    resp.headers["Access-Control-Allow-Origin"]= "*"
    return resp

@app.route("/module/", methods=['DELETE'])
def moduleDELETE():
    return 'You DELETEed @ %s' %  gettime() 

@app.route("/module/", methods=['PUT'])
def modulePUT():
    return 'You PUTed @ %s' %  gettime() 


if __name__ == "__main__":
    #app.debug = True
  
    from logging import FileHandler
    fh = FileHandler(filename='/tmp/myapp.log')
    app.logger.addHandler(fh)
    app.run(host='0.0.0.0', debug=True)
