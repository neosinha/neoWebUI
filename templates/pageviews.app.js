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
        var divx_{{pview.subview}} = ui.createElement('div', 'cont_{{pview.subview}}' );
        divx_{{pview.subview}}.innerHTML = '<h3>Subview {{pview.subview}}</h3><hr>';
        //var divx_{{pview.subview}} = this.create_{{pview.subview.lower()}}();
        divx.appendChild(divx_{{pview.subview}});

        {% endfor %}

        var mx = document.getElementById('mcontent');
        mx.innerHTML = '';
        mx.appendChild(divx);

        return divx;
    };
    {% endfor %}




};

