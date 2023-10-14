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

        },
    
        init: function(parent, context) {
            this._super(parent, context);
            console.log("context",context)
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

        start: function() {
    
            this._super.apply(this, arguments)
            console.log("action cont: ",this.action)

            this.render_dashboards()
        },

        _onModelCardClickAction: function(ev) {
            var model_name = $(ev.currentTarget).attr('id')
            var action_model_name = $(ev.currentTarget).attr('name')
            var self = this;
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            var def = self._rpc({
                    model: 'logic.employee.performance', // Replace with your actual model name
                    method: 'model_records_open_action', // Use 'search_read' to retrieve records
                    args: [self.employee_id,model_name], // Define search domain if needed
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