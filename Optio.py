import datetime
import os.path, shutil, errno, json

from jinja2 import Environment, FileSystemLoader
import yaml

class Optio(object):


    def __init__(self, appname=None, exportdir=None, appdef=None):
        """
        Initialize App Model
        :param appdef:
        """

        appfile = os.path.join(os.getcwd(), 'appmodel', 'app-model') #deffault app model
        if appdef:
            appfile = appdef
        #appfile = os.path.join(os.getcwd(), 'appmodel', 'app-model.xlsx')
        self.templatedir = os.path.join(os.getcwd(), 'templates')
        # Frontend adapter: templates/frontends/<framework> overrides files in templates/.
        # Default is bootstrap3, which is the plain templates/ directory.
        self.framework = 'bootstrap3'
        self.frontenddir = None
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
        self.backendmodel = {}
        if appdef:
            if os.path.exists(appdef):
                print(f"Found app modelfile {appfile}")
                with open(appfile, 'r') as yfile:
                    appdef = yaml.safe_load(yfile)
                    #print(json.dumps(appdef, indent=2))
                    self.backendmodel = appdef
                    self.selectFrontend()
                    self.initgenerationvars()
                    self.copytemplateFiles()
                    # copy a version of the YAML file to the export area
                    self.copydefinitions(appfile)


    def selectFrontend(self):
        """
        Pick the frontend adapter from the model:  frontend: {framework: bootstrap6}
        Adapter templates are searched first, then the shared templates/ directory.
        """
        fw = (self.backendmodel.get('frontend') or {}).get('framework', 'bootstrap3')
        if fw != 'bootstrap3':
            fdir = os.path.join(self.templatedir, 'frontends', fw)
            if not os.path.isdir(fdir):
                avail = sorted(os.listdir(os.path.join(self.templatedir, 'frontends')))
                raise ValueError("Unknown frontend '{}'. Available: bootstrap3, {}".format(fw, ', '.join(avail)))
            self.frontenddir = fdir
            self.environment = Environment(loader=FileSystemLoader([fdir, self.templatedir]))
        self.framework = fw
        print("Frontend framework: {}".format(fw))

    def copydefinitions(self, appfile):
        """
        Copy YAML definitions to destination
        :param appfile:
        :return:
        """

        destf = os.path.join(self.exportdir, os.path.basename(appfile))
        with open(destf, 'w') as filex:
            yaml.dump(self.backendmodel, filex)



    def initgenerationvars(self):
        """
        Initialize Generation Variables
        :return:
        """
        home_dir = os.environ['HOME']
        #self.gen_model['appname'] = self.appname
        self.backendmodel['datetime'] = self.datex

        self.backendmodel['os'] = {}
        for key, val in os.environ.items():
            self.backendmodel['os'][key] = val



    def extractTabViews(self):
        """
        Extracts Tab Names and Form Views
        :return:
        """
        tabviews = self.backendmodel['tabviews']
        print("=== TabViews ===")

        return tabviews


    def extractPageSequence(self):
        """
        Extracts Page load Sequence
        :return:
        """
        pages = self.backendmodel['pages']

        pgsequences = {}
        for idx, pseq in enumerate(pages):
            pgsequence = pseq['load']

        if 'init' in pgsequence:
            print(f"App wouuld be initialized by pageview.{pgsequence['init']}")
            pgsequences[pseq['load']] = pseq['page']
        else:
            pgsequences['init'] = 'defaultlayout'

        return pgsequences

    def extractInitPage(self):
        """
        Extracts the Init Page
        :return:
        """
        pgs = self.backendmodel['pages']
        defpage = None
        for pg in pgs:
            if pg['load'] == 'init':
                defpage = pg
                break

        return defpage



    def extractPageViews(self):
        """
        Extracts Page Views
        :return:
        """
        pageviews = self.backendmodel['pages']

        return pageviews

    def generateFormDefs(self):
        """
        Use Form definitions to generate JSON definitions JS Files
        :return:
        """
        formdefs = []
        #print(json.dumps(self.backendmodel['forms'], indent=4))


        return self.backendmodel['forms']

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
        httpserver = self.environment.get_template('httpServelet.template.py')
        context = {}
        context['appname'] = self.backendmodel['appname']
        context['formobjs'] = self.generateFormDefs()
        context['os'] = self.backendmodel['os']
        context['tableviews'] = self.backendmodel['tableviews']

        httpserverfile = os.path.join(self.exportdir, 'HttpServelet.py')
        with open(httpserverfile, mode="w", encoding="utf-8") as results:
            #print(json.dumps(self.gen_model, indent=2))
            results.write(httpserver.render(context))
            print(f"... wrote {httpserverfile}")

    def generateWebServices(self):
        """
        Generates webservices backend file with Ajax Calls

        :return:
        """
        websx = self.environment.get_template('webservices.template.js')
        context = {}
        context['datetime'] = self.datex
        context['formobjs'] = self.generateFormDefs()
        context['pagesequence'] = self.extractPageSequence()
        context['tabviews'] = self.backendmodel['tabviews']
        print(self.backendmodel['tabviews'])
        context['tableviews'] = self.backendmodel['tableviews']
        context['pages'] = self.backendmodel['pages']

        

        websxfile = os.path.join(self.exportdir, 'ui_www', 'js','webservices.js')
        with open(websxfile, mode="w", encoding="utf-8") as results:
            results.write(websx.render(context))
            print(f"... wrote {websxfile}")

    def generateAppService(self):
        """
        Generates Initial App Template
        :return:
        """
        websx = self.environment.get_template('app.template.js')
        context = {}
        context['appname'] = self.appname
        context['datetime'] = self.datex
        context['formobjs'] = self.generateFormDefs()
        context['pagesequence'] = self.backendmodel['pages']

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
        Generates Form, Tab, Table views from code
        :return:
        """
        formviews = self.environment.get_template('views.forms.js')
        appviews  = self.environment.get_template('views.app.js')
        pageviews  = self.environment.get_template('pageviews.app.js')

        context = {}
        context['appname'] = self.backendmodel['appname']
        context['datetime'] = self.datex
        context['formobjs'] = self.generateFormDefs()
        context['tabviews'] = self.extractTabViews()
        context['pages'] = self.backendmodel['pages']
        context['tableviews'] = self.backendmodel['tableviews']



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
            overlay = os.path.join(self.frontenddir, 'ui_www') if self.frontenddir else None
            if overlay and os.path.isdir(overlay):
                # adapter files (css, bootstrapui.js) replace the shared kit's copies
                shutil.copytree(overlay, dst, dirs_exist_ok=True)
        except OSError as exc:  # python >2.5
            if exc.errno in (errno.ENOTDIR, errno.EINVAL):
                shutil.copy(src, dst)
            else:
                raise


if __name__ == '__main__':
    print("Starting Optio Engine..")

    import argparse
    ap = argparse.ArgumentParser(description='Optio app generator')
    ap.add_argument('--model', default=os.path.join(os.getcwd(), 'amodel', 'pexpress.yml'))
    ap.add_argument('--appname', default='PExpress')
    ap.add_argument('--exportdir', default=None)
    args = ap.parse_args()
    scf = Optio(appdef=args.model, appname=args.appname, exportdir=args.exportdir)
    scf.generateFormDefs()
    scf.generateFormSubmissions()
    scf.generateWebServices()
    scf.generateAppService()
    scf.generateIndexFile()
    scf.generateViews()
