from odoo import models,fields,api
from odoo.exceptions import UserError
from . import actions_common
import logging
class AcademicTracker(models.Model):
    _name = "academic.tracker"
    
    @api.model
    def retrieve_dashboard_data(self,start_date=False,end_date=False,manager_id=False):
        logger = logging.getLogger("Debugger: ")

        logger.error("Manager Id: "+str(manager_id))
        if start_date and end_date:
            start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)

        dashboard_data = {}
        employees_data = {}
        department_obj = self.env['hr.department'].sudo().search([('name','=','ACADEMICS')])

        if not manager_id:
            manager_id = department_obj.child_ids[0].manager_id.id

        manager,managers,department_heads_data = actions_common.get_manager_managers_heads_data(self,department_obj,manager_id)

        employees = actions_common.get_employees(self,department_obj,manager,managers)

        academic_domains = actions_common.get_academic_domains(self,department_obj=department_obj,start_date=start_date,end_date=end_date,manager=manager,managers=managers,employee_user_ids=False)

        academic_counts = actions_common.get_academic_counts(self,academic_domains)
        dashboard_data = {
            'upaya_count':academic_counts['upaya_count'],
            'yes_plus_count':academic_counts['yes_plus_count'], 
            'sfc_count': academic_counts['sfc_count'], 
            'exam_count':academic_counts['exam_count'],
            'one_to_one_count': academic_counts['one_to_one_count'],
            'mock_interview_count':academic_counts['mock_interview_count'],
            'cip_excel_count':academic_counts['cip_excel_count'],
            'bring_buddy_count':academic_counts['bring_buddy_count'],
            'department_heads': department_heads_data,
            }


        dashboard_data['qualitatives'] = actions_common.get_raw_qualitative_data(self,employees,start_date,end_date)

        for employee in employees:
            total_completed=0
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
                'total_completed': total_completed
            }

            acad_coord_perf_obj = self.env['academic.coordinator.performance'].sudo().search([('employee','=',employee.id)])
            if acad_coord_perf_obj:
                acad_coord_perf_obj.write(values)
            else:
                self.env['academic.coordinator.performance'].create(values)

            actions_common.create_employee_qualitative_performance(self,dashboard_data['qualitatives'],employee)

        academic_coord_perfs = self.env['academic.coordinator.performance'].sudo().search([('employee','in',employees.ids)])
        logger.error(academic_coord_perfs)
        for coord_perf in academic_coord_perfs:
            emp_id_name = str(coord_perf.employee.id)+" "
            employees_data[emp_id_name] = {}
            employees_data[emp_id_name]['name'] = coord_perf.employee.name
            employees_data[emp_id_name]['upaya_count'] = coord_perf.upaya_count
            employees_data[emp_id_name]['yes_plus_count'] = coord_perf.yes_plus_count
            employees_data[emp_id_name]['one2one_count'] = coord_perf.one2one_count
            employees_data[emp_id_name]['sfc_count'] = coord_perf.sfc_count
            employees_data[emp_id_name]['exam_count'] = coord_perf.exam_count
            employees_data[emp_id_name]['mock_interview_count'] = coord_perf.mock_interview_count
            employees_data[emp_id_name]['cip_excel_count'] = coord_perf.cip_excel_count
            employees_data[emp_id_name]['bring_buddy_count'] = coord_perf.bring_buddy_count
            employees_data[emp_id_name]['total_completed'] = coord_perf.total_completed
            # coord_perf.total_completed = 

        dashboard_data['coordinator_data'] = employees_data
        dashboard_data['qualitatives'],dashboard_data['qualitative_overall_averages'] = actions_common.get_ordered_qualitative_data(self,dashboard_data['qualitatives'],employees)    
        dashboard_data['other_performances'] = actions_common.get_miscellaneous_performances(self,employees,start_date,end_date)
        logger.error("dashboard_data['other_performances'] "+str(dashboard_data['other_performances']))

        dashboard_data['org_datas'],dashboard_data['dept_names'] = actions_common.get_org_datas_dept_names(manager,managers)
        return dashboard_data
    
    @api.model
    def retrieve_employee_academic_data(self,employee_id,start_date=False,end_date=False):
        employee_id = int(employee_id.strip())
        logger = logging.getLogger("Debugger")
        logger.error("from"+start_date)
        logger.error("end"+end_date)

        employee = self.env['hr.employee'].sudo().browse(employee_id)
        if len(start_date)==0 or len(end_date)==0:
            upaya_objs = self.env['upaya.form'].sudo().search([('coordinator_id','!=',False),('coordinator_id','=',employee.user_id.id)])
            yes_plus_objs = self.env['yes_plus.logic'].sudo().search([('coordinator_id','!=',False),('coordinator_id','=',employee.user_id.id)])
            one_to_one_objs = self.env['one_to_one.meeting'].sudo().search([('coordinator_id','!=',False),('coordinator_id','=',employee.user_id.id)])
            exam_objs = self.env['exam.details'].sudo().search([('coordinator','!=',False),('coordinator','=',employee.user_id.id)])
        else:
            start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)

            upaya_objs = self.env['upaya.form'].sudo().search([('coordinator_id','!=',False),('coordinator_id','=',employee.user_id.id),('date','>=',start_date),('date','<=',end_date)])
            yes_plus_objs = self.env['yes_plus.logic'].sudo().search([('coordinator_id','!=',False),('coordinator_id','=',employee.user_id.id),('date_one','>=',start_date),('date_one','<=',end_date)])
            one_to_one_objs = self.env['one_to_one.meeting'].sudo().search([('coordinator_id','!=',False),('coordinator_id','=',employee.user_id.id),('added_date','>=',start_date),('added_date','<=',end_date)])
            exam_objs = self.env['exam.details'].sudo().search([('coordinator','!=',False),('coordinator','=',employee.user_id.id),('date','>=',start_date),('date','<=',end_date)])

        upaya_len = len(upaya_objs) if upaya_objs else 0
        yes_plus_len = len(yes_plus_objs) if yes_plus_objs else 0
        one_to_one_len = len(one_to_one_objs) if one_to_one_objs else 0
        exam_len = len(exam_objs) if exam_objs else 0

        longest_len = max(upaya_len,yes_plus_len,one_to_one_len,exam_len) 
        employee_datas = []
        for i in range(longest_len):
            current_row_data = {}
            try:
                current_row_data['upaya_name'] = upaya_objs[i].name
                current_row_data['upaya_name']+= (" - " + str(upaya_objs[i].date)) if upaya_objs[i].date else ''
            except:
                current_row_data['upaya_name'] = '-'

            try:
                current_row_data['yes_plus_name'] = yes_plus_objs[i].name
            except:
                current_row_data['yes_plus_name'] = '-'

            try:
                current_row_data['one_to_one_name'] = one_to_one_objs[i].name
            except:
                current_row_data['one_to_one_name'] = '-'

            current_row_data['exam'] = {} 

            try:
                present_count = list(exam_objs[i].student_results.mapped('present')).count(True)
                total_students = len(exam_objs[i].student_results)
                current_row_data['exam']['name'] = exam_objs[i].name
                current_row_data['exam']['present_count'] = present_count
                current_row_data['exam']['total_count'] = total_students
            except Exception as exception:
                logger.error("exception")
                logger.error(exception)
                current_row_data['exam']['name'] = '-'
            employee_datas.append(current_row_data)

        logger.error(employee_datas)
        if len(employee_datas)>0:
            return employee_datas
        else:
            return False