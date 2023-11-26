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
    // require('logic_performance_tracker/static/src/js/orgchart.js');
    const { useRef, useSubEnv } = hooks;

    var DashboardCardAction = AbstractAction.extend({

        // template: 'logic_performance_tracker.academic_dashboard_template',

        xmlDependencies: [
            '/logic_performance_tracker/static/src/xml/academic_templates.xml',
            '/logic_performance_tracker/static/src/xml/report_templates/academic_report_templates.xml',

            // '/logic_performance_tracker/static/src/xml/organizational_chart.xml'
        ],
        
        events:{
            'click .o_filter_performance': '_onPerformanceFilterActionClicked',
            'change .department_head': '_onPerformanceFilterActionClicked',
            'click .o_filter_reset': 'filter_reset',
            'click .o_employee_name': '_onEmployeeNameClicked',
            'click .node':'_onEmployeeNodeClicked',
            'click .report_download_btn': '_downloadPDFReport',


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
            this.render_organisation_chart()
        },


        render_organisation_chart: function(){
            this.$(".organisation_charts").empty()
            var acad_org_datas = this.data['org_datas']
            var dept_names = this.data['dept_names']
            console.log(acad_org_datas)
            console.log(Object.keys(this.data['org_datas']).length)
            for(let i=0; i<Object.keys(this.data['org_datas']).length; i++)
            {
                this.$(".organisation_charts").append($("<div id=chart-container-"+i+"></div>"))
                this.$("#chart-container-"+i).addClass("chart-container col m-3")
                this.$("#chart-container-"+i).append($("<div class='tracker-heading1 mt-3'><h2 class=text-center text-info>"+dept_names[i]+"</h2></div>"))

                var oc = this.$("#chart-container-"+i).orgchart({
                    exportButton: false,
                    exportFilename: "MyOrgChart",
                    verticalLevel: 5,
                    horizontalLevel:2,
                    data: acad_org_datas[i],
                    nodeContent: "title",
                    nodeID: "id",
                    createNode: function ($node, data) {
                    if (data.image!==undefined){
                        $node.find(".title").append(`
                        <img class="avatar" src="data:image/png;base64,${data.image}" crossorigin="anonymous" />
                        `);
                    }
                    // $node.find(".content").prepend($node.find(".symbol"));
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
            var dashboard = QWeb.render('logic_performance_tracker.academic_dashboard_template', {
                values: this.data
            });
            this.$el.html(dashboard)

                // this.$(".org_chart_parent").append(org_chart)

            return $.when()
    
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

        _onEmployeeNameClicked: function (ev) {
            var self = this;
    
            // Get the date field's value
            var fromDate = this.$('.from_date').val();
            var endDate = this.$('.end_date').val();
            console.log("from",fromDate==="")
            console.log("To",endDate)
            if(fromDate=='' || endDate=='')
            {
                fromDate=false;
                endDate=false;
            }
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
            var department_head_id = this.$('.department_head').val()
            if (department_head_id==="all")
            {
                var fun_args = [fromDate,endDate]
            }
            else
            {
                var fun_args = [fromDate,endDate,department_head_id]
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
                self.render_organisation_chart()
                self.$(".from_date").val(fromDate)
                self.$(".end_date").val(endDate)
                self.$(".department_head").val(department_head_id)

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
                self.render_organisation_chart()
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
                self.render_organisation_chart()
            });
        
        },

        _downloadPDFReport: function(){
            self = this;
            var fromDate = this.$('.from_date').val();
            var endDate = this.$('.end_date').val();
            var department_head_id = this.$('.department_head').val()

            if (fromDate == '' || endDate == '') {
                fromDate = false
                endDate = false
            }
            var def = self._rpc({
                model: 'academic.tracker', // Replace with your actual model name
                method: 'get_academic_performance_report_data', // Use 'search_read' to retrieve records
                args: [fromDate, endDate, department_head_id], // Define search domain if needed
                // kwargs: {},
            }).then(function(academic_data){
                var report_template = QWeb.render('logic_performance_tracker.academic_report_template',{'values':academic_data})
                console.log(academic_data)
                console.log(report_template)
                self._rpc({
                    model: 'performance.tracker', // Replace with your actual model name
                    method: 'get_performance_report_pdf', // Use 'search_read' to retrieve records
                    args: [report_template,'Marketing Performance'], 
                }).then(function(pdf_data){
                    var link = `data:application/pdf;base64, ${pdf_data.pdf_b64}`
                    console.log(link)
                    self.$('.o_dashboard_card').append("<a id='report_download' target='_blank'><a/>")
                    var download_link = self.$('#report_download')
                    download_link.attr('href',link)
                    download_link.attr('download',pdf_data.filename)
                    console.log(download_link[0])
                    download_link[0].click()
                    download_link.remove()
                    // download_link.remove()
                    // window.open('data:application/pdf;base64, '+pdf_file)
                }).catch(function(err){
                    console.log(err)
                })
            }).catch(function(err){
                console.log(err)
            })
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