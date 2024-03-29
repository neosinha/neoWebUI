/**
* AppName: {{appname}}
* Date : {{datetime}}
**/
//Global objects
var websx = new Webservices();
var callbacks = new Callbacks();
var forms = new FormViews();
var views = new Views();
var pviews = new Pages();
var tableviews = new TableViews();

var backendmodel = { //Global object which stores all backend responses
{% for formobj in formobjs %} '{{formobj.form.lower()}}': '', // placeholder for parsed {{formobj.form.lower()}}
{% endfor %}
    }



function appInit() {

    {% for pg in pagesequence %}
    {% if pg.load == 'init' -%}
    pviews.pageview_{{pg.page.lower() }}();
    {% endif %}
    {% endfor %}
	//backendTester();
	websx.getclientlog(); //upload log to server
}

//Function which calls all the backend APIs together
function backendTester() {
    {% for formobj in formobjs %}
    websx.{{formobj.form.lower()}}(); //webservices call
    {%- endfor %}
}

function loadLandingView() {
		var h1x = ui.h3(null, 'Example UI', null);
		jum = ui.jumbotron('view1', h1x,' bg-basic'); 
		
		
		//create tab area
		tabs = new Array();
		tabs.push({'name' : "Login" , 'content' : loginForm()});
		tabs.push({'name' : "Register" ,'content' : registerForm()});
		tabs.push({'name' : "Panel" ,'content' : loadPanels()});
		
		navtabs= ui.navtabs('tabbed', 'justified bg-basic text-warning', tabs);
		
		notifyarea = ui.createElement('div', 'notify');
		
		jum.appendChild(navtabs);
		jum.appendChild(notifyarea);
		
		
		ui.addSubViewToMain([jum]);
	}

	




