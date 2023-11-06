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
    
        xmlDependencies: ['/logic_performance_tracker/static/src/xml/digital_templates.xml'],
            
        events:{
            'click .o_filter_performance': '_onPerformanceFilterActionClicked',
            'click .o_record_state': '_onStateActionClicked',
            'click .o_filter_reset': 'filter_reset',
            'click .node': '_onEmployeeNodeClicked',
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
            this.render_state_chart()
            this.render_organisation_chart()

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
                self.render_state_chart();
                self.render_organisation_chart()
            });
        },

        render_state_chart:function(){
            var self = this;
            var w = 200;
            var h = 200;
            var r = h/2;
            var elem = this.$('.state_pie_chart');
    //        var colors = ['#ff8762', '#5ebade', '#b298e1', '#70cac1', '#cf2030'];
            var colors = ['#FFD700', '#70cac1', '#9370DB', '#FF8C00', '#006400', '#696969', '#191970', '#fe7139',
            '#ffa433', '#ffc25b', '#f8e54b'];
            var color = d3.scale.ordinal().range(colors);
            var segColor = {};
            var data= this.data['states_data']
            var vis = d3.select(elem[0]).append("svg:svg").data([data]).attr("width", w).attr("height", h).append("svg:g").attr("transform", "translate(" + r + "," + r + ")");
            var pie = d3.layout.pie().value(function(d){return d.value;});
            var arc = d3.svg.arc().outerRadius(r);
            var arcs = vis.selectAll("g.slice").data(pie).enter().append("svg:g").attr("class", "slice");
            arcs.append("svg:path")
                .attr("fill", function(d, i){
                    return color(i);
                })
                .attr("d", function (d) {
                    return arc(d);
                });

            var legend = d3.select(elem[0]).append("table").attr('class','legend');

            // create one row per segment.
            var tr = legend.append("tbody").selectAll("tr").data(data).enter().append("tr");

            // create the first column for each segment.
            tr.append("td").append("svg").attr("width", '16').attr("height", '16').append("rect")
                .attr("width", '16').attr("height", '16')
                .attr("fill",function(d, i){ return color(i) });

            // create the second column for each segment.
            tr.append("td").text(function(d){ return d.label;});

            // create the third column for each segment.
            tr.append("td").attr("class",'legendFreq')
                .text(function(d){ return d.value;});
    
        
        },

        render_organisation_chart: function(){
            this.$(".organisation_charts").empty()
            var org_datas = this.data['org_datas']
            console.log(org_datas)
            console.log(Object.keys(this.data['org_datas']).length)
            for(let i=0; i<Object.keys(this.data['org_datas']).length; i++)
            {
                this.$(".organisation_charts").append($("<div id=chart-container-"+i+"></div>"))
                this.$("#chart-container-"+i).addClass("chart-container col m-3")
                var oc = this.$("#chart-container-"+i).orgchart({
                    exportButton: false,
                    exportFilename: "MyOrgChart",
                    data: org_datas[i],
                    nodeContent: "title",
                    nodeID: "id",
                    createNode: function ($node, data) {
                        if (data.image!==undefined){
                            $node.find(".title").append(`
                            <img class="avatar" src="data:image/png;base64,${data.image}" crossorigin="anonymous" />
                            `);
                        }
                    }
                });
            }
            return $.when()

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
                self.render_organisation_chart()
                self.render_state_chart()

            });
        
        },
    
        _onPerformanceFilterActionClicked: function (ev) {
            var self = this;
    
            // Get the date field's value
            var fromDate = this.$el.find('.from_date').val();
            var endDate = this.$('.end_date').val();
    
            console.log("from_date",fromDate)
            console.log("end_date",endDate)
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
                self.render_state_chart()
                self.render_organisation_chart()


                self.$(".from_date").val(fromDate)
                self.$(".end_date").val(endDate)
                // self.updateState(self.state,false)
                // console.log(self.renderer)
            }).catch(function(err){
                console.log(err)
            });
    
            // this.updateState(self.state,false)
        },

        _onEmployeeNodeClicked: function (ev){
            var self = this
            let emp_id = $(ev.currentTarget).attr('id')
            let emp_name = 
            console.log("empt id: ",emp_id)
            this._rpc({
                model: "logic.employee.performance", // Replace with your actual model name
                method: 'get_employee_details', // Use 'search_read' to retrieve records
                args: [emp_id]
            }).then(function (employee) {
            var action = {
                type: 'ir.actions.client',
                name: employee.name,
                // res_model: self.model_name,
                // view_type: 'tree',
                // target: 'main',
                tag: 'employee_performance',
                target: 'current',
                // nodestroy: true
                params: {'employee_id': emp_id},
                context: {'hello1': true},

            }
            return self.do_action(action,{'hello': true});
        }).catch(function(err){
            console.log(err)
        })
        },
    
        _onStateActionClicked: function (ev) {
            let record_state = $(ev.currentTarget).find('.state').text()
            let state_title = $(ev.currentTarget).find('.stat-title').text()
            var self = this
            console.log(this)
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            var action = {
                type: 'ir.actions.act_window',
                name: "Digital Tasks: "+state_title,
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