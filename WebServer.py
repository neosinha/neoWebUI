import os
import argparse
import base64, json
import logging
import datetime, time, os, sys, shutil
import cherrypy as HttpServer
import inspect

class Webserver(object):
    '''
    classdocs
    '''

    staticdir = None

    starttime = None

    def __init__(self, staticdir=None):
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
        port = 9005
        www = os.path.join(os.getcwd(), 'ui_www')
        ipaddr = '127.0.0.1'
        dbip = '127.0.0.1'
        logpath = os.path.join(os.getcwd(), 'log', 'webui-server.log')
        logdir = os.path.dirname(logpath)
        os.makedirs(logdir, exist_ok=True)

        cascPath = os.path.abspath(os.getcwd())

        ap = argparse.ArgumentParser()
        ap.add_argument("-p", "--port", required=False, default=6001,
                        help="Port number to start HTTPServer.")

        ap.add_argument("-i", "--ipaddress", required=False, default='127.0.0.1',
                        help="IP Address to start HTTPServer")

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

        #HttpServer.quickstart(Webserver (staticdir=staticwww),
        #                      '/', conf)
        wbsx = Webserver(staticdir=staticwww)
        wbsx.getjs()
