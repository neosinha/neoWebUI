/**
 * Rest APIs for {{appname}}
 * Generated on {{datetime}}
 *
 * Uses fetch(): the bootstrap6 frontend does not load jQuery.
 */


var server = location.protocol + "//" + location.host;
console.log("Location: "+ server);

var backendmodel = null;


/**
 * POST a form object as the `data` field, the same encoding the server
 * expects from the jQuery version (application/x-www-form-urlencoded).
 */
function wsPost(path, dataobj, onSuccess) {
    var body = new URLSearchParams({'data': JSON.stringify(dataobj)});
    fetch(server + path, {method: 'POST', body: body})
        .then(function (resp) {
            if (!resp.ok) {
                throw new Error(resp.status + ' ' + resp.statusText);
            }
            return resp.text();
        })
        .then(onSuccess)
        .catch(function (err) {
            console.error('POST ' + path + ' failed: ' + err);
        });
}

function wsGet(path, onSuccess) {
    fetch(server + path)
        .then(function (resp) {
            if (!resp.ok) {
                throw new Error(resp.status + ' ' + resp.statusText);
            }
            return resp.text();
        })
        .then(onSuccess)
        .catch(function (err) {
            console.error('GET ' + path + ' failed: ' + err);
        });
}


/**
 * Class webservice
 */
var Webservices = function () {
    //get logobject back on the server
    this.getclientlog = function () {

    }

    {% for formobj in formobjs %}
    this.{{ formobj.form.lower() }} = function() {
          //make a call to API submit_{{formobj.form.lower() }}
          var dataobj = {
            {% for fld in formobj.fields -%}
                '{{fld.field.lower()}}' : document.getElementById('{{formobj.form.lower()}}_{{fld.field.lower()}}_id').value,
            {% endfor -%}
            };

          wsPost('/submit_{{formobj.form.lower()}}', dataobj, callbacks.{{ formobj.form.lower() }});
    };//end of {{formobj.form.lower()}}
    {% endfor -%}

    //webservices for all get table functions
    //{{tableviews}} tableviews were found
    {% for tview in tableviews  -%}
    {% set tabtype = tview.content.split(":")[0]  %}
    {% set tabname = tview.content.split(":")[1]  %}
    {% if tabtype == "get" -%}
    //Get TableView: {{tview.table}} -> {{tabname}}
    this.{{tabname.lower()}} = function() {
        wsGet('/{{tabname.lower()}}', callbacks.{{tabname.lower() }});
    }; // end of {{tabname}} web call
    {% endif -%}

    {% endfor %}

};


//Callback Class for Webservice
/**
*Class : callbacks
**/
var Callbacks = function () {
 {% for formobj in formobjs %}

    this.{{formobj.form.lower()}} = function (msg) {
        console.log('Callback {{formobj.form.lower()}}'+ msg );
        backendmodel['{{formobj.form.lower()}}'] = JSON.parse(msg);
        var rarea = document.getElementById('{{formobj.form.lower()}}_rid');
        rarea.innerHTML = '';
        var px = ui.createElement('p', 'resel_{{formobj.form.lower()}}');
        px.innerHTML = msg;
        rarea.appendChild(px);

        {%- for pview in pages -%}
        {%- if 'callback:' in pview['load'] and pview['load'].split(':')[1].lower() == formobj.form.lower() %}
        // Page {{pview.page}} is loaded from this callback ({{pview['load']}})
        pviews.pageview_{{pview.page.lower()}}();
        {%- endif -%}
        {%- endfor %}
    }

 {% endfor %}

  //callbacks for webservices for all get table functions
  // {{tableviews}} tableviews were found
  {% for tview in tableviews  -%}
    {% set tabtype = tview.content.split(":")[0]  %}
    {% set tabname = tview.content.split(":")[1]  %}
    {% if tabtype == "get" -%}
    this.{{tabname.lower()}} = function(msg) {
        var tbldata = JSON.parse(msg);
        tableviews.backend_{{tabname.lower()}} = tbldata;
        tableviews.create_{{tabname.lower()}}();
    }; // end of {{tabname}} web call
    {% endif -%}

    {% endfor %}


 };
