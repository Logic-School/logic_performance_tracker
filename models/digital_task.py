from odoo import models,fields,api
from odoo.exceptions import UserError
from . import actions_common
import logging
class DigitalTaskInherit(models.Model):
    _inherit = "digital.task"

    def get_states_data(self,tasks):
        states = {'Sent to Approve':0,'Approved':0,'Assigned':0,'In Progress':0,'Completed':0,'To Post':0,'Posted':0}
        for task in tasks:
            try:
                states[dict(task._fields['state'].selection).get(task.state)]+=1
            except:
                pass
        states_data = []
        for key in states.keys():
            states_data.append({'label':key,'value':states[key]})
        return states_data
            # except:
            #     states[task.state] = [dict(task._fields['state'].selection).get(task.state),1]

    @api.model
    def retrieve_dashboard_data(self,start_date=False,end_date=False,manager_id=False):
        logger = logging.getLogger("Debugger: ")

        logger.error("Manager Id: " + str(manager_id))
        if start_date and end_date:
            start_date, end_date = actions_common.get_date_obj_from_string(start_date, end_date)

        dashboard_data = {}

        employees_data = {}
        department_obj = self.env['hr.department'].sudo().search([('name', '=', 'Digital')])

        if not manager_id:
            manager_id = department_obj.child_ids[0].manager_id.id
        manager, managers, department_heads_data = actions_common.get_manager_managers_heads_data(self, department_obj,
                                                                                                  manager_id)
        employees = actions_common.get_employees(self, department_obj, manager, managers)
        # if start_date and end_date:
        #     start_date, end_date = actions_common.get_date_obj_from_string(start_date, end_date)
        #
        # dashboard_data = {}
        # employees_data = {}
        # department_obj = self.env['hr.department'].sudo().search([('name', '=', 'Digital')])
        #
        # if start_date and end_date:
        #     start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)
        #
        # logger = logging.getLogger("Debugger")
        tasks = self.env['digital.task'].sudo().search([])
        # try:
        #     if not manager_id:
        #         manager_id = department_obj.child_ids[0].manager_id.id
        #
        #     manager, managers, department_heads_data = actions_common.get_manager_managers_heads_data(self,
        #                                                                                               department_obj,
        #                                                                                               manager_id)
        #     # manager = department_obj.child_ids[0].manager_id.id
        #     employees = manager.child_ids
        # except:
        #     manager = False
        # dashboard_data = {}
        #
        dashboard_data = {
            'department_heads': department_heads_data,
        }
        dashboard_data['states_data'] = self.get_states_data(tasks)

        dashboard_data['qualitatives'] = actions_common.get_raw_qualitative_data(self,employees,start_date,end_date)


        if not start_date or not end_date:
            dashboard_data['performances'] = self.env['digital.executive.performance'].action_executive_performance(dashboard_data['qualitatives'])
        else:
            dashboard_data['performances'] = self.env['digital.executive.performance'].action_executive_performance(dashboard_data['qualitatives'],start_date,end_date)


        dashboard_data['other_performances'] = actions_common.get_miscellaneous_performances(self,employees,start_date,end_date)

        for employee in employees:
            self.env['logic.common.task.performance'].sudo().create_employee_common_task_performance(employee,start_date,end_date)

            actions_common.create_employee_qualitative_performance(self,dashboard_data['qualitatives'],employee)

        dashboard_data['qualitatives'],dashboard_data['qualitative_overall_averages'] = actions_common.get_ordered_qualitative_data(self,dashboard_data['qualitatives'],employees)
        dashboard_data['common_task_performances'] = self.env['logic.common.task.performance'].sudo().get_employee_common_task_performances(employees)

        org_datas=[]
        if manager:
            org_datas = [manager.get_organisation_data(manager)]
        dashboard_data['org_datas'] = org_datas
        # raise UserError(dashboard_data)
        return dashboard_data
