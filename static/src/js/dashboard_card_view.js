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
        // className: 'o_dashboard_card',
        // cssLibs: [
        //     "/logic_performance_tracker/static/src/scss/dashboard_card_view.scss"
        // ],
        // template: 'logic_performance_tracker.dashboard_card_template',
        xmlDependencies: ['/logic_performance_tracker/static/src/xml/dashboard_templates.xml'],
        
        events:_.extend({}, ListRenderer.prototype.events, {
            'click .o_filter_performance': '_onPerformanceFilterActionClicked',
        }),


        _onPerformanceFilterActionClicked: function (ev) {
            var self = this;

            // Get the date field's value
            // var selectedDate = this.$('#from_date').val();
            // console.log(selectedDate+"Helloasdas")
        },
        
    // Override the render method to customize the rendering logic
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.state = state || {};

        },
        // on_attach_callback : function(){
        //     this._render();
        // },
        start() {
            this._super.apply(this, arguments)
        },
        // _renderView: function () {
        //     var self = this;
        //     console.log("Hellosdfdsf")
        //     console.log(self)
        // },
        _render: function () {
            const values = this.state.data
            console.log(values)
            var digital_dashboard = QWeb.render('logic_performance_tracker.dashboard_card_template', {
                values: values
            });
            this.$el.append(digital_dashboard);
                    
                return $.when();
            // var self = this;
            // console.log("Babss")
            // console.log(this.$el)
            // // console.log(Object.keys(self['state']))
            // // const values = self.state.data
            // console.log(this)
            // var digital_dashboard = QWeb.render('logic_performance_tracker.dashboard_card_template', {
            //             values: values,
            //         });
            // this.setElement(digital_dashboard);
            // // this.$el.prependTo(purchase_dashboard);
            // // console.log(this.$el)
            //     return  this.$.when();
            // // return this._super.apply(this, arguments).then(function () {
            // //     // var values = self['state'];
            // //     console.log("gelt")
            // //     console.log(values)
            // //     console.log(values.length)
            // //     var purchase_dashboard = QWeb.render('logic_performance_tracker.dashboard_card_template', {
            // //         values: values,
            // //     });
            // //     console.log(purchase_dashboard)
            // //     self.prependTo(purchase_dashboard);
            // //     console.log(self.$)
            // //     // self.renderElement();
            // //     // self.$el.before(purchase_dashboard);
            // // });
        },
    });
    var DashboardCardController = AbstractController.extend({
        start: function () {
            var self = this;
            var state = {}
            // self.state.dashboardValues = {'name':'babu','age':10};
            this._rpc({
                model: this.modelName, // Replace with your actual model name
                method: 'retrieve_dashboard_data', // Use 'search_read' to retrieve records
                // args: [], // Define search domain if needed
                // kwargs: {},
            }).then(function (data) {
                // Set the state with the retrieved data
                state = {'data': data}
                self.renderer.updateState(state,false)
                console.log(self.renderer)
            }).catch(function(err){
                console.log(err)
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

        // start: function () {
        //     this.renderer = new DashboardCardRenderer(this, this.state, this.rendererParams);
        //     // ...
        // },
        viewType: 'dashboard_card', // Use single quotes (') instead of backticks (`) or curly quotes (‘’).
    });
    
    viewRegistry.add('dashboard_card', DashboardCardView);
    
    return DashboardCardView;
});