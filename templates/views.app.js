// file holds the code which designs the UI views
// or bigger/composite UI view elements

var ui = new Bootstrap();
//var forms = new FormViews();
var Views = function() {

    this.pagelayout = function() {
        //initialize a jumbotron object
        var h1x = ui.h3(null, 'Content for {{appname}}', null);
        var jum = ui.jumbotron('view1', h1x);


        var notifyarea = ui.createElement('div', 'notify'); //add a notify area
        ui.addSubViewToMain([jum]);

    }; //end of pagelayout


    //Initial Layout
    this.initiallayout = function() {

        //initialize a jumbotron object
        var h1x = ui.h3(null, 'Header', null);
        var jum = ui.jumbotron('view1', h1x);


        //build a tabbed view
	    var tabs = new Array();
	    tabs.push({'name' : "AppInfo" , 'content' : this.appInfo() }); //add content for Basic App Info
	    tabs.push({'name' : "Forms" , 'content' : this.formview() }); //add the tab content for Forms View

	    // Tab Views //
	     {% for tabv in tabviews -%}
	     tabs.push({'name' : "{{tabv.tabview}}", 'content': this.gettabview_{{tabv.tabview.lower()}}() }); //add tabbed view {{tabv.tabview}}
	     {% endfor -%}



	    var navtabs= ui.navtabs('tabbed', 'justified', tabs); //initialize the tab object

	    var notifyarea = ui.createElement('div', 'notify'); //add a notify area

        //add the nav tabs in the jumbotron area
	    jum.appendChild(navtabs);
	    jum.appendChild(notifyarea); //add the tabs in the notify area


	    //loginview = ui.addSubView(jum, navtabs);

	    //showView([navbar, jum]);
	    //view = ui.addSubViewById('mcontent', [loginview]);
	    ui.addSubViewToMain([jum]);

    } ;//end initialView


    //Sample Voew Code Routines
    this.appInfo = function() {
        var px = ui.createElement('p', 'appinfo');
        px.innerHTML = 'Example Content for {{appname}}';

        return px;

    } ;

    //Sample View Code Routines
    this.formview = function() {
        var divx = ui.createElement('div', 'formview');
        divx.appendChild(ui.br());
        divx.innerHTML = 'Example Content for Form {{appname}}';

        return divx;

    } ;

    {% for tabv in tabviews %}
    //Generate TabView for {tabv.tabview}
    this.gettabview_{{tabv.tabview.lower()}} = function() {
        var divx = ui.createElement('div', "{{tabv.tabview.lower()}}_rootid");
        var p = ui.createElement('p', "{{tabv.tabview.lower()}}_childid");
        p.innerHTML = '<h3>{{tabv.tabview}}</h3>';
        divx.appendChild(p);
        //Code to build {{tabv.tabview}}
        var tabobjs = new Array();
        {% for tabobj in tabv.tabs -%}
        {% set contenttype = tabobj.content.split(":")[0] -%}
        {% set contentname = tabobj.content.split(":")[1] -%}
        {% if contenttype == "form" -%}
             //this.createview_signin
        tabobjs.push({'name': "{{tabobj.tab}}" , 'content' : forms.createview_{{contentname}}() }); //Content Type: {{contenttype}}
        {% endif -%}
        {% if contenttype == "tableview" -%}
        tabobjs.push({'name': "{{tabobj.tab}}" , 'content' : tableviews.create_{{contentname}}() }); //Content Type: {{contenttype}}
        {% endif -%}

        {% endfor -%}
        var navtabs= ui.navtabs('tabbed', 'justified', tabobjs); //initialize the tab object
        divx.appendChild(navtabs);

        return divx;
	}
    {% endfor -%}

    //subviews





    //basic navbar handler
    this.appNavBar = function() {
	    navbar = ui.navbar("navarea", '{{appname}}'); //Initialize App Header
	    ui.addSubViewToMain([navbar]);
    } ;

    //process subviews
    {% for pg in views -%}
     this.createview_{{pg.view.lower()}} = function() {
        var divp = ui.createElement('div', 'sview_{{pg.view.lower()}}' );


        return divp;
     }; // subview for {{pg.view.lower() }}

    {% endfor %}




} ;




function clicker() {
	alert('Clicked..');
}




