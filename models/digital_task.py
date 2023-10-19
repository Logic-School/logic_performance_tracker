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
    def retrieve_dashboard_data(self,start_date=False,end_date=False):

        if start_date and end_date:
            start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)

        logger = logging.getLogger("Debugger")
        tasks = self.env['digital.task'].sudo().search([])
        try:
            manager = self.env.ref('logic_digital_tracker.group_digital_head').users[0].employee_id
            employees = manager.child_ids
        except:
            manager = False
        dashboard_data = {}

        dashboard_data['states_data'] = self.get_states_data(tasks)
        
        dashboard_data['qualitatives'] = actions_common.get_raw_qualitative_data(self,manager,False,start_date,end_date)


        if not start_date or not end_date:
            # dashboard_data['qualitatives'] = self.env['base.qualitative.analysis'].retrieve_performance(manager=manager)
            dashboard_data['performances'] = self.env['digital.executive.performance'].action_executive_performance(dashboard_data['qualitatives'])
            # dashboard_data['other_performances'] = self.env['logic.task.other'].retrieve_performance(manager)
        else:
            # dashboard_data['qualitatives'] = self.env['base.qualitative.analysis'].retrieve_performance(manager=manager,start_date=start_date,end_date=end_date)
            dashboard_data['performances'] = self.env['digital.executive.performance'].action_executive_performance(dashboard_data['qualitatives'],start_date,end_date)
            # dashboard_data['other_performances'] = self.env['logic.task.other'].retrieve_performance(manager,False,start_date,end_date)
        

        dashboard_data['other_performances'] = actions_common.get_miscellaneous_performances(self,manager,False,start_date,end_date)

        for employee in employees:  

            actions_common.create_employee_qualitative_performance(self,dashboard_data,employee)

        dashboard_data['qualitatives'],dashboard_data['qualitative_overall_averages'] = actions_common.get_ordered_qualitative_data(self,dashboard_data,employees)
        
        org_datas=[]
        if manager:
            org_datas = [manager.get_organisation_data(manager)]
        dashboard_data['org_datas'] = org_datas
        # raise UserError(dashboard_data)
        return dashboard_data
