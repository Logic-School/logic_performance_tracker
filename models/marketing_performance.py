from odoo import models,fields,api
import logging
from . import actions_common
class MarketingTracker(models.Model):
    _name="marketing.tracker"

    @api.model
    def retrieve_dashboard_data(self,start_date=False,end_date=False,manager_id=False):
        logger = logging.getLogger("Debugger: ")
        dashboard_data = {}
        department_obj = self.env['hr.department'].sudo().search([('name','=','Marketing')])
        manager,managers,department_heads_data = actions_common.get_manager_managers_heads_data(self,department_obj,manager_id)
        dashboard_data['department_heads'] = department_heads_data
        if manager or managers:
            employees = actions_common.get_employees(self,department_obj,manager,managers)
            employee_user_ids = employees.mapped('user_id.id')

        dashboard_data['qualitatives'] = actions_common.get_raw_qualitative_data(self,manager,managers,start_date,end_date)

        for employee in employees:
            actions_common.create_employee_qualitative_performance(self,dashboard_data,employee)

        dashboard_data['org_datas'],dashboard_data['dept_names'] = actions_common.get_org_datas_dept_names(manager,managers)

        dashboard_data['qualitatives'],dashboard_data['qualitative_overall_averages'] = actions_common.get_ordered_qualitative_data(self,dashboard_data,employees)
        dashboard_data['other_performances'] = actions_common.get_miscellaneous_performances(self,manager,managers,start_date,end_date)

        return dashboard_data