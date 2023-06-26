import datetime
import os.path, shutil, errno, json

import pandas as pd
import numpy as np
from jinja2 import Environment, FileSystemLoader

class Scaffold(object):


    def __init__(self, appname=None, exportdir=None, appdef=None):
        """
        Initialize App Model
        :param appdef:
        """

        appfile = os.path.join(os.getcwd(), 'appmodel', 'app-model') #deffault app model
        if appdef:
            appfile = appdef
        #appfile = os.path.join(os.getcwd(), 'appmodel', 'app-model.xlsx')
        self.templatedir = os.path.join(os.getcwd(), 'template_excel')
        self.environment = Environment(loader=FileSystemLoader(self.templatedir))


        dtx = str(datetime.datetime.today()).split(' ')[0].replace('-', '')
        self.datex = dtx
        self.appname = 'App1'
        if appdef:
            self.appname = appname

        self.exportdir = os.path.join(os.getcwd(), 'exports', self.appname)
        if exportdir:
            self.exportdir = exportdir

        print("Setting export dir to {}".format(self.exportdir))
        os.makedirs(self.exportdir, exist_ok=True)

        if appdef:
            if os.path.exists(appdef):
                print(f"Found app modelfile {appfile}")

        self.about = pd.read_excel(appfile, sheet_name='About')
        print(self.about)

        self.forms = pd.read_excel(appfile, sheet_name='Forms')
        print(self.forms)

        self.backend = pd.read_excel(appfile, sheet_name='Backend')
        self.backend['TableName'].replace({np.nan: None}, inplace=True)
        #df.col_name.replace({np.nan: None}, inplace=True)
        self.backend['TableName'] = self.backend['TableName'].astype(str)
        print(self.backend)

        self.pageviews = pd.read_excel(appfile, sheet_name='PageViews')
        #print(self.pageviews)


        

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



    def extractTabViews(self):
        """
        Extracts Tab Names and Form Views
        :return:
        """
        tabnames = self.backend['TabView'].unique()
        print(tabnames)
        print("=== TabViews ===")
        tabviews = []
        for idx, tabx in enumerate(tabnames):
            form_rows = self.backend.loc[self.backend['TabView'] == tabx]
            formnames = list(form_rows['Form Name'])
            tabviewname = None
            print(tabx, formnames)
            if len(formnames):
                formobjs = {}
                #get form objects for each form
                for fname in formnames:
                    #formdefs = self.getFormbyName(formname=fname)
                    formobjs[fname] = self.getFormbyName(formname=fname)
                    #print("FormObj: ", json.dumps(formobjs, indent=2))

                #Add to tab only if there is at least 1 form in the tabview
                tabviews.append( {'tabview' : tabx, 'forms' : formnames, 'formobjs': formobjs,
                                  } )

        print("\t===**** TabViews **** ===")
        return tabviews


    def extractPageSequence(self):
        """
        Extracts Page load Sequence
        :return:
        """
        pages = self.pageviews
        print(pages)
        loadseq = pages['LoadSequence'].unique()[:-1]
        print("PgSeq=== \n",loadseq)

        pgsequence = {}
        for idx, pseq in enumerate(loadseq):
            sequence = self.pageviews.loc[self.pageviews['LoadSequence'] == pseq]
            seq_cond = list(sequence['PageView'])[0].lower()
            pgsequence[pseq] = seq_cond
        if 'init' in pgsequence:
            print(f"App wouuld be initialized by pageview.{pgsequence['init']}")
        else:
            pgsequence['init'] = 'defaultlayout'

        print(pgsequence)

        return pgsequence


    def extractPageViews(self):
        """
        Extracts Page Views
        :return:
        """
        pagenames = self.backend['PageView'].unique()[:-1]
        print(pagenames)
        print("=== Page Names ===")
        pageviews = {}
        for idx, pagex in enumerate(pagenames):
            tab_rows = self.backend.loc[self.backend['PageView'] == pagex]
            tab_names = list(tab_rows['TabView'])
            tabviewname = None
            #print(pagex, tab_names)
            tabviews = []
            pageviews[pagex] = []

            for tabx in tab_names:
                form_rows = self.backend.loc[self.backend['TabView'] == tabx]
                formnames = list(form_rows['Form Name'])
                tabviewname = None
                #print("tabs",tabx, formnames)
                if len(formnames):
                    formobjs = {}
                    # get form objects for each form
                    for fname in formnames:
                        # formdefs = self.getFormbyName(formname=fname)
                        formobjs[fname] = self.getFormbyName(formname=fname)
                        #print("FormObj: ", json.dumps(formobjs, indent=2))

                    # Add to tab only if there is at least 1 form in the tabview
                    if 'NaN' in str(tabx).lower():
                        print(f"Skipping {tabx}")
                    else:
                        tabviews.append({'tabview': tabx, 'forms': formnames, 'formobjs': formobjs,
                                 })
                if len(tabviews):
                    if 'NaN' in str(pagex).lower():
                        print("Skipping empty pages")
                    else:
                        pageviews[pagex] = tabviews

        print("\t===**** PageViews **** ===")
        print("\t--> ", len(pageviews))
        #print(json.dumps(pageviews, indent=2))

        return pageviews

    def generateFormDefs(self):
        """
        Use Form definitions to generate JSON definitions JS Files
        :return:
        """
        self.forms.set_index('Form Name')
        formnames = self.forms['Form Name'].unique()
        formdefs = []
        authdefs = []

        for idx, formx in enumerate(formnames):
            print(f"=====Form: {formx}")
            fields = self.forms.loc[self.forms['Form Name'] == formx]
            formtype = self.backend.loc[self.backend['Form Name'] == formx]
            print("FormType: {}".format(formtype['RecordType'].values[0]))
            tablename = None
            print("FormTable: {}".format(formtype['TableName'].values[0]))

            fldarr = []
            for fld in fields.iterrows():
                print(fld[1]['FieldName'], fld[1]['Type'], fld[1]['Default'])
                formdef = {'name' : fld[1]['FieldName'],
                           'type' : fld[1]['Type'],
                           'id': '{}_id'.format(fld[1]['FieldName']),
                           'value' : fld[1]['Default']}
                fldarr.append(formdef)


            formdefs.append({'name': formx, 'fields': fldarr,
                             'recordtype' : formtype['RecordType'].values[0],
                             'tablename' : formtype['TableName'].values[0]
                             })


        #print(formdefs)
        self.gen_model['formobjs'] = formdefs
        self.gen_model['authobjs'] = authdefs

        return formdefs

    def getFormbyName(self, formname=None):
        """
        Gets the Form Name
        :param formname:
        :return:
        """
        formdefs = self.gen_model['formobjs']
        forms = []
        for idx, formdef in enumerate(formdefs):
            #print(f"TabForm: {formname}")
            if formname == formdef['name']:
                #print("\t\t--- ", formname, formdef['name'])
                forms.append(formdef)
                break

        #print("\t\t--- ", len(forms))
        return forms




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
        context['pagesequence'] = self.extractPageSequence()

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
        context['pagesequence'] = self.extractPageSequence()

        print("Page Seq")
        print(f"\t{context['pagesequence']}")
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
        pageviews  = self.environment.get_template('pageviews.app.jst')

        context = {}
        context['appname'] = self.appname
        context['datetime'] = self.datex
        context['formobjs'] = self.generateFormDefs()
        context['pageviews'] = self.extractPageViews()


        context['tabviews'] = self.extractTabViews()

        formvf = os.path.join(self.exportdir, 'ui_www', 'js','views.forms.js')
        with open(formvf, mode="w", encoding="utf-8") as results:
            results.write(formviews.render(context))
            print(f"... wrote {formvf}")

        appviewf = os.path.join(self.exportdir, 'ui_www', 'js', 'views.app.js')
        with open(appviewf, mode="w", encoding="utf-8") as results:
            results.write(appviews.render(context))
            print(f"... wrote {appviewf}")

        pageviewf = os.path.join(self.exportdir, 'ui_www', 'js', 'pageviews.app.js')
        with open(pageviewf, mode="w", encoding="utf-8") as results:
            results.write(pageviews.render(context))
            print(f"... wrote {pageviewf}")

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

    xlmodel = os.path.join(os.getcwd(), 'appmodel', 'packet-manager.xlsx')
    xlmodel = os.path.join(os.getcwd(), 'appmodel', 'app-model.xlsx')
    xlmodel = os.path.join(os.getcwd(), 'appmodel', 'raedam-enforcement.xlsx')
    xlmodel = os.path.join(os.getcwd(), 'appmodel', 'pexpress.xlsx')

    #xlmodel = os.path.join(os.getcwd(), 'appmodel', 'summarize.xlsx')

    #scf = Scaffold(appdef=xlmodel, appname='Summarize')
    scf = Scaffold(appdef=xlmodel, appname='PExpress')
    scf.generateFormDefs()
    scf.generateFormSubmissions()
    scf.generateWebServices()
    scf.generateAppService()
    scf.generateIndexFile()
    #scf.generateTabViews()
    scf.generateViews()



