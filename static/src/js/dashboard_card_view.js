odoo.define('logic_performance_tracker.DashboardCardView', function (require) {
    "use strict";
    var core = require('web.core');
    var AbstractController = require('web.AbstractController');
    var AbstractModel = require('web.AbstractModel');
    var AbstractRenderer = require('web.AbstractRenderer');
    var AbstractView = require('web.AbstractView');
    var viewRegistry = require('web.view_registry');
    var QWeb = core.qweb;

    
    var DashboardCardModel = AbstractModel.extend({
        init: function () {
            this.values = {};
            this._super.apply(this, arguments);
        },
    });
    
    var DashboardCardRenderer = AbstractRenderer.extend({
        // Override the template to specify a custom QWeb template
        // template: 'custom_module.CustomRendererTemplate',
        template: 'logic_performance_tracker.dashboard_card_template',
        xmlDependencies: ['/logic_performance_tracker/static/src/xml/dashboard_templates.xml'],
        
    // Override the render method to customize the rendering logic
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.state = state || {};

        },
        _render: function () {
            var self = this;
            // console.log(Object.keys(self['state']))
            const values = self.state.data
            console.log()
            return this._super.apply(this, arguments).then(function () {
                // var values = self['state'];
                console.log("gelt")
                console.log(values)
                console.log(values.length)
                var purchase_dashboard = QWeb.render('logic_performance_tracker.dashboard_card_template', {
                    values: values,
                });
                console.log(self.$el)
                self.$el.prepend(purchase_dashboard);
                // self.$el.before(purchase_dashboard);
            });
        },
    });
    var DashboardCardController = AbstractController.extend({
        start: function () {
            var self = this;
            // self.state.dashboardValues = {'name':'babu','age':10};

            this._rpc({
                model: 'digital.task', // Replace with your actual model name
                method: 'search_read', // Use 'search_read' to retrieve records
                args: [], // Define search domain if needed
                kwargs: {},
            }).then(function (data) {
                // Set the state with the retrieved data
                var state = {'data': data}
                self.renderer.updateState(state,false)
                self.renderer._render()
                console.log(self.renderer)

            });
            return this._super.apply(this, arguments);
            },

    });

    
    var DashboardCardView = AbstractView.extend({
        config: _.extend({}, AbstractView.prototype.config, {
            Model: DashboardCardModel,
            Controller: DashboardCardController,
            Renderer: DashboardCardRenderer,
        }),
        viewType: 'dashboard_card', // Use single quotes (') instead of backticks (`) or curly quotes (‘’).
        el: '.o_dashboard_card',
    });
    
    viewRegistry.add('dashboard_card', DashboardCardView);
    
    return DashboardCardView;
});