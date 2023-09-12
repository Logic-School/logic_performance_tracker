odoo.define('logic_performance_tracker.DashboardCardView', function (require) {
    "use strict";
    var core = require('web.core');
    var AbstractController = require('web.AbstractController');
    var AbstractModel = require('web.AbstractModel');
    var AbstractRenderer = require('web.AbstractRenderer');
    var AbstractView = require('web.AbstractView');
    var viewRegistry = require('web.view_registry');
    var web_client = require('web.web_client');

    var QWeb = core.qweb;

    
    var DashboardCardModel = AbstractModel.extend({
        init: function () {
            this.values = {};
            this._super.apply(this, arguments);
        },
    });
    
    var DashboardCardRenderer = AbstractRenderer.extend({

        xmlDependencies: ['/logic_performance_tracker/static/src/xml/dashboard_templates.xml'],
        
        events:_.extend({}, AbstractRenderer.prototype.events, {
            'click .o_filter_performance': '_onPerformanceFilterActionClicked',
            'click .o_record_state': '_onStateActionClicked',
        }),

        // to be used when going back using breadcrumb
        render_dashboards: function() {
            let values = self.state.data;
            console.log(self,"dash_rend")
            var dashboard = QWeb.render('logic_performance_tracker.dashboard_card_template', {
                values: values
            });
            this.updateState(self.state,false)
            // console.log(dashboard)
            // this.$el.empty()
            this.$el.html(dashboard)
            return $.when()

        },

        // to refetch data when using breadcrumb
        fetch_data: function(modelName){
            var def = this._rpc({
                model: 'performance.tracker', // Replace with your actual model name
                method: 'retrieve_dashboard_data', // Use 'search_read' to retrieve records
                args: [modelName], // Define search domain if needed
                // kwargs: {},
            }).then(function (data) {
                self.state = {'data':data,'model_name':modelName}
            }).catch(function(err){
                console.log(err)
            })
            return $.when(def)
        },

        // to use self globally between functions
        update_cp: function() {
            var self = this;
        },
        // execute when using breadcrumb
        on_reverse_breadcrumb : function(){
            // )
            var self = this;

            // Save the current state
            var currentState = _.extend({}, this.state);
        
            console.log("Current State:", currentState);
            // console.log("state",self.state)

        
            web_client.do_push_state({});
            // this.update_cp()
            this.fetch_data(this.state.model_name).then(function(){
                self.$el.empty()
                // console.log("state",self.state)
                // self.updateState(self.state,false)
                self.render_dashboards();
            });
        
            // this.controller.reloadData(this.state.model_name).then(function(data){
            //     this.updateState(data)
            //     this._render()
            // })
            // console.log("State after push:", this.state);
        
            // this.render_dashboards(currentState);

            
                // this.render_dashboards();
        },

        _onPerformanceFilterActionClicked: function (ev) {
            if (!self)
            {
                var self = this;

            }
            console.log(self,"self", "this",this)

            // Get the date field's value
            var fromDate = this.$('.from_date').val();
            var endDate = this.$('.end_date').val();

            console.log(fromDate)
            console.log(endDate)
            // this.$(".date_val").text(fromDate)
            self.state.data.dates = {}
            self.state.data.dates.fromDate = fromDate
            self.state.data.dates.endDate = endDate

            this._rpc({
                model: 'digital.executive.performance', // Replace with your actual model name
                method: 'action_executive_performance', // Use 'search_read' to retrieve records
                args: [
                    fromDate,endDate
                ], // Define search domain if needed
                // kwargs: {},
            }).then(function (performances) {
                // Set the state with the retrieved data
                self.state.data.performances = performances
                self.updateState(self.state,false)
                console.log(self.renderer)
            }).catch(function(err){
                console.log(err)
            });

            // this.updateState(self.state,false)
        },

        _onStateActionClicked: function (ev) {
            let record_state = $(ev.currentTarget).find('.state').text()
            var self = this
            console.log(this)
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            var action = {
                type: 'ir.actions.act_window',
                name: self.state.model_name,
                res_model: self.state.model_name,
                views: [[false, 'list'],[false,'form']],
                // view_type: 'tree',
                view_mode: 'tree,form',
                domain: [['state','=',record_state]],
                // target: 'main',
                target: 'current',
                // nodestroy: true
                // context: {'no_breadcrumbs': true},
            }
            return self.do_action(action,options);
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
            let values = this.state.data;
            if (values!==undefined && values.dates===undefined){
                values.dates  = {fromDate:"",endDate:""}
            }
            console.log("_render called")
            console.log(this)

            var digital_dashboard = QWeb.render('logic_performance_tracker.dashboard_card_template', {
                values: values
            });
            // this.$el.parent().find(".o_dashboard_card").remove();

            this.$el.html(digital_dashboard);
            if (values!==undefined && values.dates!==undefined){
                this.$(".from_date").val(values.dates.fromDate)
                this.$(".end_date").val(values.dates.endDate)
            }
                    
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
        
        // reloadData : function(modelName){
        //     console.log("reload method called")
        //     this._rpc({
        //         model: 'performance.tracker', // Replace with your actual model name
        //         method: 'retrieve_dashboard_data', // Use 'search_read' to retrieve records
        //         args: [modelName], // Define search domain if needed
        //         // kwargs: {},
        //     }).then(function (data) {
        //         return data
        //     }).catch(function(err){
        //         console.log(err)
        //     })
        // },
        start: function () {
            var self = this;
            var state = {}
            // self.state.dashboardValues = {'name':'babu','age':10};
            this._rpc({
                model: 'performance.tracker', // Replace with your actual model name
                method: 'retrieve_dashboard_data', // Use 'search_read' to retrieve records
                args: [self.modelName], // Define search domain if needed
                // kwargs: {},
            }).then(function (data) {
                // Set the state with the retrieved data
                state = {'data': data, 'model_name':self.modelName}
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