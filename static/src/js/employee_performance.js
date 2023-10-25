odoo.define('logic_performance_tracker.employee_performance', function (require) {
    "use strict";
    
    const ActionMenus = require('web.ActionMenus');
    const ComparisonMenu = require('web.ComparisonMenu');
    const ActionModel = require('web/static/src/js/views/action_model.js');
    const FavoriteMenu = require('web.FavoriteMenu');
    const FilterMenu = require('web.FilterMenu');
    const GroupByMenu = require('web.GroupByMenu');
    const patchMixin = require('web.patchMixin');
    const Pager = require('web.Pager');
    const SearchBar = require('web.SearchBar');
    const { useModel } = require('web/static/src/js/model.js');
    
    const { Component, hooks } = owl;
    
    var concurrency = require('web.concurrency');
    var config = require('web.config');
    var field_utils = require('web.field_utils');
    var time = require('web.time');
    var utils = require('web.utils');
    var AbstractAction = require('web.AbstractAction');
    var ajax = require('web.ajax');
    var Dialog = require('web.Dialog');
    var field_utils = require('web.field_utils');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var web_client = require('web.web_client');
    var abstractView = require('web.AbstractView');
    var _t = core._t;
    var QWeb = core.qweb;

    const { useRef, useSubEnv } = hooks;
    
    var EmployeePerformanceAction = AbstractAction.extend({
    
        xmlDependencies: ['/logic_performance_tracker/static/src/xml/employee_performance_templates.xml'],
            
        events:{
            'click .model_record_card': '_onModelCardClickAction',
            'change .graph_year': '_onGraphYearChange',
            'click .o_filter_reset': 'filter_reset',
            'click .o_filter_performance': '_onPerformanceFilterActionClicked',

        },
    
        init: function(parent, context) {
            this._super(parent, context);
            console.log("context",context)
            this.LineChart1 = undefined
            this.line_chart_datasets = []
            this.employee_id = context.params.employee_id
            this.data = {};
        },
    
        willStart: function(){
            var self = this;
            return this._super().then(function() {
                var def = self._rpc({
                    model: 'logic.employee.performance', // Replace with your actual model name
                    method: 'retrieve_employee_performance', // Use 'search_read' to retrieve records
                    args: [self.employee_id], // Define search domain if needed
                    // kwargs: {},
                }).then(function (data) {
                    self.data = data;
                }).catch(function(err){
                    console.log(err)
                })
                return $.when(def)
            });
        },

        fetch_data: function(){
            var self = this;
            var def = self._rpc({
                model: 'logic.employee.performance', // Replace with your actual model name
                method: 'retrieve_employee_performance', // Use 'search_read' to retrieve records
                args: [self.employee_id], // Define search domain if needed
                // kwargs: {},
            }).then(function (data) {
                self.data = data;
            }).catch(function(err){
                console.log(err)
            })
            return $.when(def)
        },

        retrieve_line_chart_data: function(year){
            if(!year)
            {
                var curDate = new Date();
                var year = curDate.getFullYear();
            }
            var self = this;
                var def = self._rpc({
                    model: 'logic.employee.performance', // Replace with your actual model name
                    method: 'get_line_chart_datasets', // Use 'search_read' to retrieve records
                    args: [self.employee_id,year], // Define search domain if needed
                    // kwargs: {},
                }).then(function (data) {
                    self.line_chart_datasets = data;
                    self.render_line_chart();

                }).catch(function(err){
                    console.log(err)
                })
                return $.when(def)
        },

        start: function() {
    
            this._super.apply(this, arguments)
            console.log("action cont: ",this.action)
            this.render_dashboards()
            // retrieve line chart data and render it
            this.retrieve_line_chart_data()
            this.render_districtwise_leads_chart()
            // this.render_line_chart();
        },

        render_line_chart: function() {
            var self = this
            var data = {
                labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
                datasets: this.line_chart_datasets
            };

            // Configuration options
            var options = {

                responsive: true,
                maintainAspectRatio: false,

                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            };
            
            // var canvas2 = this.$('#LineChart2')

            // Create a new chart with jQuery
            var canvas_container = this.$('.linechart-canvas-container');
            canvas_container.empty()
            canvas_container.append('<canvas id="LineChart1" style="width:600px;height:350px;"></canvas>')
            var canvas1 = this.$('#LineChart1');
            this.LineChart1 = new Chart(canvas1, {
                type: 'line',
                data: data,
                options: options
            });

            // var LineChart2 = new Chart(canvas2, {
            //     type: 'line',
            //     data: data,
            //     options: options
            // });
        },

        render_districtwise_leads_chart: function() {
            var self = this
            if (this.data.leads_data)
            {
                console.log("inside if",this.data)
                var data = {
                    labels: this.data.leads_data['districts'],
                    datasets: this.data.leads_data['leads_dataset'],
                }
                // Configuration options
                var options = {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        title: {
                          display: true,
                          text: 'Seminar Leads'
                        },
                      },
                    scales: {
                        x: {
                            stacked: true,
                            },
                            y: {
                            beginAtZero: true,

                            stacked: true
                            }

                    }
                };
                

                // Create a new chart with jQuery
                var canvas_container = self.$('.districtchart-canvas-container');
                canvas_container.empty()
                canvas_container.append('<canvas id="districtWiseLeadChart" style="width:850px;height:500px;"></canvas>')
                var canvas1 = self.$('#districtWiseLeadChart');
                self.LineChart1 = new Chart(canvas1, {
                    type: 'bar',
                    data: data,
                    options: options
                });            



        }
        },

        _onPerformanceFilterActionClicked: function (ev) {
            var self = this;
    
            // Get the date field's value
            var fromDate = this.$('.from_date').val();
            var endDate = this.$('.end_date').val();
            if (fromDate=='' || endDate=='')
            {
                fromDate=false
                endDate=false
            }
            // var fun_args = [fromDate,endDate]

            // this.$(".date_val").text(fromDate)
    
            var self = this;
            var def = self._rpc({
                model: 'logic.employee.performance', // Replace with your actual model name
                method: 'retrieve_employee_performance', // Use 'search_read' to retrieve records
                args: [self.employee_id,fromDate,endDate], // Define search domain if needed
                // kwargs: {},
            }).then(function (data) {
                self.data = data;
                self.render_dashboards()
                // retrieve line chart data and render it
                self.retrieve_line_chart_data()
                self.render_districtwise_leads_chart()
                self.$(".from_date").val(fromDate)
                self.$(".end_date").val(endDate)
            }).catch(function(err){
                console.log(err)
            })

        },

        filter_reset : function(){
            var self = this;
    
            // Save the current state
            var currentState = _.extend({}, this.state);
        
            console.log("Current State:", currentState);
            // console.log("state",self.state)
    
        
            web_client.do_push_state({});
            this.fetch_data().then(function(){
                self.$el.empty()
                console.log(self.data,"datat")
                // console.log("state",self.state)
                // self.updateState(self.state,false)
                self.render_dashboards()
                // retrieve line chart data and render it
                self.retrieve_line_chart_data()
                self.render_districtwise_leads_chart()
            });
        },

        _onModelCardClickAction: function(ev) {
            var self = this;

            var model_name = $(ev.currentTarget).attr('id')
            var action_model_name = $(ev.currentTarget).attr('name')
            var fromDate = this.$('.from_date').val();
            var endDate = this.$('.end_date').val();
            console.log("fromDate",fromDate)
            console.log("endDate",endDate)
            if (fromDate=='' || endDate=='')
            {
                fromDate=false
                endDate=false
            }
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            var def = self._rpc({
                    model: 'logic.employee.performance', // Replace with your actual model name
                    method: 'model_records_open_action', // Use 'search_read' to retrieve records
                    args: [self.employee_id,model_name,fromDate,endDate], // Define search domain if needed
                    // kwargs: {},
                }).then(function (domain) {

                    var action = {
                        type: 'ir.actions.act_window',
                        name: action_model_name,
                        res_model: model_name,
                        view_type: 'tree',
                        target: 'main',
                        views: [[false, 'list'],[false,'form']],

                        // tag: 'employee_performance',
                        target: 'current',
                        // nodestroy: true
                        domain: domain,

                    }
                    self.do_action(action,options)
                }).catch(function(err){
                    console.log(err)
                })
                return $.when(def);
        },

        _onGraphYearChange: function(ev){

            var self = this;
            var selected_year = this.$('.graph_year').val();
            console.log(selected_year)
            self.retrieve_line_chart_data(selected_year)
        },


        render_dashboards: function() {
            var self = this
            console.log(this)
            var dashboard = QWeb.render('logic_performance_tracker.employee_performance_template', {
                values: this.data
            });
            this.$el.html(dashboard)
            return $.when()
        },

        _render: function () {
            let values = this.data;
            console.log("_render called")
            console.log(this)
            return $.when();
        },
    });
    core.action_registry.add('employee_performance', EmployeePerformanceAction);
    return EmployeePerformanceAction;
    
    })