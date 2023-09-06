from odoo import models,fields,api
from odoo.exceptions import UserError

class DigitalPerformance(models.Model):
    _name = "digital.executive.performance"
    _order = "completed_tasks desc"
    digital_executive = fields.Many2one('res.users')
    average_rating = fields.Float(string="Average Rating")
    completed_tasks = fields.Integer(string="Completed Tasks")

    def action_executive_performance(self):
        self.env['digital.executive.performance'].search([]).unlink()
        executives_performance = {}
        digital_tasks = self.env['digital.task'].search([('state','in',('completed','to_post','posted'))])
        for task in digital_tasks:
            for executive in task.assigned_execs:
                if executives_performance.get(executive.id):
                    if task.head_rating!='0':
                        executives_performance[executive.id]['rating']+=int(task.head_rating)
                        executives_performance[executive.id]['rated_tasks']+=1
                    executives_performance[executive.id]['completed_tasks']+=1
                else:
                    executives_performance[executive.id] = {}
                    if task.head_rating!='0':
                        executives_performance[executive.id]['rating'] = int(task.head_rating)
                        executives_performance[executive.id]['rated_tasks']=1
                    executives_performance[executive.id]['completed_tasks']=1
        for exec_id in executives_performance.keys():
            self.env['digital.executive.performance'].create({
                'digital_executive': exec_id,
                'average_rating': executives_performance[exec_id]['rating']/executives_performance[exec_id]['rated_tasks'],
                'completed_tasks': executives_performance[exec_id]['completed_tasks'],
            })
        return {
            'type': 'ir.actions.act_window',
            'name': 'Executives Performance',
            'view_mode': 'tree',
            'res_model': 'digital.executive.performance',
            'target': 'current',
        }
