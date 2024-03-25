from odoo import models,fields,api
from . import actions_common
from . import common_task_performance
from datetime import date

class CrashTracker(models.Model):
    _name = "crash.tracker"

    @api.model
    def retrieve_dashboard_data(self,start_date=False,end_date=False,manager_id=False):

        if start_date and end_date:
            start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)
            month = start_date.month
            year=start_date.year
        else:
            year = date.today().year
            month = date.today().month

        dashboard_data = {}
        employees_data = {}
        department_obj = self.env['hr.department'].sudo().search([('name','=','Crash')])

        if not manager_id:
            manager_id = department_obj.child_ids[0].manager_id.id

        manager,managers,department_heads_data = actions_common.get_manager_managers_heads_data(self,department_obj,manager_id)

        if manager or managers:
            employees = actions_common.get_employees(self,department_obj,manager,managers)
            employee_ids = employees.ids


        dashboard_data['department_heads'] = department_heads_data

        dashboard_data['qualitatives'] = actions_common.get_raw_qualitative_data(self,employees,start_date,end_date)
        dashboard_data['quantitatives'] = actions_common.get_raw_quantitative_data(self,employees,start_date,end_date)


        lead_sources = self.env['leads.sources'].sudo().search([])
        lead_source_names = lead_sources.mapped('name')

        for employee in employees:
            actions_common.create_employee_qualitative_performance(self,dashboard_data['qualitatives'],employee)
            actions_common.create_employee_quantitative_performance(self,dashboard_data['quantitatives'],employee)

            self.env['sales.tracker'].sudo().create_employee_leads_leaderboard_data(employee,start_date,end_date)

            self.env['logic.common.task.performance'].sudo().create_employee_common_task_performance(employee,start_date,end_date)
        
        dashboard_data['employee_ids'] = employee_ids
        dashboard_data['lead_sources'] = self.env['sales.tracker'].sudo().get_lead_sources_data()
        dashboard_data['common_task_performances'] = self.env['logic.common.task.performance'].sudo().get_employee_common_task_performances(employees)
        dashboard_data['qualitatives'],dashboard_data['qualitative_overall_averages'] = actions_common.get_ordered_qualitative_data(self,dashboard_data['qualitatives'],employees)    
        dashboard_data['quantitatives'],dashboard_data['quantitative_overall_averages'] = actions_common.get_ordered_quantitative_data(self,dashboard_data['quantitatives'],employees)

        dashboard_data['other_performances'] = actions_common.get_miscellaneous_performances(self,employees,start_date,end_date)
        dashboard_data['leads_performances'] = self.env['sales.tracker'].sudo().get_leads_leaderboard_data(employees)
        dashboard_data['month'] = actions_common.get_month_list().get(month).capitalize()
        dashboard_data['org_datas'],dashboard_data['dept_names'] = actions_common.get_org_datas_dept_names(manager,managers)

        if start_date and end_date:
            if start_date.month != end_date.month:
                dashboard_data['month'] = False
        dashboard_data['year'] = year

        return dashboard_data
    
    @api.model
    def retrieve_employee_all_source_wise_lead_data(self,employee_id,start_date=False,end_date=False):
        return self.env['sales.tracker'].sudo().retrieve_employee_all_source_wise_lead_data(employee_id,start_date,end_date)
    
    @api.model
    def get_sourcewise_charts_data(self,lead_source_id,employee_ids,start_date=False,end_date=False):
        return self.env['sales.tracker'].sudo().get_sourcewise_charts_data(self,lead_source_id,employee_ids,start_date,end_date)