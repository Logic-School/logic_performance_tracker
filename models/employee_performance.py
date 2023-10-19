from odoo import models,api,fields
import logging
class LogicEmployeePerformance(models.Model):
    _name = "logic.employee.performance"
    @api.model
    def model_records_open_action(self,employee_id,model_name,start_date=False,end_date=False):
        domain=[]
        logger = logging.getLogger("Debugger: ")

        employee = self.env['hr.employee'].browse(int(employee_id))
        if model_name=="upaya.form":
            domain = [['coordinator_id','=',employee.user_id.id]]
        elif model_name=="yes_plus.logic":
            domain = [['coordinator_id','=',employee.user_id.id]]
        elif model_name=="student.faculty":
            domain = [['coordinator','=',employee.user_id.id]]
        elif model_name=="exam.details":
            domain = [['coordinator','=',employee.user_id.id]]
        elif model_name=="one_to_one.meeting":
            domain = [['coordinator_id','=',employee.user_id.id]]
        elif model_name=="logic.mock_interview":
            domain = [['coordinator','=',employee.user_id.id]]
        elif model_name=="logic.cip.form":
            domain = [['coordinator_id','=',employee.user_id.id]]
        elif model_name=="bring.your.buddy":
            domain = [['coordinator_id','=',employee.user_id.id]]
        logger.error("domain: "+str(domain))
        return domain
    
    def get_monthly_misc_counts(self,employee,year):
        misc_tasks = self.env['logic.task.other'].search([('task_creator_employee','=',employee.id),('state','=','completed')])
        misc_tasks = misc_tasks.filtered(lambda task: (task.date_completed or task.date).year==year)
        misc_data = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0}
        for task in misc_tasks:
            if task.date_completed or task.date:
                date = task.date_completed or task.date
                misc_data[date.month]+=1
        return list(misc_data.values())

    def get_monthly_to_do_counts(self,employee,year):
        to_do_tasks = self.env['to_do.tasks'].sudo().search([('state','=','completed'),'|',('assigned_to','=',employee.user_id.id),('coworkers_ids','in',[employee.user_id.id] )])
        to_do_tasks = to_do_tasks.filtered(lambda task: task.assigned_date.year==year)
        to_do_data = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0}
        for task in to_do_tasks:
            if task.assigned_date:
                date = task.assigned_date
                to_do_data[date.month]+=1
        return list(to_do_data.values())
    
    @api.model
    def get_line_chart_datasets(self,employee_id,year="2023"):
        employee = self.env['hr.employee'].browse(int(employee_id))
        logger = logging.getLogger("Debugger: ")
        year = int(year)
        datasets = []
        logger.error(self.get_monthly_misc_counts(employee,year))
        misc_data = {
            'label': 'Miscellaneous Tasks',
            'backgroundColor': 'rgba(255,255,255, 0.2)',
            'borderColor': 'rgba(255, 0, 0, 0.6)',
            'borderWidth': 1,
            'data': self.get_monthly_misc_counts(employee,year)
        }
        to_do_data = {
            'label': 'To Do Tasks',
            'backgroundColor': 'rgba(255,255,255, 0.2)',
            'borderColor': 'rgba(25, 131, 19, 0.8)',
            'borderWidth': 1,
            'data': self.get_monthly_to_do_counts(employee,year)
        }
        datasets.append(misc_data)
        datasets.append(to_do_data)
        return datasets

    def get_employee_personal_data(self,employee):
        personal_data = {}
        personal_data['name'] = employee.name
        personal_data['job_title'] = employee.job_title
        personal_data['department_name'] = employee.department_id.name
        personal_data['image'] = 'data:image/png;base64, ' + str(employee.image_1920, 'UTF-8')
        return personal_data
    
    def get_student_feedback_average(self,employee):
        student_feedbacks = self.env['student.feedback'].sudo().search([('coordinator_id','=',employee.user_id.id)])
        if student_feedbacks:
            total_rating = 0
            for feedback in student_feedbacks:
                total_rating+= int(feedback.star_rating)
            average_rating = round(total_rating/len(student_feedbacks),2)
            return average_rating
        else:
            return 0
        
    def get_employee_academic_data(self,employee):
        academic_coord_perfs = self.env['academic.coordinator.performance'].sudo().search([('employee','=',employee.id)])
        if academic_coord_perfs:
            for coord_perf in academic_coord_perfs:
                academic_data = {}
                academic_data['name'] = coord_perf.employee.name
                academic_data['upaya_count'] = coord_perf.upaya_count
                academic_data['yes_plus_count'] = coord_perf.yes_plus_count
                academic_data['one2one_count'] = coord_perf.one2one_count
                academic_data['sfc_count'] = coord_perf.sfc_count
                academic_data['exam_count'] = coord_perf.exam_count
                academic_data['mock_interview_count'] = coord_perf.mock_interview_count
                academic_data['cip_excel_count'] = coord_perf.cip_excel_count
                academic_data['bring_buddy_count'] = coord_perf.bring_buddy_count
                academic_data['total_completed'] = coord_perf.total_completed
            
            academic_data['student_feedback_rating'] = self.get_student_feedback_average(employee)
            return academic_data
        else:
            return False
        
    def get_common_performance_data(self,employee):
        common_performance = {}
        common_performance['qualitative_rating'] = 0
        qualitative_perf = self.env['employee.qualitative.performance'].search([('employee','=',employee.id)])
        if qualitative_perf:
            common_performance['qualitative_rating'] = qualitative_perf[0].overall_average
        common_performance['misc_task_count'] = self.env['logic.task.other'].search_count([('task_creator','=',employee.user_id.id)])
        common_performance['to_do_count'] = self.env['to_do.tasks'].sudo().search_count([('state','=','completed'),'|',('assigned_to','=',employee.user_id.id),('coworkers_ids','in',[employee.user_id.id] )])        
        return common_performance

    @api.model
    def retrieve_employee_performance(self,employee_id):
        logger = logging.getLogger("Debugger: ")
        employee = self.env['hr.employee'].browse(int(employee_id))
        employee_data = {}
        employee_data['personal_data'] = self.get_employee_personal_data(employee)
        employee_data['academic_data'] = self.get_employee_academic_data(employee)
        employee_data['common_performance'] = self.get_common_performance_data(employee)
        employee_data['line_chart_datasets'] = self.get_line_chart_datasets(employee)
        return employee_data
