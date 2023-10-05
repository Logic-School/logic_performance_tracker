odoo.define('logic_performance_tracker.academic_dashboard', function (require) {
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

    var DashboardCardAction = AbstractAction.extend({

        xmlDependencies: ['/logic_performance_tracker/static/src/xml/academic_templates.xml',],
        
        events:{
            'click .o_filter_performance': '_onPerformanceFilterActionClicked',
            'click .o_filter_reset': 'filter_reset',
            'click .o_employee_name': '_onEmployeeNameClicked',

            // uncomment the below line to view records on clicking the card
            // 'click .o_model_count': '_onCardActionClicked',
        },
    
        init: function(parent, context) {
            this._super(parent, context);
            this.model_name = 'academic.tracker'
            this.data = {};
        },

        willStart: function(){
            var self = this;
            return this._super().then(function() {
                var def = self._rpc({
                    model: self.model_name, // Replace with your actual model name
                    method: 'retrieve_dashboard_data', // Use 'search_read' to retrieve records
                    args: [], // Define search domain if needed
                    // kwargs: {},
                }).then(function (data) {
                    self.data = data;
                }).catch(function(err){
                    console.log(err)
                })
                return $.when(def)
            });
        },

        start: function() {
    
            this._super.apply(this, arguments)
            this.render_dashboards()
        },

        render_dashboards: function() {
            // let values = self.state.data;
            // console.log(self,"dash_rend")
            var self = this
            console.log(this)
            var dashboard = QWeb.render('logic_performance_tracker.academic_dashboard_template', {
                values: this.data
            });
            // this.updateState(self.state,false)
            // console.log(dashboard)
            // this.$el.empty()
            this.$el.html(dashboard)
            return $.when()
    
        },

        _onEmployeeNameClicked: function (ev) {
            var self = this;
    
            // Get the date field's value
            var fromDate = this.$('.from_date').val();
            var endDate = this.$('.end_date').val();
            console.log("from",fromDate==="")
            console.log("To",endDate)
            var employee_id = $(ev.currentTarget).find(".o_employee_id").data("empid")
            console.log("hello",employee_id)
            var next_element = $(ev.currentTarget).next()
            
            if (next_element.attr("class")==='o_academic_data_subtable')
            {
                $(ev.currentTarget).next().remove(".o_academic_data_subtable")
            }
            else
            {
                this._rpc({
                    model: this.model_name, // Replace with your actual model name
                    method: 'retrieve_employee_academic_data', // Use 'search_read' to retrieve records
                    args: [
                        employee_id,fromDate,endDate
                    ], 
                    // Define search domain if needed
                    // kwargs: {},
                }).then(function (values) {
                    // Set the state with the retrieved data
                    console.log(values)
                    var coordinator_subdata = QWeb.render('logic_performance_tracker.academic_coordinator_data', {
                        values: values
                    });
                    $(ev.currentTarget).after(coordinator_subdata)
                    
                }).catch(function(err){
                    console.log(err)
                });
            }

        },

        _onPerformanceFilterActionClicked: function (ev) {
            var self = this;
    
            // Get the date field's value
            var fromDate = this.$('.from_date').val();
            var endDate = this.$('.end_date').val();
            var academic_head_id = this.$('.academic_head').val()
            if (academic_head_id==="all")
            {
                var fun_args = [fromDate,endDate]
            }
            else
            {
                var fun_args = [fromDate,endDate,academic_head_id]
            }
    
            console.log(fromDate)
            console.log(endDate)
            console.log(fun_args)
            // this.$(".date_val").text(fromDate)
            self.data.dates = {}
            self.data.dates.fromDate = fromDate
            self.data.dates.endDate = endDate
    
            this._rpc({
                model: this.model_name, // Replace with your actual model name
                method: 'retrieve_dashboard_data', // Use 'search_read' to retrieve records
                args: fun_args // Define search domain if needed
                // kwargs: {},
            }).then(function (data) {
                // Set the state with the retrieved data
                self.data = data
                self.render_dashboards()
                self.$(".from_date").val(fromDate)
                self.$(".end_date").val(endDate)
                self.$(".academic_head").val(academic_head_id)

                // self.updateState(self.state,false)
                // console.log(self.renderer)
            }).catch(function(err){
                console.log(err)
            });
            
            // this.updateState(self.state,false)
        },

        fetch_data: function(){
            console.log("fetch",this)
            var self = this
            var def = this._rpc({
                model: this.model_name, // Replace with your actual model name
                method: 'retrieve_dashboard_data', // Use 'search_read' to retrieve records
                args: [], // Define search domain if needed
                // kwargs: {},
            }).then(function (data) {
                self.data = data;
            }).catch(function(err){
                console.log(err)
            })
            return $.when(def)
        },

        update_cp: function() {
            var self = this;
        },

        filter_reset : function(){
            var self = this;
    
            // Save the current state
            var currentState = _.extend({}, this.state);
        
            console.log("Current State:", currentState);
            // console.log("state",self.state)
    
        
            web_client.do_push_state({});
            this.update_cp()
            this.fetch_data().then(function(){
                self.$el.empty()
                console.log(self.data,"datat")
                // console.log("state",self.state)
                // self.updateState(self.state,false)
                self.render_dashboards();
            });
        },

        on_reverse_breadcrumb : function(){
            // )
            var self = this;
    
            // Save the current state
            var currentState = _.extend({}, this.state);
        
            console.log("Current State:", currentState);
            // console.log("state",self.state)
    
        
            web_client.do_push_state({});
            this.update_cp()
            this.fetch_data().then(function(){
                self.$el.empty()
                console.log(self.data,"datat")
                // console.log("state",self.state)
                // self.updateState(self.state,false)
                self.render_dashboards();
            });
        
        },

        _onCardActionClicked: function (ev) {
            // let record_state = $(ev.currentTarget).find('.state').text()
            // let state_title = $(ev.currentTarget).find('.stat-title').text()
            let model_title = $(ev.currentTarget).find('.model-title').text()
            let model_name = $(ev.currentTarget).find('.model_name').text()

            var self = this
            console.log(this)
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            var action = {
                type: 'ir.actions.act_window',
                name: model_title,
                res_model: model_name,
                views: [[false, 'list'],[false,'form']],
                // view_type: 'tree',
                view_mode: 'tree,form',
                domain: [],
                // target: 'main',
                target: 'current',
                // nodestroy: true
                // context: {'no_breadcrumbs': true},
            }
            return self.do_action(action,options);
        },

        _render: function () {
            let values = this.data;
            console.log("_render called")
            console.log(this)
    
            var academic_dashboard = QWeb.render('logic_performance_tracker.academic_dashboard_template', {
                values: values
            });
            // this.$el.parent().find(".o_dashboard_card").remove();
    
            this.$el.html(academic_dashboard);
                    
                return $.when();
        },

    });
    core.action_registry.add('academic_dashboard', DashboardCardAction);
    return DashboardCardAction;
    
    })