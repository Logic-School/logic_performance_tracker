from odoo import models, fields, api
from odoo.exceptions import UserError

class OtherTaskInherit(models.Model):
    _inherit = "logic.task.other"

    @api.model
    def retrieve_performance(self, manager, start_date=False,end_date=False):
        employee_performances = {}
        if not start_date or not end_date:
            if manager:
                records = self.env['logic.task.other'].sudo().search([('task_creator_employee','in',manager.child_ids.ids)])
            else:
                records = self.env['logic.task.other'].sudo().search([])
        else:
            if manager:
                records = self.env['logic.task.other'].sudo().search([('task_creator_employee','in',manager.child_ids.ids),('date','>=',start_date),('date','<=',end_date)])
            else:
                records = self.env['logic.task.other'].sudo().search([('date','>=',start_date),('date','<=',end_date)])  
        employees = []
        for record in records:
            if record.task_creator_employee.id not in employees:
                employees.append(record.task_creator_employee.id)
        for employee_id in employees:
            if not start_date or not end_date:
                task_records = self.env['logic.task.other'].sudo().search([('task_creator_employee','=',employee_id)])
            else:
                task_records = self.env['logic.task.other'].sudo().search([('task_creator_employee','=',employee_id),('date','>=',start_date),('date','<=',end_date)])
            for task in task_records:
                emp_name = self.env['hr.employee'].browse(employee_id).name

                if employee_performances.get(employee_id):
                    if task.head_rating!='0':
                        employee_performances[employee_id]['rating']+=int(task.head_rating)
                        employee_performances[employee_id]['rated_tasks']+=1
                        
                    employee_performances[employee_id]['name'] = emp_name
                    employee_performances[employee_id]['completed_tasks']+=1
                else:
                    employee_performances[employee_id] = {}
                    if task.head_rating!='0':
                        employee_performances[employee_id]['rating'] = int(task.head_rating)
                        employee_performances[employee_id]['rated_tasks']=1

                    employee_performances[employee_id]['name'] = emp_name    
                    employee_performances[employee_id]['completed_tasks']=1
                if employee_performances[employee_id].get('rating') and employee_performances[employee_id].get('rated_tasks'):
                    employee_performances[employee_id]['average_rating'] = round(employee_performances[employee_id]['rating'] / employee_performances[employee_id]['rated_tasks'],2)
                else:
                    employee_performances[employee_id]['average_rating'] = 0

        return employee_performances