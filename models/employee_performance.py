from odoo import models,api,fields
from odoo.exceptions import UserError
import logging
import random
from datetime import date
from . import actions_common
from . import academic_data
class LogicEmployeePerformance(models.Model):
    _name = "logic.employee.performance"
    @api.model
    def model_records_open_action(self,employee_id,model_name,start_date=False,end_date=False):
        domain=[]
        logger = logging.getLogger("Debugger: ")
        if start_date and end_date:
            start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)
        logger.error("start date, end date: "+str(start_date)+ " "+str(end_date))

        employee = self.env['hr.employee'].browse(int(employee_id))
        if model_name=="upaya.form":
            domain = [['coordinator_id','=',employee.user_id.id],['state','=','complete']]
            if start_date and end_date:
                domain.extend([('date','>=',start_date),('date','<=',end_date)])

        elif model_name=="yes_plus.logic":
            domain = [['coordinator_id','=',employee.user_id.id],['state','=','complete']]
            if start_date and end_date:
                domain.extend([('date_one','>=',start_date),('date_one','<=',end_date)])

        elif model_name=="student.faculty":
            domain = [['coordinator','=',employee.user_id.id]]
            if start_date and end_date:
                domain.extend([('date','>=',start_date),('date','<=',end_date)])

        elif model_name=="exam.details":
            domain = [['coordinator','=',employee.user_id.id]]
            if start_date and end_date:
                domain.extend([('date','>=',start_date),('date','<=',end_date)])

        elif model_name=="one_to_one.meeting":
            domain = [['coordinator_id','=',employee.user_id.id]]
            if start_date and end_date:
                domain.extend([('added_date','>=',start_date),('added_date','<=',end_date)])

        elif model_name=="logic.mock_interview":
            domain = [['coordinator','=',employee.user_id.id]]
            if start_date and end_date:
                domain.extend([('date','>=',start_date),('date','<=',end_date)])

        elif model_name=="logic.cip.form":
            domain = [['coordinator_id','=',employee.user_id.id]]
            if start_date and end_date:
                domain.extend([('date','>=',start_date),('date','<=',end_date)])

        elif model_name=="bring.your.buddy":
            domain = [['coordinator_id','=',employee.user_id.id]]
            if start_date and end_date:
                domain.extend([('date','>=',start_date),('date','<=',end_date)])

        elif model_name=='logic.task.other':
            domain = [['task_creator','=',employee.user_id.id]]
            if start_date and end_date:
                domain.extend([('date_completed','>=',start_date),('date_completed','<=',end_date)])
        
        elif model_name=='to_do.tasks':
            domain = [('state','=','completed'),'|',('assigned_to','=',employee.user_id.id),('coworkers_ids','in',[employee.user_id.id] ), ('state','=','completed')]
            if start_date and end_date:
                domain.extend([('completed_date','>=',start_date),('completed_date','<=',end_date)])

        elif model_name=='digital.task':
            domain = [('state','in',('completed','to_post','posted')), ('assigned_execs','in',[employee.user_id.id] ),('assigned_execs','!=',False)]
            if start_date and end_date:
                domain.extend([('date_completed', '>=',start_date), ('date_completed','<=',end_date)])

        elif model_name=='seminar.leads':
            # if (seminar.attended_by.id==employee.id) or ( (not seminar.attended_by) and (seminar.create_uid.id==employee.user_id.id) ):

            domain = ['|',('attended_by','=',employee.id ),'&',('attended_by','=',False),('create_uid','=',employee.user_id.id)]
            if start_date and end_date:
                domain.extend([('seminar_date', '>=',start_date), ('seminar_date','<=',end_date)])

        elif model_name=='leads.logic':
            lead_domain = [('leads_assign','=',employee.id)]
        
            # month,year = self.env['sales.tracker'].sudo().get_leads_month_year(start_date,end_date)
            
            leads = self.env['leads.logic'].sudo().search(lead_domain)
            leads_with_admission,leads_without_admission = self.env['sales.tracker'].sudo().get_leads_with_and_without_admission(leads,start_date,end_date)
            leads = leads_with_admission + leads_without_admission
            domain = [('id','in',leads.ids)]
            # if start_date and end_date:
            #     domain.extend([('date_of_adding', '>=',start_date), ('date_of_adding','<=',end_date)])

        elif model_name=='logic.presentations':
            domain = [('coordinator','=',employee.user_id.id )]
            if start_date and end_date:
                domain.extend([('date', '>=',start_date), ('date','<=',end_date)])

        elif model_name=='attendance.session':
            domain = [('coordinator','=',employee.user_id.id )]
            if start_date and end_date:
                domain.extend([('date', '>=',start_date), ('date','<=',end_date)])
        logger.error("domain: "+str(domain))
        logger.error("model: "+str(model_name))

        return domain
    
    def get_monthly_misc_counts(self,employee,year):
        misc_tasks = self.env['logic.task.other'].sudo().search([('task_creator_employee','=',employee.id),('state','=','completed')])
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
    
    def get_monthly_digital_counts(self,employee,year):
        digital_tasks = self.env['digital.task'].sudo().search([('state','=','completed'),('assigned_execs','in',[employee.user_id.id] )])
        digital_tasks = digital_tasks.filtered(lambda task: task.date_completed.year==year)
        digital_data = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0, 10:0, 11:0, 12:0}
        for task in digital_tasks:
            if task.date_completed:
                date = task.date_completed
                digital_data[date.month]+=1
        return list(digital_data.values())

    # @api.model
    def get_line_chart_datasets(self,employee_id,start_date,end_date):
        if start_date and end_date:
            year = start_date.year
        else:
            year = date.today().year
        employee = self.env['hr.employee'].sudo().browse(int(employee_id))
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

        if employee.department_id.name=="Digital":
            digital_data = {
                'label': 'Digital Tasks',
                'backgroundColor': 'rgba(255,255,255, 0.2)',
                'borderColor': 'rgba(112, 63, 205, 0.8)',
                'borderWidth': 1,
                'data': self.get_monthly_digital_counts(employee,year)
            }
            datasets.append(digital_data)
        return datasets

    def get_employee_personal_data(self,employee):
        personal_data = {}
        personal_data['id'] = employee.id
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
        
    @api.model
    def get_employee_academic_batches(self,employee_id,window=False):
        employee = self.env['hr.employee'].sudo().browse(int(employee_id))
        if not window:
            window = 'january'
        batch_objs = self.env['logic.base.batch'].sudo().search([('academic_coordinator','=',employee.user_id.id),('batch_window','=',window)])
        batches = []
        for batch_obj in batch_objs:
            batch = {'id':batch_obj.id,'name':batch_obj.name}
            batch['strength'] = self.env['logic.students'].sudo().search_count([('batch_id','=',batch_obj.id),('current_status','=',True)])
            batches.append(batch)
        return batches
    
    @api.model
    def get_academic_batch_data(self,batch_id):
        batch_obj = self.env['logic.base.batch'].sudo().browse(int(batch_id))
        batch_strength = self.env['logic.students'].sudo().search_count([('batch_id','=',batch_obj.id)])
        batch_data = {'batch_strength': batch_strength}

        batch_data['upaya_data'] = academic_data.get_upaya_data(self,batch_obj)
        batch_data['yes_plus_data'] = academic_data.get_yes_plus_data(self,batch_obj)
        batch_data['presentation_data'] = academic_data.get_presentation_data(self,batch_obj)
        batch_data['excel_data'] = academic_data.get_excel_data(self,batch_obj)
        batch_data['cip_data'] = academic_data.get_cip_data(self,batch_obj)
        batch_data['bb_data'] = academic_data.get_bb_data(self,batch_obj)
        batch_data['mock_interview_data'] = academic_data.get_mock_interview_data(self,batch_obj)
        batch_data['attendance_data'] = academic_data.get_attendance_data(self,batch_obj)
        batch_data['exam_data'] = academic_data.get_exam_data(self,batch_obj)
        batch_data['one_to_one_data'] = academic_data.get_one_to_one_data(self,batch_obj)
        return batch_data
    
    def get_employee_academic_data(self,employee,start_date=False,end_date=False):
        department_obj = employee.department_id
        employee_data = {}
        if department_obj.parent_id:
            if department_obj.parent_id.name=='ACADEMICS':
                
                employee_academic_domains = actions_common.get_academic_domains(self,department_obj=department_obj,start_date=start_date,end_date=end_date,manager=False,managers=False,employee_user_ids=[employee.user_id.id])
                employee_academic_counts = actions_common.get_academic_counts(self,employee_academic_domains)
                total_completed = sum(list(employee_academic_counts.values()))
                values = {
                    'employee': employee.id,
                    'upaya_count': employee_academic_counts['upaya_count'],
                    'yes_plus_count': employee_academic_counts['yes_plus_count'],
                    'one2one_count': employee_academic_counts['one_to_one_count'],
                    'sfc_count': employee_academic_counts['sfc_count'],
                    'exam_count': employee_academic_counts['exam_count'],
                    'mock_interview_count': employee_academic_counts['mock_interview_count'],
                    'cip_excel_count': employee_academic_counts['cip_excel_count'],
                    'bring_buddy_count': employee_academic_counts['bring_buddy_count'],
                    'presentation_count': employee_academic_counts['presentation_count'],
                    'attendance_count': employee_academic_counts['attendance_count'],
                    'total_completed': total_completed
                }

                acad_coord_perf_obj = self.env['academic.coordinator.performance'].sudo().search([('employee','=',employee.id)])
                if acad_coord_perf_obj:
                    acad_coord_perf_obj.write(values)
                else:
                    self.env['academic.coordinator.performance'].create(values)
                employee_data.update(values)
                employee_data['name'] = employee.name
                employee_data['student_feedback_rating'] = self.get_student_feedback_average(employee)
                employee_data['batches'] = self.get_employee_academic_batches(employee.id)
                employee_data['academic_windows'] = actions_common.get_academic_windows(self,employee)
                employee_data['is_associate_faculty'] = employee.is_associate_faculty
                return employee_data
        return False
        
    def get_employee_sales_data(self,employee,start_date=False,end_date=False):
        sales_dept_obj = self.env['hr.department'].sudo().search([('name','=','Sales')])
        if employee.department_id.id in sales_dept_obj.child_ids.ids:
            lead_sources = self.env['leads.sources'].sudo().search([])
            lead_courses = self.env['logic.base.courses'].sudo().search([('name','not in',('Nill',"DON'T USE",'Nil'))])
            lead_source_names = lead_sources.mapped('name')
            lead_course_names = lead_courses.mapped('name')
            employee_leads_data = {'lead_sources':lead_source_names, 'sourcewise_leads_dataset': [], 'lead_courses': lead_course_names,'coursewise_leads_dataset': [], }
            leads_sourcewise_count = []
            sourcewise_conversion_rates = []
            sourcewise_leads_count_data = {
                'type':'bar',
                'label': 'Leads Count',
                'yAxisID': 'leads_count',
                'fill': True,
                'backgroundColor': 'rgba(255, 255, 255, 0)',
                'borderColor': 'rgba(49, 150, 76, 0.68)',
                'borderWidth': 1,
                'data': []
            }  


            sourcewise_leads_conversion_data = {
                'type':'line',
                'label': 'Conversion Rate (%)',
                'yAxisID': 'conversion_rates',
                'fill': True,
                'backgroundColor': 'rgba(255, 255, 255, 0)',
                'borderColor': 'rgba(249, 83, 0, 0.83)',
                'borderWidth': 1,
                'data': []
            }  

            for lead_source in lead_sources:
                source_leads_data = self.env['sales.tracker'].retrieve_employee_source_wise_lead_data(lead_source,employee,start_date,end_date)
                leads_sourcewise_count.append(source_leads_data['leads_count'])
                sourcewise_conversion_rates.append(source_leads_data['leads_conversion_rate'])

            sourcewise_leads_count_data['data'] = leads_sourcewise_count
            sourcewise_leads_conversion_data['data'] = sourcewise_conversion_rates
            employee_leads_data['sourcewise_leads_dataset'].append(sourcewise_leads_count_data)
            employee_leads_data['sourcewise_leads_dataset'].append(sourcewise_leads_conversion_data)


            leads_coursewise_count = []
            coursewise_conversion_rates = []
            coursewise_leads_count_data = {
                'type':'bar',
                'label': 'Leads Count',
                'yAxisID': 'leads_count',
                'fill': True,
                'backgroundColor': 'rgba(255, 255, 255, 0)',
                'borderColor': 'rgba(49, 150, 76, 0.68)',
                'borderWidth': 1,
                'data': []
            }  


            coursewise_leads_conversion_data = {
                'type':'line',
                'label': 'Conversion Rate (%)',
                'yAxisID': 'conversion_rates',
                'fill': True,
                'backgroundColor': 'rgba(255, 255, 255, 0)',
                'borderColor': 'rgba(249, 83, 0, 0.83)',
                'borderWidth': 1,
                'data': []
            }  

            for course in lead_courses:
                course_leads_data = self.env['sales.tracker'].retrieve_employee_course_wise_lead_data(course,employee,start_date,end_date)
                leads_coursewise_count.append(course_leads_data['leads_count'])
                coursewise_conversion_rates.append(course_leads_data['leads_conversion_rate'])

                
            coursewise_leads_count_data['data'] = leads_coursewise_count
            coursewise_leads_conversion_data['data'] = coursewise_conversion_rates
            employee_leads_data['coursewise_leads_dataset'].append(coursewise_leads_count_data)
            employee_leads_data['coursewise_leads_dataset'].append(coursewise_leads_conversion_data)


            year_target_data = self.env['sales.tracker'].retrieve_leads_target_count(employee,start_date,end_date)
            employee_leads_data['month_year_leads_count'] = year_target_data['month_year_leads_count']
            employee_leads_data['month_year_leads_target'] = year_target_data['month_year_leads_target']
            employee_leads_data['month_year_converted_leads_count'] = year_target_data['month_year_converted_leads_count']


            employee_leads_data['leads_count'] = self.env['sales.tracker'].get_employee_lead_count(employee,start_date,end_date)            
            return employee_leads_data
        else:
            return False

    def get_employee_marketing_data(self,employee,start_date=False,end_date=False):
        marketing_dept_obj = self.env['hr.department'].sudo().search([('name','=','Marketing')])
        if employee.department_id.id in marketing_dept_obj.child_ids.ids:
            rgba_colors = ['rgba(178, 56, 154, 0.75)', 'rgba(57, 141, 244, 0.52)', 'rgba(61, 14, 226, 0.88)', 'rgba(154, 29, 178, 0.51)', 'rgba(126, 101, 181, 0.05)', 'rgba(21, 80, 20, 0.70)', 'rgba(130, 79, 252, 0.09)', 'rgba(161, 125, 151, 0.61)', 'rgba(126, 124, 212, 0.81)', 'rgba(158, 94, 192, 0.75)', 'rgba(5, 19, 109, 0.87)', 'rgba(91, 247, 56, 0.89)', 'rgba(158, 182, 64, 0.12)', 'rgba(188, 190, 44, 0.53)', 'rgba(127, 164, 35, 0.92)', 'rgba(166, 173, 138, 0.32)', 'rgba(183, 241, 33, 0.89)', 'rgba(228, 183, 46, 0.94)', 'rgba(141, 226, 67, 0.39)', 'rgba(134, 126, 5, 0.13)', 'rgba(32, 190, 250, 0.85)', 'rgba(161, 59, 186, 0.20)', 'rgba(44, 217, 96, 0.68)', 'rgba(214, 67, 23, 0.77)', 'rgba(182, 127, 43, 0.94)', 'rgba(189, 3, 175, 0.71)', 'rgba(169, 148, 168, 0.69)', 'rgba(207, 205, 71, 0.74)', 'rgba(51, 140, 78, 0.42)', 'rgba(5, 246, 98, 0.81)', 'rgba(86, 128, 43, 0.90)', 'rgba(175, 77, 156, 0.63)', 'rgba(171, 104, 178, 0.31)', 'rgba(217, 229, 63, 0.47)', 'rgba(153, 138, 39, 0.09)', 'rgba(48, 141, 171, 0.01)', 'rgba(112, 207, 164, 0.50)', 'rgba(179, 184, 214, 0.61)', 'rgba(241, 14, 96, 0.44)', 'rgba(227, 53, 23, 0.54)', 'rgba(218, 215, 218, 0.87)', 'rgba(171, 194, 173, 0.57)', 'rgba(195, 154, 186, 0.04)', 'rgba(127, 118, 87, 0.01)', 'rgba(52, 222, 91, 0.32)', 'rgba(140, 238, 113, 0.55)', 'rgba(182, 249, 246, 0.76)', 'rgba(148, 12, 56, 0.61)', 'rgba(239, 154, 91, 0.33)', 'rgba(69, 251, 118, 0.25)']
            districts = dict(self.env['seminar.leads'].sudo().fields_get()['district']['selection'])
            district_names = list(dict(self.env['seminar.leads'].sudo().fields_get()['district']['selection']).values())
            employee_leads_data = {'districts':district_names, 'leads_dataset': [] }
            leads_count = []
            conversion_rates = []
            leads_count_data = {
                'type':'bar',

                'label': 'Leads Count',
                'yAxisID': 'leads_count',
                'fill': True,
                'backgroundColor': 'rgba(255, 255, 255, 0)',
                'borderColor': 'rgba(49, 150, 76, 0.68)',
                'borderWidth': 1,
                'data': []
            }  

            leads_conversion_data = {
                'type':'line',
                'label': 'Conversion Rate (%)',
                'yAxisID': 'conversion_rates',
                'fill': True,
                'backgroundColor': 'rgba(255, 255, 255, 0)',
                'borderColor': 'rgba(249, 83, 0, 0.83)',
                'borderWidth': 1,
                'data': []
            }  

            for district in districts.keys():
                district_leads_data = self.env['marketing.tracker'].retrieve_employee_district_wise_lead_data(district,employee,start_date,end_date)
                leads_count.append(district_leads_data['leads_count'])
                conversion_rates.append(district_leads_data['leads_conversion_rate'])
            leads_count_data['data'] = leads_count
            leads_conversion_data['data'] = conversion_rates
            employee_leads_data['leads_dataset'].append(leads_count_data)
            employee_leads_data['leads_dataset'].append(leads_conversion_data)

            year_target_data = self.env['marketing.tracker'].retrieve_leads_target_count(employee,start_date,end_date)
            employee_leads_data['year_leads_count'] = year_target_data['year_leads_count']
            employee_leads_data['year_leads_target'] = year_target_data['year_leads_target']

            employee_leads_data['leads_count'] = self.env['marketing.tracker'].get_employee_seminar_count(employee,start_date,end_date)            
            return employee_leads_data
        else:
            return False

    def get_common_performance_data(self,employee,start_date=False,end_date=False):

        common_performance = {}
        common_performance['qualitative_rating'] = 0
        
        qualitatives = actions_common.get_raw_qualitative_data(self,employee,start_date,end_date)
        actions_common.create_employee_qualitative_performance(self,qualitatives,employee)

        qualitative_perf = self.env['employee.qualitative.performance'].sudo().search([('employee','=',employee.id)])
        if qualitative_perf:
            common_performance['qualitative_rating'] = qualitative_perf[0].overall_average
        
        misc_domain = [('task_creator','=',employee.user_id.id),('state','=','completed')]
        to_do_domain = [('state','=','completed'),'|',('assigned_to','=',employee.user_id.id),('coworkers_ids','in',[employee.user_id.id] ), ('state','=','completed')]
        if start_date and end_date:
            misc_domain.extend([('date_completed','>=',start_date),('date_completed','<=',end_date)])
            to_do_domain.extend([('completed_date','>=',start_date),('completed_date','<=',end_date)])

        common_performance['misc_task_count'] = self.env['logic.task.other'].sudo().search_count(misc_domain)    
        common_performance['to_do_count'] = self.env['to_do.tasks'].sudo().search_count(to_do_domain)        
            
        return common_performance
    
    def get_digital_performance_data(self,employee,start_date=False,end_date=False):
        digital_dept_obj = self.env['hr.department'].sudo().search([('name','=','Digital')])
        if employee.department_id.id == digital_dept_obj.id:
            digital_domain = [('state','in',('completed','to_post','posted')), ('assigned_execs','in',[employee.user_id.id] ), ('assigned_execs','!=',False)]
            if start_date and end_date:
                digital_domain.extend([('date_completed', '>=',start_date), ('date_completed','<=',end_date)])
            task_count = self.env['digital.task'].sudo().search_count(digital_domain)

            digital_data = {'digital_task_count':task_count}
            return digital_data
        else:
            return False
        
    # get all other employees in the department
    def get_department_employees(self,employee):
        employees = self.env['hr.employee'].sudo().search([('department_id','=',employee.department_id.id),('id','!=',employee.id)])
        employees_data = []
        for employee in employees:
            data = {}
            data['id'] = employee.id
            data['name'] = employee.name
            employees_data.append(data)
        return employees_data
    
    @api.model
    def get_employee_details(self,employee_id):
        employee = self.env['hr.employee'].sudo().browse(int(employee_id))
        return {'name':employee.name}

    def check_access(self,employee):
        if self.env.user.has_group('logic_performance_tracker.group_perf_admin') \
            or self.env.user.has_group('logic_performance_tracker.group_perf_academic_head') \
            or self.env.user.has_group('logic_performance_tracker.group_perf_digital_head') \
            or self.env.user.has_group('logic_performance_tracker.group_perf_marketing_head') \
            or self.env.user.has_group('logic_performance_tracker.group_perf_sales_head') \
            or self.env.user.has_group('logic_performance_tracker.group_perf_accounts_head'):
            return True
        # elif employee.id in self.env.user.employee_id.child_ids.ids or (employee.id==self.env.user.employee_id.id):
        #     return True
        return False
    
    @api.model
    def retrieve_employee_performance(self,employee_id,start_date=False,end_date=False):
        
        employee = self.env['hr.employee'].sudo().browse(int(employee_id))

        if not self.check_access(employee):
            return False
        
        logger = logging.getLogger("Debugger: ")
        if start_date and end_date:
            start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)
            year = start_date.year
            month = actions_common.get_month_list().get(start_date.month)
        else:
            year = date.today().year
            month = actions_common.get_month_list().get(date.today().month)

        employee_data = {}

        # employee_data['years'] = [2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036, 2037]
        employee_data['department_employees'] = self.get_department_employees(employee)
        employee_data['misc_to_do_chart_dataset'] = self.get_line_chart_datasets(employee.id,start_date,end_date)
        employee_data['personal_data'] = self.get_employee_personal_data(employee)
        employee_data['academic_data'] = self.get_employee_academic_data(employee,start_date,end_date)
        employee_data['common_performance'] = self.get_common_performance_data(employee,start_date,end_date)
        # employee_data['line_chart_datasets'] = self.get_line_chart_datasets(employee)
        employee_data['digital_data'] = self.get_digital_performance_data(employee,start_date,end_date)
        employee_data['marketing_data'] = self.get_employee_marketing_data(employee,start_date,end_date)
        employee_data['sales_data'] = self.get_employee_sales_data(employee,start_date,end_date)

        employee_data['year'] = year
        employee_data['month'] = month.capitalize()

        if start_date and end_date:
            if start_date.month != end_date.month:
                employee_data['month'] = False

        return employee_data
