from odoo import models,fields,api
from odoo.exceptions import UserError
from . import actions_common
class DigitalTaskInherit(models.Model):
    _inherit = "digital.task"

    @api.model
    def retrieve_dashboard_data(self,start_date=False,end_date=False):

        tasks = self.env['digital.task'].search([])
        try:
            manager = self.env.ref('logic_digital_tracker.group_digital_head').users[0].employee_id

        except:
            manager = False
        dashboard_data = {}
        states = {}
        for task in tasks:
            try:
                states[task.state][1]+=1
            except:
                states[task.state] = [dict(task._fields['state'].selection).get(task.state),1]
        dashboard_data['states'] = states
        
        if not start_date or not end_date:
            dashboard_data['qualitatives'] = self.env['base.qualitative.analysis'].retrieve_performance(manager)
            dashboard_data['performances'] = self.env['digital.executive.performance'].action_executive_performance(dashboard_data['qualitatives'])
            dashboard_data['other_performances'] = self.env['logic.task.other'].retrieve_performance(manager)
        else:
            start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)
            dashboard_data['qualitatives'] = self.env['base.qualitative.analysis'].retrieve_performance(manager,start_date,end_date)
            dashboard_data['performances'] = self.env['digital.executive.performance'].action_executive_performance(dashboard_data['qualitatives'],start_date,end_date)
            dashboard_data['other_performances'] = self.env['logic.task.other'].retrieve_performance(manager,start_date,end_date)

        # raise UserError(dashboard_data)
        return dashboard_data
