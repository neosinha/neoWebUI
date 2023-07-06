/**
 * Rest APIs for {{appname}}
 * Generated on {{datetime}}
 */


var serverLocation = location.host;
var server = "http://" + serverLocation ;
console.log("Location: "+ server);

var backendmodel = null;



/**
 * Class webservice
 */
var Webservices = function () {
    //get logobject back on the server
    this.getclientlog = function () {

    }

    {% for formobj in formobjs %}
    this.{{ formobj.form.lower() }} = function() {
          //make an ajax call to API submit_{{formobj.form.lower() }}
          var dataobj =  {
                  {% for fld in formobj.fields -%}
                  '{{fld.field.lower()}}' : '{{fld.value}}',
                  {% endfor -%}
                          };
          var dataobj = {
            {% for fld in formobj.fields -%}
                '{{fld.field.lower()}}' : document.getElementById('{{formobj.form.lower()}}_{{fld.field.lower()}}_id').value,
            {% endfor -%}
            };

          $.ajax( {url : server+'/submit_{{formobj.form.lower()}}',
                  sync: false,
                  method: "POST",
                  data : {'data': JSON.stringify(dataobj)},
                  success: callbacks.{{ formobj.form.lower() }}
                  });
    };//end of {{formobj.form.lower()}}
    {% endfor -%}

    //webservices for all get tab functions
    //{{tabviews}} tabviews were found
    {% for tview in tabviews.tabs  -%}
    //TabView: tview.tab
    {% set tabtype = tview.content.split(":")[0]  %}
    {% set tabname = tview.content.split(":")[0]  %}
    {% if tabtype == "get" %}
    //TabView: {{tabname}}
    this.{{tabname.lower()}} = function() {
        $.ajax( { url : server+'/submit_{{formobj.form.lower()}}',
                  sync: false,
                  method: "POST",
                  data : {'data': JSON.stringify(dataobj)},
                  success: callbacks.{{ formobj.form.lower() }}
        });
    }; // end of {{tabname}} web call
    {% endif -%}

    {% endfor %}

    //webservices for all get table functions
    //{{tableviews}} tableviews were found
    {% for tview in tableviews  -%}
    //TabView: {{tview.table}}, {{tview.content}}
    {% set tabtype = tview.content.split(":")[0]  %}
    {% set tabname = tview.content.split(":")[1]  %}
    {% if tabtype == "get" -%}
    //Get TableView: {{tabname}}
    this.{{tabname.lower()}} = function() {
        $.ajax( {url : server+'/{{tabname.lower()}}',
                 sync: false,
                 method: "POST",
                 data : {'data': JSON.stringify(dataobj)},
                 success: callbacks.{{tabname.lower() }}
                } );
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

        {%- for trx, pgname in pagesequence.items() -%}
        {% if 'callback:' in trx %}
        {% if formobj.form.lower() in trx %}
            //{{trx}} {{pgname}}
         pviews.pageview_{{pgname.lower()}}();
        {% endif %}
        {% endif %}

        {% endfor %}
    }

 {% endfor %}

  //callbacks for webservices for all get table functions
  // {{tableviews}} tableviews were found
  {% for tview in tableviews  -%}
    //TabView: {{tview.table}}, {{tview.content}}
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


