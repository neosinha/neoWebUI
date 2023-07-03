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
 };


