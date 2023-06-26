# -----------------------
# Copyright(c)
# The contents of this file are automatically generated using a code-generator.
# Any changes to this file shall get over-writen upon next re-geneation
# Date: {{datetime}}
# Author: {{os.USER.upper()}}
# ---------------------------
import os
import argparse
import base64, json
import logging
import datetime, time,  os, sys, shutil
import cherrypy as HttpServer
import inspect
from pymongo import MongoClient

class Webserver(object):
    '''
    classdocs
    '''

    staticdir = None
    starttime = None



    def __init__(self, staticdir=None, dbhost=None):
        '''
        Constructor
        '''
        self.staticdir = os.path.join(os.getcwd(), 'ui_www')
        if staticdir:
            self.staticdir = staticdir

        logging.info("Static directory for web-content: %s" % self.staticdir)

        # Intializing the upload directory
        uploaddir = os.path.join(self.staticdir, '..', 'uploads')
        if uploaddir:
            self.uploaddir = uploaddir

            # DB Port Addresses
            self.dbhost = '127.0.0.1'
            self.dbport = 27017
            if dbhost:
                dbhostarr = dbhost.split(":")
                self.dbhost = dbhostarr[0]
                if dbhostarr[1]:
                    self.dbport = int(dbhostarr[1])
            logging.info("MongoDB Client: {} : {}".format(self.dbhost, self.dbport))
            client = MongoClient(self.dbhost, self.dbport)

            self.dbase = client['{{appname.lower()}}']
            {% for formobj in formobjs -%}
                self.db_{{formobj.name.lower()}} = self.dbase['{{formobj.name.lower()}}']
            {% endfor %}


    @HttpServer.expose
    def index(self):
        """
        Sources the index file
        :return: raw index file
        """
        return open(os.path.join(self.staticdir, "index.html"))



    @HttpServer.expose()
    def status(self):
        robj = {'status' : True}
        return robj

    @HttpServer.expose()
    def apicall1(self, data1, data2, data3):
        print("API Call: {}/{}/{}".format(data1, data2, data3))

   {% for formobj in formobjs %}
    @HttpServer.expose()
    def submit_{{formobj.name.lower()}}(self, data=None):
        """
        Submission API for {{formobj.name}}
        Form shall submit a stringified JSON object with the following fields,
         {% for fld in formobj.fields %} ## {{fld.name}}, Type: {{fld.type}}
         {% endfor %}
        """
        datax = json.loads(data)
        ts = datetime.datetime.now()
        print("{} : {{formobj.name.lower()}} submission, {}".format(ts, data))
        {% if formobj.recordtype != 'authorization' %}
        robj = {'datetime' : {'date' : ts,
                              'day' : ts.day,
                              'month' : ts.month,
                              'year' : ts.year,
                              'minute' : ts.minute,
                              'hour' : ts.hour,
                              'second' : ts.second},
                'status' : True, 'data' : datax}
        {% endif -%}

        {% if formobj.recordtype =='timeseries' %}
        ## Generating timeseries code for {{formobj.name.lower()}}, object would be time-stamped and stored
        res = self.db_{{formobj.name.lower()}}.insert_one(robj)
        {% endif -%}
        {% if formobj.recordtype =='stateful' %}
        ## Generating Stateful code for {{formobj.name.lower()}}, object is updated if it exists others created new
        res = self.db_{{formobj.name.lower()}}.replace_one(filter={'data' : datax},
                                        replacement=robj, upsert=True)

        robj = res
        {% endif -%}
        {% if formobj.recordtype == 'authorization' %}
        ## Generating Authorization code for {{formobj.name.lower()}}, reccord fields are looked up and compared
        ## TableName: {{ formobj.tablename.lower() }}
        query = {
            {% for fld in formobj.fields -%}
                'data.{{fld.name}}': datax['{{fld.name.lower()}}'],
            {% endfor -%}
        }

        authres = self.db_{{formobj.tablename.lower()}}.find_one(query, {'_id': 0})
        robj = {'authorization' : False}
        if authres:
            robj = {'authorization' : True}

        robj['timestamp'] = ts

        {% endif -%}

        return json.dumps(robj, default=self.datetimencoder)

    {% endfor -%}

    {% for formobj in formobjs %}
    {% if formobj.recordtype == 'timeseries' %}
    @HttpServer.expose()
    def qtable_{{formobj.name}}(self, last=10):
        """
        Returns records which match datime.date > last criterion
        last 10, implies return everything in the last 10 days
        This data is a timeseries data from database table {{formobj.name.lower()}}
        """
        rightnow = datetime.datetime.now()
        otimestamp = datetime.timedelta(days=last)
        recds = list(self.db_{{formobj.name}}.find({'datetime.date' : {'$gt' : otimestamp}}, {'_id' : 0}))

        return json.dumps(recds, default=self.datetimencoder)
    {% endif %}
    {% endfor %}





    def datetimencoder(self, o):
        """
        Converts Datatime object to string
        :param self:
        :param o:
        :return:
        """
        if isinstance(o, datetime.datetime):
            return o.__str__()

    @HttpServer.expose()
    def getjs(self):
        rstr = 'js'
        membrs = inspect.getmembers(self)
        for mem in membrs:
            #print(mem[0])
            #print(inspect.getmembers(self, ))
            #print(inspect.ismethod((mem[1])))
            if inspect.ismethod(mem[1]):
                print("{}".format(mem[0]))
                #print("{} ".format(type(inspect.signature(mem[1]) )) )
                for par in inspect.signature(mem[1]).parameters:
                    print("\t==>{}".format(par))

                print(inspect.get_annotations(mem[1]))


        return rstr





# main code section
if __name__ == '__main__':
        portmum = 9005
        www = os.path.join(os.getcwd(), 'ui_www')
        ipaddr = '127.0.0.1'

        dbip = '127.0.0.1:27017'

        logpath = os.path.join(os.getcwd(), 'log', '{{appname.lower()}}-server.log')
        logdir = os.path.dirname(logpath)
        os.makedirs(logdir, exist_ok=True)

        cascPath = os.path.abspath(os.getcwd())

        ap = argparse.ArgumentParser()
        ap.add_argument("-p", "--port", required=False, default=portmum,
                        help="Port number to start HTTPServer, defaults to {}".format(portmum))

        ap.add_argument("-i", "--ipaddress", required=False, default='127.0.0.1',
                        help="IP Address to start HTTPServer")

        ap.add_argument("-d", "--dbaddress", required=False, default='127.0.0.1:27017',
                        help="Database IP Address")

        ap.add_argument("-s", "--static", required=False, default=www,
                        help="Static directory where WWW files are present")


        ap.add_argument("-f", "--logfile", required=False, default=logpath,
                        help="Directory where application logs shall be stored, defaults to %s" % (logpath))

        # Parse Arguments
        args = vars(ap.parse_args())
        if args['port']:
            portnum = int(args["port"])

        if args['ipaddress']:
            ipadd = args["ipaddress"]

        if args['dbaddress']:
            dbip = args["dbaddress"]

        if args['static']:
            staticwww = os.path.abspath(args['static'])

        if args['logfile']:
            logpath = os.path.abspath(args['logfile'])
        else:
            if not os.path.exists(logdir):
                print("Log directory does not exist, creating %s" % (logdir))
                os.makedirs(logdir)

        logging.basicConfig(filename=logpath, level=logging.DEBUG, format='%(asctime)s %(message)s')
        handler = logging.StreamHandler(sys.stdout)
        logging.getLogger().addHandler(handler)

        HttpServer.config.update({'server.socket_host': ipadd,
                                  'server.socket_port': portnum,
                                  'server.socket_timeout': 60,
                                  'server.thread_pool': 8,
                                  'server.max_request_body_size': 0
                                  })

        logging.info("Static dir: %s " % (staticwww))
        conf = {'/': {
            'tools.sessions.on': True,
            'tools.staticdir.on': True,
            'tools.staticdir.dir': staticwww}
        }

        HttpServer.quickstart(Webserver (staticdir=staticwww, dbhost=dbip), '/', conf)
        #wbsx = Webserver(staticdir=staticwww)
        #wbsx.getjs()
