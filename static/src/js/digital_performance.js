odoo.define('logic_performance_tracker.digital_dashboard', function (require) {
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

    // template: 'logic_performance_tracker.dashboard_card_template',
    xmlDependencies: ['/logic_performance_tracker/static/src/xml/digital_templates.xml'],
        
    events:{
        'click .o_filter_performance': '_onPerformanceFilterActionClicked',
        'click .o_record_state': '_onStateActionClicked',
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.model_name = 'digital.task'
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
        // console.log("hello")

        this._super.apply(this, arguments)
        this.render_dashboards()
    },

    render_dashboards: function() {
        // let values = self.state.data;
        // console.log(self,"dash_rend")
        var self = this
        console.log(this)
        var dashboard = QWeb.render('logic_performance_tracker.digital_dashboard_template', {
            values: this.data
        });
        // this.updateState(self.state,false)
        // console.log(dashboard)
        // this.$el.empty()
        this.$el.html(dashboard)
        return $.when()

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

    // to use self globally between functions
    update_cp: function() {
        var self = this;
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

    _onPerformanceFilterActionClicked: function (ev) {
        var self = this;

        // Get the date field's value
        var fromDate = this.$('.from_date').val();
        var endDate = this.$('.end_date').val();

        console.log(fromDate)
        console.log(endDate)
        // this.$(".date_val").text(fromDate)
        self.data.dates = {}
        self.data.dates.fromDate = fromDate
        self.data.dates.endDate = endDate

        this._rpc({
            model: this.model_name, // Replace with your actual model name
            method: 'retrieve_dashboard_data', // Use 'search_read' to retrieve records
            args: [
                fromDate,endDate
            ], // Define search domain if needed
            // kwargs: {},
        }).then(function (data) {
            // Set the state with the retrieved data
            self.data = data
            self.render_dashboards()
            self.$(".from_date").val(fromDate)
            self.$(".end_date").val(endDate)
            // self.updateState(self.state,false)
            // console.log(self.renderer)
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
            name: self.model_name,
            res_model: self.model_name,
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


    _render: function () {
        let values = this.data;
        console.log("_render called")
        console.log(this)

        var digital_dashboard = QWeb.render('logic_performance_tracker.digital_dashboard_template', {
            values: values
        });
        // this.$el.parent().find(".o_dashboard_card").remove();

        this.$el.html(digital_dashboard);
                
            return $.when();
    },

});
core.action_registry.add('digital_dashboard', DashboardCardAction);
return DashboardCardAction;

})
