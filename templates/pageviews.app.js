//defines the page level structures

var ui = new Bootstrap();

var Pages = function() {

    //Default Layout
    this.pageview_defaultlayout = function() {
        views.appNavBar();
	    views.initiallayout();
	    //backendTester();
    }

    {% for pgobj in pages-%}
    //Generate PageView for {{pgobj.page}}
    this.pageview_{{pgobj.page.lower()}} = function() {
        var divx = ui.createElement('div', '{{pgobj.page.lower()}}_container');
        divx.setAttribute('class', 'well pagewell');
        divx.innerHTML = "<h2>View for {{pgobj.page.lower()}}</h2><BR>";

        //add subviews
        {% for pview in pgobj.subviews -%}
            {% if ':' in pview.subview -%}
                {% set viewtype = pview.subview.split(":")[0] -%}
                {% set viewname = pview.subview.split(":")[1] %}
        // Page Subview: {{pview.subview}}, {{viewtype}}
        // Page Subview: {{pview.subview}}, {{viewname}}
                {% if viewtype == "tabview" %}
        var divx_{{viewname.lower()}} = ui.createElement('div', 'cont_{{viewname.lower()}}' );
        divx_{{viewname.lower()}}.innerHTML = '<h3>Subview {{viewname.upper()}}</h3><hr>';
        var dsubview_{{viewname.lower()}} = views.gettabview_{{viewname.lower()}}();
        divx.appendChild(divx_{{viewname.lower() }});
        divx.appendChild(dsubview_{{viewname.lower() }});
                {% elif viewtype == "footer" %}
        var divx_{{viewname.lower()}} = ui.createElement('div', 'cont_{{viewname.lower()}}' );
        divx.setAttribute('class', 'pagefooter');
        divx_{{viewname.lower()}}.innerHTML = '<h3>Footer for {{viewname.lower()}} goes here</h3><hr>';
        divx.appendChild(divx_{{viewname.lower() }});
                {% endif %}

            {% else %}
                {% set viewtype = "divx" -%}
                {% set viewname = pview.subview %}
        var divx_{{pview.subview}} = ui.createElement('div', 'cont_{{viewname.lower()}}' );
        divx_{{pview.subview}}.innerHTML = '<h3>Subview {{viewname.upper()}}</h3><hr>';
        divx.appendChild(divx_{{pview.subview}});
            {% endif %}
        {% endfor %}

        var mx = document.getElementById('mcontent');
        mx.innerHTML = '';
        mx.appendChild(divx);

        return divx;
    };
    {% endfor %}




};

