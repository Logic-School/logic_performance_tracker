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

        xmlDependencies: ['/logic_performance_tracker/static/src/xml/employee_performance_templates.xml','/logic_performance_tracker/static/src/xml/batch_data_templates.xml'],

        events: {
            'click .model_record_card': '_onModelCardClickAction',
            // 'change .graph_year': '_onGraphYearChange',
            'click .o_filter_reset': 'filter_reset',
            'click .o_filter_performance': '_onPerformanceFilterActionClicked',
            'change .department_employee': '_onSelectedEmployeeChanged',
            'change .academic_batch': 'render_academic_batch_data_summary',
            'change .academic_window': 'render_academic_batch_list',
        },

        init: function (parent, context) {
            this._super(parent, context);
            console.log("context", context)
            this.LineChart1 = undefined
            this.line_chart_datasets = []
            this.employee_id = context.params.employee_id
            this.start_date = context.context.start_date
            this.end_date = context.context.end_date

            this.data = {};
        },

        willStart: function () {
            var self = this;
            console.log("this.employee_id",this.employee_id)
            return this._super().then(function () {
                var def = self._rpc({
                    model: 'logic.employee.performance', // Replace with your actual model name
                    method: 'retrieve_employee_performance', // Use 'search_read' to retrieve records
                    args: [self.employee_id, self.start_date, self.end_date], // Define search domain if needed
                    // kwargs: {},
                }).then(function (data) {
                    self.data = data;

                }).catch(function (err) {
                    console.log(err)
                })
                return $.when(def)
            });
        },

        fetch_data: function () {
            var self = this;
            var def = self._rpc({
                model: 'logic.employee.performance', // Replace with your actual model name
                method: 'retrieve_employee_performance', // Use 'search_read' to retrieve records
                args: [self.employee_id, self.start_date, self.end_date], // Define search domain if needed
                // kwargs: {},
            }).then(function (data) {
                self.data = data;
            }).catch(function (err) {
                console.log(err)
            })
            return $.when(def)
        },

        _onSelectedEmployeeChanged: function (ev) {
            var self = this
            var fromDate = this.$('.from_date').val();
            var endDate = this.$('.end_date').val();

            if (fromDate == '' || endDate == '') {
                fromDate = false
                endDate = false
            }

            let emp_id = $(ev.currentTarget).val()
            console.log("empt id: ", emp_id)
            this._rpc({
                model: "logic.employee.performance", // Replace with your actual model name
                method: 'get_employee_details', // Use 'search_read' to retrieve records
                args: [emp_id]
            }).then(function (employee) {
                var action = {
                    type: 'ir.actions.client',
                    name: employee.name,
                    tag: 'employee_performance',
                    target: 'main',
                    // clear_breadcrumb: true,

                    // nodestroy: true
                    params: { 'employee_id': emp_id },
                    context: { 'start_date': fromDate, 'end_date': endDate },

                }
                return self.do_action(action, { 'hello': true });
            }).catch(function (err) {
                console.log(err)
            })
        },

        start: function () {

            this._super.apply(this, arguments)
            console.log("action cont: ", this.action)
            this.render_dashboards()
            // retrieve line chart data and render it
            this.render_line_chart()
            this.render_districtwise_leads_chart()
            this.render_sourcewise_leads_chart();
            this.render_coursewise_leads_chart()
            this.render_academic_batch_list()
            this.render_academic_batch_data_summary();
            // this.render_line_chart();
        },

        render_academic_batch_list: function(){
            var self = this;
            if (self.data.academic_data) {
                var academic_window = self.$('.academic_window').val()
                if (academic_window==='')
                {
                    academic_window = false;
                }
                var def = self._rpc({
                    model: 'logic.employee.performance', // Replace with your actual model name
                    method: 'get_employee_academic_batches', // Use 'search_read' to retrieve records
                    args: [self.employee_id,academic_window], // Define search domain if needed        },
                }).then(function (data){
                    self.$('.academic_batches_list').empty()
                    console.log("batch list",data,academic_window)
                    var academic_batches =  QWeb.render('logic_performance_tracker.academic_batches_template', {
                        batches: data
                    });
                    self.$('.academic_batches_list').append(academic_batches)

                    var sub_div_elem = self.$('.academic_batch_data_sub_div')
                    if(sub_div_elem)
                    {
                        sub_div_elem.remove()
                    }

                    self.render_academic_batch_data_summary()
                }).catch(function(err){
                    console.log(err)
                })
            }
        },

        render_academic_batch_data_summary: function () {
            var self = this;
            if (self.data.academic_data) {
                var batch_id = self.$('.academic_batch').val()
                if (batch_id)
                {
                var def = self._rpc({
                    model: 'logic.employee.performance', // Replace with your actual model name
                    method: 'get_academic_batch_data', // Use 'search_read' to retrieve records
                    args: [batch_id], // Define search domain if needed
                    // kwargs: {},
                }).then(function (data) {
                    var sub_div_elem = self.$('.academic_batch_data_sub_div')
                    if(sub_div_elem)
                    {
                        sub_div_elem.remove()
                    }
                    var academic_batch_data = QWeb.render('logic_performance_tracker.batch_data_template', {
                        values: data
                    });
                    self.$('.academic_batch_data').append(academic_batch_data)
                    console.log('batch data: ',data)
                    self.$(".upaya_attended").progressbar({
                        value: data.upaya_data.attended_count,
                        max: data.batch_strength,
                        classes: {
                            "ui-progressbar": "highlight"
                        }
                    })
                    self.$(".upaya_attended").find('.ui-progressbar-value').html(`<div class='d-flex justify-content-center'><span>${data.upaya_data.attended_count} / ${data.batch_strength}</span></div>`)
                   
                    self.$(".yes_plus_average").progressbar({
                        value: data.yes_plus_data.average_attendance,
                        max: data.batch_strength,
                        classes: {
                            "ui-progressbar": "highlight"
                        }
                    })
                    self.$(".yes_plus_average").find('.ui-progressbar-value').html(`<div class='d-flex justify-content-center'><span>${data.yes_plus_data.average_attendance} / ${data.batch_strength}</span></div>`)


                    self.$(".presentation_attended").progressbar({
                        value: data.presentation_data.presented_count,
                        max: data.batch_strength,
                        classes: {
                            "ui-progressbar": "highlight"
                        }
                    })
                    self.$(".presentation_attended").find('.ui-progressbar-value').html(`<div class='d-flex justify-content-center'><span>${data.presentation_data.presented_count} / ${data.batch_strength}</span></div>`)
                   
                    self.$(".one_to_one_attended").progressbar({
                        value: data.one_to_one_data.total_conducted,
                        max: data.batch_strength,
                        classes: {
                            "ui-progressbar": "highlight"
                        }
                    })
                    self.$(".one_to_one_attended").find('.ui-progressbar-value').html(`<div class='d-flex justify-content-center'><span>${data.one_to_one_data.total_conducted} / ${data.batch_strength}</span></div>`)
                   
                    
                    self.$(".cip_average").progressbar({
                        value: data.cip_data.average_attendance,
                        max: data.batch_strength,
                        classes: {
                            "ui-progressbar": "highlight"
                        }
                    })
                    self.$(".cip_average").find('.ui-progressbar-value').html(`<div class='d-flex justify-content-center'><span>${data.cip_data.average_attendance} / ${data.batch_strength}</span></div>`)

                    self.$(".excel_average").progressbar({
                        value: data.excel_data.average_attendance,
                        max: data.batch_strength,
                        classes: {
                            "ui-progressbar": "highlight"
                        }
                    })
                    self.$(".excel_average").find('.ui-progressbar-value').html(`<div class='d-flex justify-content-center'><span>${data.excel_data.average_attendance} / ${data.batch_strength}</span></div>`)

                    self.$(".bb_average").progressbar({
                        value: data.bb_data.attendance,
                        max: data.batch_strength,
                        classes: {
                            "ui-progressbar": "highlight"
                        }
                    })
                    self.$(".bb_average").find('.ui-progressbar-value').html(`<div class='d-flex justify-content-center'><span>${data.bb_data.attendance} / ${data.batch_strength}</span></div>`)

                    self.$(".mock_average").progressbar({
                        value: data.mock_interview_data.total_conducted,
                        max: data.batch_strength,
                        classes: {
                            "ui-progressbar": "highlight"
                        }
                    })
                    self.$(".mock_average").find('.ui-progressbar-value').html(`<div class='d-flex justify-content-center'><span>${data.mock_interview_data.total_conducted} / ${data.batch_strength}</span></div>`)

                    self.$(".attendance_average").progressbar({
                        value: data.attendance_data.average_attendance,
                        max: data.batch_strength,
                        classes: {
                            "ui-progressbar": "highlight"
                        }
                    })
                    self.$(".attendance_average").find('.ui-progressbar-value').html(`<div class='d-flex justify-content-center'><span>${data.attendance_data.average_attendance} / ${data.batch_strength}</span></div>`)
                
                    var data = {
                        labels: ['Pass (%)'],
                        datasets: data.exam_data.exam_datasets
                    };
                    // Configuration options
                    var options = {
                        responsive: true,
                        maintainAspectRatio: false,
                        // scales: {
                        //     x: {
                        //         stacked: true,
                        //         },
                        //     y: {
                        //         beginAtZero: true,
        
                        //         stacked: true
                        //     }
        
                        // },
                        plugins: {
                            title: {
                                display: true,
                                text: 'Exam Data'
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    };

                    var canvas_container = self.$('.examchart-canvas-container');
                    canvas_container.empty()
                    canvas_container.append('<canvas id="ExamChart1" style="width:600px;height:350px;"></canvas>')
                    var canvas1 = self.$('#ExamChart1');
                    self.LineChart1 = new Chart(canvas1, {
                        type: 'bar',
                        data: data,
                        options: options
                    });

                }).catch(function(err){
                    console.log(err)
                });
            }

            }
        },

        render_line_chart: function () {
            var self = this

            var data = {
                labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
                datasets: this.data.misc_to_do_chart_dataset
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

        render_districtwise_leads_chart: function () {
            var self = this
            if (this.data.marketing_data) {
                console.log("inside if", this.data)
                var data = {
                    labels: this.data.marketing_data['districts'],
                    datasets: this.data.marketing_data['leads_dataset'],
                }
                // Configuration options
                var options = {
                    responsive: true,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    stacked: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Seminar Leads'
                        }
                    },
                    scales: {
                        leads_count: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            beginAtZero: true,

                        },
                        conversion_rates: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            beginAtZero: true,


                            // grid line settings
                            grid: {
                                drawOnChartArea: false, // only want the grid lines for one axis to show up
                            },
                        },
                    }
                }


                // Create a new chart with jQuery
                var canvas_container = self.$('.districtchart-canvas-container');
                canvas_container.empty()
                canvas_container.append('<canvas id="districtWiseLeadChart" style="width:850px;height:500px;"></canvas>')
                var canvas1 = self.$('#districtWiseLeadChart');
                self.LineChart1 = new Chart(canvas1, {
                    type: 'line',
                    data: data,
                    options: options
                });



            }
        },

        render_sourcewise_leads_chart: function () {
            var self = this
            if (this.data.sales_data) {
                console.log("inside if", this.data)
                var data = {
                    labels: this.data.sales_data['lead_sources'],
                    datasets: this.data.sales_data['sourcewise_leads_dataset'],
                }
                // Configuration options
                var options = {
                    responsive: true,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    stacked: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Leads (By Source)' + (self.data.month ? ' '+self.data.month+' '+self.data.year : '')
                        }
                    },
                    scales: {
                        leads_count: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            beginAtZero: true,

                        },
                        conversion_rates: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            beginAtZero: true,


                            // grid line settings
                            grid: {
                                drawOnChartArea: false, // only want the grid lines for one axis to show up
                            },
                        },
                    }
                }


                // Create a new chart with jQuery
                var canvas_container = self.$('.sourcechart-canvas-container');
                canvas_container.empty()
                canvas_container.append('<canvas id="sourceWiseLeadChart" style="width:850px;height:500px;"></canvas>')
                var canvas1 = self.$('#sourceWiseLeadChart');
                self.LineChart1 = new Chart(canvas1, {
                    type: 'bar',
                    data: data,
                    options: options
                });



            }
        },

        render_coursewise_leads_chart: function () {
            var self = this
            if (this.data.sales_data) {
                console.log("inside if", this.data)
                var data = {
                    labels: this.data.sales_data['lead_courses'],
                    datasets: this.data.sales_data['coursewise_leads_dataset'],
                }
                // Configuration options
                var options = {
                    responsive: true,
                    interaction: {
                        mode: 'index',
                        intersect: false,
                    },
                    stacked: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Leads (By Course)' + (self.data.month ? ' '+self.data.month+' '+self.data.year : '')
                        }
                    },
                    scales: {
                        leads_count: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            beginAtZero: true,

                        },
                        conversion_rates: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            beginAtZero: true,


                            // grid line settings
                            grid: {
                                drawOnChartArea: false, // only want the grid lines for one axis to show up
                            },
                        },
                    }
                }


                // Create a new chart with jQuery
                var canvas_container = self.$('.coursechart-canvas-container');
                canvas_container.empty()
                canvas_container.append('<canvas id="courseWiseLeadChart" style="width:850px;height:500px;"></canvas>')
                var canvas1 = self.$('#courseWiseLeadChart');
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
            if (fromDate == '' || endDate == '') {
                fromDate = false
                endDate = false
            }
            // var fun_args = [fromDate,endDate]

            // this.$(".date_val").text(fromDate)

            var self = this;
            var def = self._rpc({
                model: 'logic.employee.performance', // Replace with your actual model name
                method: 'retrieve_employee_performance', // Use 'search_read' to retrieve records
                args: [self.employee_id, fromDate, endDate], // Define search domain if needed
                // kwargs: {},
            }).then(function (data) {
                self.data = data;
                self.render_dashboards()
                // retrieve line chart data and render it
                self.render_line_chart()
                self.render_districtwise_leads_chart()
                self.render_sourcewise_leads_chart();
                self.render_coursewise_leads_chart()
                self.render_academic_batch_list()

                self.render_academic_batch_data_summary();

                self.$(".from_date").val(fromDate)
                self.$(".end_date").val(endDate)
            }).catch(function (err) {
                console.log(err)
            })

        },

        filter_reset: function () {
            var self = this;
            self.start_date = false
            self.end_date = false
            // Save the current state
            var currentState = _.extend({}, this.state);

            console.log("Current State:", currentState);
            // console.log("state",self.state)


            web_client.do_push_state({});
            this.fetch_data().then(function () {
                self.$el.empty()
                console.log(self.data, "datat")
                // console.log("state",self.state)
                // self.updateState(self.state,false)
                self.render_dashboards()
                // retrieve line chart data and render it
                self.render_line_chart()
                self.render_districtwise_leads_chart()
                self.render_sourcewise_leads_chart()
                self.render_coursewise_leads_chart()
                self.render_academic_batch_list()

                self.render_academic_batch_data_summary();

            });
        },

        _onModelCardClickAction: function (ev) {
            var self = this;

            var model_name = $(ev.currentTarget).attr('id')
            var action_model_name = $(ev.currentTarget).attr('name')
            var fromDate = this.$('.from_date').val();
            var endDate = this.$('.end_date').val();
            console.log("fromDate", fromDate)
            console.log("endDate", endDate)
            if (fromDate == '' || endDate == '') {
                fromDate = false
                endDate = false
            }
            var options = {
                on_reverse_breadcrumb: this.on_reverse_breadcrumb,
            };
            var def = self._rpc({
                model: 'logic.employee.performance', // Replace with your actual model name
                method: 'model_records_open_action', // Use 'search_read' to retrieve records
                args: [self.employee_id, model_name, fromDate, endDate], // Define search domain if needed
                // kwargs: {},
            }).then(function (domain) {

                var action = {
                    type: 'ir.actions.act_window',
                    name: action_model_name,
                    res_model: model_name,
                    view_type: 'tree',
                    target: 'main',
                    views: [[false, 'list'], [false, 'form']],

                    // tag: 'employee_performance',
                    target: 'current',
                    // nodestroy: true
                    domain: domain,

                }
                self.do_action(action, options)
            }).catch(function (err) {
                console.log(err)
            })
            return $.when(def);
        },

        // _onGraphYearChange: function(ev){

        //     var self = this;
        //     var selected_year = this.$('.graph_year').val();
        //     console.log(selected_year)
        //     self.retrieve_line_chart_data(selected_year)
        // },


        render_dashboards: function () {
            var self = this
            console.log(this)
            var dashboard = QWeb.render('logic_performance_tracker.employee_performance_template', {
                values: this.data
            });
            this.$el.html(dashboard)
            if (self.start_date && self.end_date) {
                self.$(".from_date").val(self.start_date)
                self.$(".end_date").val(self.end_date)
            }
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