from odoo import models, fields, api
from . import actions_common
from . import common_task_performance


class ResidentialTracker(models.Model):
    _name = "operations.tracker"

    @api.model
    def retrieve_dashboard_data(self, start_date=False, end_date=False, manager_id=False):

        if start_date and end_date:
            start_date, end_date = actions_common.get_date_obj_from_string(start_date, end_date)

        dashboard_data = {}
        employees_data = {}
        department_obj = self.env['hr.department'].sudo().search([('name', '=', 'Operations')])

        if not manager_id:
            manager_id = department_obj.child_ids[0].manager_id.id

        manager, managers, department_heads_data = actions_common.get_manager_managers_heads_data(self, department_obj,
                                                                                                  manager_id)

        employees = actions_common.get_employees(self, department_obj, manager, managers)

        dashboard_data['department_heads'] = department_heads_data

        dashboard_data['qualitatives'] = actions_common.get_raw_qualitative_data(self, employees, start_date, end_date)

        for employee in employees:
            actions_common.create_employee_qualitative_performance(self, dashboard_data['qualitatives'], employee)
            self.env['logic.common.task.performance'].sudo().create_employee_common_task_performance(employee,
                                                                                                     start_date,
                                                                                                     end_date)
        dashboard_data['common_task_performances'] = self.env[
            'logic.common.task.performance'].sudo().get_employee_common_task_performances(employees)
        dashboard_data['qualitatives'], dashboard_data[
            'qualitative_overall_averages'] = actions_common.get_ordered_qualitative_data(self, dashboard_data[
            'qualitatives'], employees)
        dashboard_data['other_performances'] = actions_common.get_miscellaneous_performances(self, employees,
                                                                                             start_date, end_date)

        dashboard_data['org_datas'], dashboard_data['dept_names'] = actions_common.get_org_datas_dept_names(manager,
                                                                                                            managers)
        return dashboard_data
