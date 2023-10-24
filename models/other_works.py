from odoo import models, fields, api
from odoo.exceptions import UserError
import logging


class OtherTaskInherit(models.Model):
    _inherit = "logic.task.other"

    @api.model
    def retrieve_performance(self, employees, start_date=False,end_date=False):
        logger = logging.getLogger("Debugger: ")
        employee_performances = {}
        employees = employees.ids

        for employee_id in employees:
            employee_performances[employee_id] = {}
            employee_performances[employee_id]['name'] = self.env['hr.employee'].browse(employee_id).name

            employee_performances[employee_id]['rating'] = 0
            employee_performances[employee_id]['rated_tasks']=0
            employee_performances[employee_id]['completed_tasks']=0
            employee_performances[employee_id]['average_rating'] = 0


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

            other_task_perf_obj = self.env['other.task.performance'].sudo().search([('employee','=',employee_id)])
            if other_task_perf_obj:
                other_task_perf_obj.write({
                    'total_completed': employee_performances[employee_id]['completed_tasks'],
                    'average_rating': employee_performances[employee_id]['average_rating'],
                })
            else:
                self.env['other.task.performance'].sudo().create({
                    'employee': employee_id,
                    'total_completed': employee_performances[employee_id]['completed_tasks'],
                    'average_rating': employee_performances[employee_id]['average_rating'],
                })
        other_task_perf_objs = self.env['other.task.performance'].sudo().search([('employee','in',employees)], order="average_rating desc")
        employee_performances = {}
        logger.error('other_task_perf_objs '+str(other_task_perf_objs))

        for other_task_perf_obj in other_task_perf_objs:
            emp_id_name = str(other_task_perf_obj.employee.id) + " "
            employee_performances[emp_id_name] = {}
            employee_performances[emp_id_name]['name'] = other_task_perf_obj.employee.name
            employee_performances[emp_id_name]['average_rating'] = other_task_perf_obj.average_rating
            employee_performances[emp_id_name]['total_completed']=other_task_perf_obj.total_completed
        logger.error('employee_performances '+str(employee_performances))

        return employee_performances
    
class OtherTaskPerformance(models.Model):
    _name="other.task.performance"
    _order="average_rating asc"

    employee = fields.Many2one("hr.employee",string="Employee")
    total_completed = fields.Integer(default=0)
    average_rating = fields.Float(default=0)
