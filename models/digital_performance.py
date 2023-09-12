from odoo import models,fields,api
from odoo.exceptions import UserError
from datetime import date
from . import actions_common

class DigitalPerformance(models.Model):
    _name = "digital.executive.performance"
    _order = "completed_tasks desc"
    digital_executive = fields.Many2one('res.users')
    name = fields.Char(related='digital_executive.name')
    average_rating = fields.Float(string="Average Rating")
    completed_tasks = fields.Integer(string="Completed Tasks")

    @api.model
    def action_executive_performance(self,from_date=False,end_date=False,order="completed_tasks desc"):
        self.env['digital.executive.performance'].search([]).unlink()
        executives_performance = {}
        if not from_date or not end_date:
            digital_tasks = self.env['digital.task'].search([('state','in',('completed','to_post','posted'))])
        else:
            digital_tasks = self.env['digital.task'].search([('state','in',('completed','to_post','posted')), ('date_completed', '>=',from_date), ('date_completed','<=',end_date)])

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
        # for exec_id in executives_performance.keys():
        #     name  = self.env['res.users'].browse(exec_id).name
        #     if executives_performance.get(name):
        #         name = name+"_1"
        #     executives_performance[name] = executives_performance.pop(exec_id)
        #     executives_performance[name]['average_rating'] = executives_performance[name]['rating']/executives_performance[name]['rated_tasks']

        for exec_id in executives_performance.keys():
            if executives_performance[exec_id].get('rating'):
                tasks_average_rating = round(executives_performance[exec_id]['rating']/executives_performance[exec_id]['rated_tasks'],1)
            else:
                tasks_average_rating = 0
            self.env['digital.executive.performance'].create({
                'digital_executive': exec_id,
                'average_rating':tasks_average_rating,
                'completed_tasks': executives_performance[exec_id]['completed_tasks'],
            })
        
        performances = self.env['digital.executive.performance'].search([],order=order)
        
        executives_performances = []
        for exec_performance in performances:
            current_performance = {}
            current_performance['name'] = exec_performance.digital_executive.name
            current_performance['average_rating'] = exec_performance.average_rating
            current_performance['completed_tasks'] = exec_performance.completed_tasks
            executives_performances.append(current_performance)

        return executives_performances



        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Executives Performance',
        #     'view_mode': 'tree',
        #     'res_model': 'digital.executive.performance',
        #     'target': 'current',
        # }
