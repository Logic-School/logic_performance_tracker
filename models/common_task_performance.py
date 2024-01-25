from odoo import models,fields,api
import logging
class CommonTaskPerformance(models.Model):
    _name = "logic.common.task.performance"
    employee = fields.Many2one('hr.employee')
    completed_to_do_count = fields.Integer()
    completed_misc_count = fields.Integer()
    delayed_misc_count = fields.Integer()
    delayed_to_do_count = fields.Integer()
    combined_rating = fields.Float()
    misc_average_rating = fields.Float()
    to_do_average_rating = fields.Float()
    qualitative_average_rating = fields.Float()
    score = fields.Float()

    def create_employee_common_task_performance(self,employee, start_date=False, end_date=False):
        logger = logging.getLogger("Common perf debug: ")
        employee_data = {'completed_to_do_count':0, 'completed_misc_count':0, 'delayed_to_do_count':0, 'delayed_misc_count':0, 'combined_rating':0, 'score':0}
        misc_domain = [('task_creator_employee','=',employee.id),('state','=',('completed')),('expected_completion','!=',False)]
        to_do_domain = [('state','=','completed'),'|',('assigned_to','=',employee.user_id.id),('coworkers_ids','in',[employee.user_id.id] ), ('completed_date','!=',False)]
        if start_date and end_date:
            misc_domain.extend([('date_completed','>=',start_date),('date_completed','<=',end_date)])
            to_do_domain.extend([('completed_date','>=',start_date),('completed_date','<=',end_date)])
        misc_tasks = self.env['logic.task.other'].sudo().search(misc_domain)
        to_do_tasks = self.env['to_do.tasks'].sudo().search(to_do_domain)
        misc_average_rating = 0
        to_do_average_rating = 0
        employee_data['completed_to_do_count'] = len(to_do_tasks)
        employee_data['completed_misc_count'] = len(misc_tasks)
        total_tasks = employee_data['completed_to_do_count'] + employee_data['completed_misc_count']
        for task in misc_tasks:
            employee_data['combined_rating']+=int(task.head_rating)
            misc_average_rating+=int(task.head_rating)
            if task.completion_datetime and task.expected_completion and task.expected_completed_difference>0 and not task.delay_approved:
                employee_data['delayed_misc_count']+=1                
                employee_data['score'] += 0.5 * int(task.head_rating)
            else:
                employee_data['score'] += int(task.head_rating)

        for task in to_do_tasks:
            employee_data['combined_rating']+=int(task.rating)
            to_do_average_rating+=int(task.rating)
            if task.dead_line:
                if task.completed_date > task.dead_line:
                    employee_data['delayed_to_do_count']+=1                
                    employee_data['score'] += 0.5 * int(task.rating)    
                else:
                    employee_data['score'] += int(task.rating)
        rated_misc_tasks = len(misc_tasks.filtered(lambda task: task.head_rating!='0'))
        rated_to_do_tasks = len(to_do_tasks.filtered(lambda task: task.rating!='0'))
        rated_tasks_count = rated_misc_tasks + rated_to_do_tasks
        
        if rated_misc_tasks>0:
            misc_average_rating = round(misc_average_rating/rated_misc_tasks,2)
        if rated_to_do_tasks>0:
            to_do_average_rating = round(to_do_average_rating/rated_to_do_tasks,2)
        if rated_tasks_count>0:
            employee_data['combined_rating'] = round(employee_data['combined_rating'] / rated_tasks_count,2)

        qualitative_average_rating = 0    
        if not start_date or not end_date:
            quality_records = self.env['base.qualitative.analysis'].sudo().search([('name','=',employee.id)])
        else:
            quality_records = self.env['base.qualitative.analysis'].sudo().search([('name','=',employee.id),('added_date','>=',start_date),('added_date','<=',end_date)])
        if quality_records:
            for quality_rec in quality_records:
                average_rating = 0
                if quality_rec.attribute_ids:
                    for attribute in quality_rec.attribute_ids:
                        average_rating+=int(attribute.performance)
                    average_rating = average_rating/len(quality_rec.attribute_ids)
                qualitative_average_rating+=average_rating 
            qualitative_average_rating = round(qualitative_average_rating/len(quality_records),2)

        common_task_perf_obj = self.env['logic.common.task.performance'].sudo().search([('employee','=',employee.id)])
        
        values = {
            'employee': employee.id,
            'completed_to_do_count':employee_data['completed_to_do_count'], 
            'completed_misc_count':employee_data['completed_misc_count'], 
            'delayed_to_do_count':employee_data['delayed_to_do_count'], 
            'delayed_misc_count':employee_data['delayed_misc_count'], 
            'combined_rating':employee_data['combined_rating'], 
            'score':employee_data['score'],
            'qualitative_average_rating': qualitative_average_rating,
            'misc_average_rating': misc_average_rating,
            'to_do_average_rating': to_do_average_rating,
        }

        if common_task_perf_obj:
            common_task_perf_obj.write(values)
        else:
            self.env['logic.common.task.performance'].sudo().create(values) 
        logger.error("Common Perf: "+str(employee_data))

        return values           

    def get_employee_common_task_performances(self,employees):
        logger = logging.getLogger("Common perf debug: ")
        logger.error("emps: "+str(employees.mapped('name')))
        common_task_perf_objs = self.env['logic.common.task.performance'].sudo().search([('employee','in',employees.ids)], order="score desc")
        employee_performances = {}

        for common_task_perf_obj in common_task_perf_objs:
            emp_id_name = str(common_task_perf_obj.employee.id) + " "
            employee_performances[emp_id_name] = {}
            employee_performances[emp_id_name]['name'] = common_task_perf_obj.employee.name
            employee_performances[emp_id_name]['completed_to_do_count'] = common_task_perf_obj.completed_to_do_count
            employee_performances[emp_id_name]['completed_misc_count']=common_task_perf_obj.completed_misc_count
            employee_performances[emp_id_name]['delayed_to_do_count']=common_task_perf_obj.delayed_to_do_count
            employee_performances[emp_id_name]['delayed_misc_count']=common_task_perf_obj.delayed_misc_count
            employee_performances[emp_id_name]['combined_rating']=common_task_perf_obj.combined_rating
            employee_performances[emp_id_name]['score']=common_task_perf_obj.score
            employee_performances[emp_id_name]['misc_average_rating'] = common_task_perf_obj.misc_average_rating
            employee_performances[emp_id_name]['to_do_average_rating'] = common_task_perf_obj.to_do_average_rating
            employee_performances[emp_id_name]['qualitative_average_rating'] = common_task_perf_obj.qualitative_average_rating

        logger.error('common perfs: '+str(employee_performances))
        return employee_performances
