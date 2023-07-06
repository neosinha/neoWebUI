/**
 * Autogenerated Form views, on {{datetime}}
 * Any changes would be overwritten on next re-generation
 *
 */

// {{formobjs}}


var FormViews = function() {

 {% for formobj in formobjs %}

    //Form formobj.form.lower() Generator
    this.createview_{{formobj.form.lower()}} = function (msg) {
        //console.log('Callback {{formobj.form.lower()}}'+ msg );
        var ffields = new Array();
         {% for fld in formobj.fields %} // {{fld.field}}, Type: {{fld.type}}
            ffields.push({
                'label' : '{{fld.field}}',
                'type'  : '{{fld.type}}',
                'name'  :  '{{fld.field.lower()}}',
                'id'    : '{{formobj.form.lower()}}_{{fld.field.lower()}}_id',
                'value' : '{{fld.value}}' }
            );
         {% endfor %}

        var vform = ui.createForm('{{formobj.form.lower()}}_formid', ffields);
        //Add submission
        var subx = ui.createElement('button', '{{formobj.form.lower()}}_submit');
         subx.setAttribute('class', 'btn btn-warning btn-lg block');
         subx.innerHTML = 'Submit';
         subx.onclick = function() {
                forms.readform_{{formobj.form.lower()}}();
                websx.{{formobj.form.lower()}}();
                }
         //subx.setAttribute('onclick', 'function() {forms.readform_{{formobj.form.lower()}}(); };' );

        vform.appendChild(subx);
        vform.appendChild(ui.br());


        var divr = ui.createElement('div', '{{formobj.form.lower()}}_rid'); //DIV area for Ajax Callback result
        divr.setAttribute('class', 'well well-lg');
        vform.appendChild(divr);

        hrx = ui.createElement('hr', 'rdiv_{{formobj.form.lower()}}');
        vform.appendChild(hrx);




        return vform;
    };



    this.readform_{{formobj.form.lower()}} = function() { // returns values of form fields of {{formobj.form.lower()}}
        //alert('Reading {{formobj.form.lower()}} form');
        var formobj = {
            {% for fld in formobj.fields -%}
                '{{fld.field}}' : document.getElementById('{{formobj.form.lower()}}_{{fld.field.lower()}}_id').value,
            {% endfor %}
        };

        console.log('Form {{formobj.form}}'+ JSON.stringify(formobj));

        return formobj;
    } ; //end read form fields of {{formobj.form.lower()}}

 {% endfor %}




};

var TableViews = function () {
    {% for tblview in tableviews -%}
    //create tableview {{tblview.table}}
    var backend_{{tblview.table}} = null;
    this.create_{{tblview.table}} = function () {
        var divx = ui.createElement('div', 'tblview_{{tblview.table}}');
        var tblheader = [{tblheader}];
        //{{tblview.header}}
        //{{tblview.content}}
        if (backend_{{tblview.table}}){
            var tbl = ui.createTable('tableview_{{tblview.table}}', 'basic', tblheader, backend_{{tblview.table}} );
        } else {
            divx.innerHTML = "<h3>Placeholder for Table</h3>";
        }

        return divx;
    };

    {% endfor %}


};


