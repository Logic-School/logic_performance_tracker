from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

class OtherTaskInherit(models.Model):
    _inherit = "logic.task.other"

    @api.model
    def retrieve_performance(self, manager=False, managers=False, start_date=False,end_date=False):
        logger = logging.getLogger("Debugger: ")
        employee_performances = {}
        employees = []
        if manager:
            employees += manager.child_ids.ids
        elif managers:
            for manager in managers:
                employees+=manager.child_ids.ids

        logger.error("Other works Emps: "+str(employees))
        for employee_id in employees:
            employee_performances[employee_id] = {}
            employee_performances[employee_id]['name'] = self.env['hr.employee'].browse(employee_id).name

            employee_performances[employee_id]['rating'] = 0
            employee_performances[employee_id]['rated_tasks']=0
            employee_performances[employee_id]['completed_tasks']=0

            if not start_date or not end_date:
                task_records = self.env['logic.task.other'].sudo().search([('task_creator_employee','=',employee_id)])
            else:
                task_records = self.env['logic.task.other'].sudo().search([('task_creator_employee','=',employee_id),('date','>=',start_date),('date','<=',end_date)])
            logger.error("Other works Emp recs: "+str(task_records))

            for task in task_records:

                if task.head_rating!='0':
                    employee_performances[employee_id]['rating']+=int(task.head_rating)
                    employee_performances[employee_id]['rated_tasks']+=1
                    
                employee_performances[employee_id]['completed_tasks']+=1
            if employee_performances[employee_id]['rated_tasks']>0:
                employee_performances[employee_id]['average_rating'] = round(employee_performances[employee_id]['rating'] / employee_performances[employee_id]['rated_tasks'],2)
            else:
                employee_performances[employee_id]['average_rating'] = 0

        return employee_performances