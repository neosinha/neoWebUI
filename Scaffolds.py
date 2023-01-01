import datetime
import os.path, shutil, errno, json

import pandas as pd
from jinja2 import Environment, FileSystemLoader

class Scaffold(object):


    def __init__(self, appmodel=None, exportdir=None, appname=None):
        """
        Initialize App Model
        :param appmodel:
        """
        appfile = os.path.join(os.getcwd(), 'appmodel', 'app-model.xlsx')
        self.templatedir = os.path.join(os.getcwd(), 'templates')
        self.environment = Environment(loader=FileSystemLoader(self.templatedir))


        dtx = str(datetime.datetime.today()).split(' ')[0].replace('-', '')
        self.datex = dtx
        self.appname = f'App'
        if appname:
            self.appname = appname

        self.exportdir = os.path.join(os.getcwd(), 'exports', self.appname)
        if exportdir:
            self.exportdir = exportdir

        print("Setting export dir to {}".format(self.exportdir))
        os.makedirs(self.exportdir, exist_ok=True)

        if appmodel:
            if os.path.exists(appmodel):
                print(f"Found app modelfile {appfile}")

        self.about = pd.read_excel(appfile, sheet_name='About')
        print(self.about)

        self.forms = pd.read_excel(appfile, sheet_name='Forms')
        print(self.forms)
        

        self.initgenerationvars()
        self.copytemplateFiles()


    def initgenerationvars(self):
        """
        Initialize Generation Variables
        :return:
        """
        home_dir = os.environ['HOME']
        self.gen_model = {}

        self.gen_model['appname'] = self.appname
        self.gen_model['datetime'] = self.datex

        self.gen_model['os'] = {}
        for key, val in os.environ.items():
            self.gen_model['os'][key] = val


    def generateFormDefs(self):
        """
        Use Form definitions to generate JSON definitions JS Files
        :return:
        """
        self.forms.set_index('Form Name')
        formnames = self.forms['Form Name'].unique()
        formdefs = []
        for idx, formx in enumerate(formnames):
            print(f"=====Form: {formx}")
            fields = self.forms.loc[self.forms['Form Name'] == formx]
            fldarr = []
            for fld in fields.iterrows():
                print(fld[1]['FieldName'], fld[1]['Type'], fld[1]['Default'])
                formdef = {'name' : fld[1]['FieldName'],
                           'type' : fld[1]['Type'],
                           'id': '{}_id'.format(fld[1]['FieldName']),
                           'value' : fld[1]['Default']}
                fldarr.append(formdef)
            formdefs.append({'name' : formx, 'fields' : fldarr})

        print(formdefs)
        self.gen_model['formobjs'] = formdefs
        return formdefs


    def generateFormSubmissions(self):
        """
        Generates Form Submission APIs for the WebServer
        :return:
        """
        formnames = self.forms['Form Name'].unique()
        httpserver = self.environment.get_template('HttpServeletTemplate.py')
        context = {}
        context['formobjs'] = self.generateFormDefs()

        httpserverfile = os.path.join(self.exportdir, 'HttpServelet.py')
        with open(httpserverfile, mode="w", encoding="utf-8") as results:
            print(json.dumps(self.gen_model, indent=2))
            results.write(httpserver.render(self.gen_model))
            print(f"... wrote {httpserverfile}")

    def generateWebServices(self):
        """
        Generates webservices backend file with Ajax Calls

        :return:
        """
        websx = self.environment.get_template('webservicesTemplate.jst')
        context = {}
        context['appname'] = self.appname
        context['datetime'] = self.datex
        context['formobjs'] = self.generateFormDefs()

        websxfile = os.path.join(self.exportdir, 'ui_www', 'js','webservices.js')
        with open(websxfile, mode="w", encoding="utf-8") as results:
            results.write(websx.render(context))
            print(f"... wrote {websxfile}")

    def generateAppService(self):
        """
        Generates Initial App Template
        :return:
        """
        websx = self.environment.get_template('apptemplate.jst')
        context = {}
        context['appname'] = self.appname
        context['datetime'] = self.datex
        context['formobjs'] = self.generateFormDefs()

        appfile = os.path.join(self.exportdir, 'ui_www', 'js', 'app.js')
        with open(appfile, mode="w", encoding="utf-8") as results:
            results.write(websx.render(context))
            print(f"... wrote {appfile}")

    def generateIndexFile(self):
        """
        Generates the Index File
        :return:
        """
        indx = self.environment.get_template('index.html')
        context = {}
        context['appname'] = self.appname
        context['datetime'] = self.datex
        context['formobjs'] = self.generateFormDefs()

        idxfile = os.path.join(self.exportdir, 'ui_www', 'index.html')
        with open(idxfile, mode="w", encoding="utf-8") as results:
            results.write(indx.render(context))
            print(f"... wrote {idxfile}")


    def generateViews(self):
        """
        Generates Form views code
        :return:
        """
        formviews = self.environment.get_template('formviews.jst')
        appviews  = self.environment.get_template('views.app.jst')

        context = {}
        context['appname'] = self.appname
        context['datetime'] = self.datex
        context['formobjs'] = self.generateFormDefs()

        formvf = os.path.join(self.exportdir, 'ui_www', 'js','views.forms.js')
        with open(formvf, mode="w", encoding="utf-8") as results:
            results.write(formviews.render(context))
            print(f"... wrote {formvf}")

        appviewf = os.path.join(self.exportdir, 'ui_www', 'js', 'views.app.js')
        with open(appviewf, mode="w", encoding="utf-8") as results:
            results.write(appviews.render(context))
            print(f"... wrote {appviewf}")




    def copytemplateFiles(self):
        print("Copying WebServer files")
        src = os.path.join(self.templatedir, 'ui_www')
        dst = os.path.join(self.exportdir, 'ui_www')
        if os.path.exists(dst):
            print("Destination {} exists, deleting now ..".format(dst))
            shutil.rmtree(dst, ignore_errors=True)
        try:
            shutil.copytree(src, dst)
        except OSError as exc:  # python >2.5
            if exc.errno in (errno.ENOTDIR, errno.EINVAL):
                shutil.copy(src, dst)
            else:
                raise



if __name__ == '__main__':
    print("Starting Scaffolding")
    xlmodel = os.path.join(os.getcwd(), 'appmodel', 'app-model.xlsx')
    scf = Scaffold(appmodel=xlmodel, appname='App1')
    scf.generateFormDefs()
    scf.generateFormSubmissions()
    scf.generateWebServices()
    scf.generateAppService()
    scf.generateIndexFile()
    scf.generateViews()


