from odoo import models,fields,api
from odoo.exceptions import UserError
from datetime import date
from . import actions_common

class DigitalPerformance(models.Model):
    _name = "digital.executive.performance"
    _order = "total_score desc"
    digital_executive = fields.Many2one('res.users')
    name = fields.Char(related='digital_executive.name')
    average_rating = fields.Float(string="Average Rating")
    completed_tasks = fields.Integer(string="Completed Tasks")
    qualitative_average = fields.Float(string="Qualitative Average")
    total_score = fields.Integer(string="Total Score")
    overall_rating = fields.Float(string="Overall Rating")

    def calculate_exec_score(self,task_id,executive):
        contrib = self.env['digital.task.contribution'].sudo().search([('task_id','=',task_id.id),('executive','=',executive.id)])
        score = 0
        if contrib:
            score = (contrib[0].contribution/100)*task_id.task_type.score
        return score

    @api.model
    def action_executive_performance(self,qualitatives,from_date=False,end_date=False,order="completed_tasks desc"):
        # self.env['digital.executive.performance'].sudo().search([]).unlink()
        executives_performance = {}
        if not from_date or not end_date:
            digital_tasks = self.env['digital.task'].sudo().search([('state','in',('completed','to_post','posted'))])
        else:
            digital_tasks = self.env['digital.task'].sudo().search([('state','in',('completed','to_post','posted')), ('date_completed', '>=',from_date), ('date_completed','<=',end_date)])

        for task in digital_tasks:
            for executive in task.assigned_execs:
                if executives_performance.get(executive.id):
                    if task.head_rating!='0':
                        executives_performance[executive.id]['rating']+=int(task.head_rating)
                        executives_performance[executive.id]['rated_tasks']+=1
                    executives_performance[executive.id]['completed_tasks']+=1
                    executives_performance[executive.id]['total_score'] += self.calculate_exec_score(task,executive)

                else:
                    executives_performance[executive.id] = {}
                    executives_performance[executive.id]['rating'] = 0
                    executives_performance[executive.id]['rated_tasks'] = 0
                    executives_performance[executive.id]['total_score'] = self.calculate_exec_score(task,executive)
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
            qualitative_average = 0
            employee_name = self.env['res.users'].browse(exec_id).employee_id.name

            if qualitatives.get(employee_name):
                for attribute in qualitatives[employee_name].keys():
                    qualitative_average += qualitatives[employee_name][attribute]['average_rating']
                qualitative_average = round(qualitative_average/len(qualitatives[employee_name].keys()), 2)

            if executives_performance[exec_id].get('rating'):
                tasks_average_rating = round(executives_performance[exec_id]['rating']/executives_performance[exec_id]['rated_tasks'],2)
            else:
                tasks_average_rating = 0

            values = {
                'digital_executive': exec_id,
                'average_rating':tasks_average_rating,
                'completed_tasks': executives_performance[exec_id]['completed_tasks'],
                'qualitative_average': qualitative_average,
                'total_score': executives_performance[exec_id]['total_score'],
                'overall_rating': round((tasks_average_rating+qualitative_average)/2,2) if qualitative_average>0 else tasks_average_rating
            }
            current_exec_performance_obj = self.env['digital.executive.performance'].sudo().search([('digital_executive','=',exec_id)])
            if current_exec_performance_obj:
                current_exec_performance_obj.write(values)
            else:
                self.env['digital.executive.performance'].sudo().create(values)
        
        performances = self.env['digital.executive.performance'].sudo().search([],order=order)
        
        executives_performances = []
        for exec_performance in performances:
            current_performance = {}
            current_performance['name'] = exec_performance.digital_executive.name
            current_performance['average_rating'] = exec_performance.average_rating
            current_performance['qualitative_average'] = exec_performance.qualitative_average
            current_performance['completed_tasks'] = exec_performance.completed_tasks
            current_performance['overall_rating'] = exec_performance.overall_rating
            current_performance['total_score'] = exec_performance.total_score

            executives_performances.append(current_performance)

        return executives_performances



        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': 'Executives Performance',
        #     'view_mode': 'tree',
        #     'res_model': 'digital.executive.performance',
        #     'target': 'current',
        # }
