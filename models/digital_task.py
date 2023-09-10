from odoo import models,fields,api

class DigitalTaskInherit(models.Model):
    _inherit = "digital.task"

    @api.model
    def retrieve_dashboard_data(self):
        tasks = self.env['digital.task'].search([])
        dashboard_data = {}
        states = {}
        for task in tasks:
            try:
                states[task.state][1]+=1
            except:
                states[task.state] = [dict(task._fields['state'].selection).get(task.state),1]
        dashboard_data['states'] = states
        dashboard_data['performances'] = self.env['digital.executive.performance'].action_executive_performance()
        return dashboard_data
