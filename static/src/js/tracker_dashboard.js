odoo.define('logic_performance_tracker.tracker_dashboard', function (require) {
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
    // require('logic_performance_tracker/static/src/js/orgchart.js');
    const { useRef, useSubEnv } = hooks;

    var DashboardCardAction = AbstractAction.extend({
        xmlDependencies: [
            '/logic_performance_tracker/static/src/xml/tracker_dashboard_templates.xml',
            // '/logic_performance_tracker/static/src/xml/organizational_chart.xml'
        ],
        
        events:{
            // 'click .o_filter_performance': '_onPerformanceFilterActionClicked',
            // 'change .department_head': '_onPerformanceFilterActionClicked',
            // 'click .o_filter_reset': 'filter_reset',
            // 'click .o_employee_name': '_onEmployeeNameClicked',
            // 'click .node':'_onEmployeeNodeClicked',

            // uncomment the below line to view records on clicking the card
            'click .tracker_type_card': '_onCardActionClicked',
        },

        init: function(parent, context) {

            this._super(parent, context);
            this.model_name = 'performance.tracker'
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
            var dashboard = QWeb.render('logic_performance_tracker.tracker_dashboard_template', {
                values: this.data
            });
            this.$el.html(dashboard)

                // this.$(".org_chart_parent").append(org_chart)

            return $.when()
    
        },


        _onCardActionClicked: function (ev) {
            // let record_state = $(ev.currentTarget).find('.state').text()
            // let state_title = $(ev.currentTarget).find('.stat-title').text()
            var tracker_department_action = $(ev.currentTarget).attr('id')
            var department_name = $(ev.currentTarget).attr('name')

            var self = this
            console.log(this)
            var action = {
                type: 'ir.actions.client',
                name: department_name,
                // res_model: self.model_name,
                // view_type: 'tree',
                // target: 'main',
                tag: tracker_department_action,
                target: 'current',

            }
            return self.do_action(action,{'hello': true});
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
    core.action_registry.add('tracker_dashboard', DashboardCardAction);
    return DashboardCardAction;
    
    })
