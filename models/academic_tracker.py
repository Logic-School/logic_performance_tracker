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
        managers=False
        manager=False
        employees = False
        upaya_domain = [('state','=','complete')]
        yes_plus_domain = [('state','=','complete')]
        sfc_domain = [('state','=','confirm')]
        exam_domain = []
        one_to_one_domain = []
        mock_interview_domain = [('state','=','done')]
        cip_domain = [('state','=','completed')]
        bring_buddy_domain = [('state','=','done')]

        logger.error(department_obj)

        if self.env.user.has_group('logic_performance_tracker.group_perf_admin'):

            academic_depts = self.env['hr.department'].search([('parent_id','=',department_obj[0].id)])
            academic_heads = []
            for academic_dept in academic_depts:
                if academic_dept.manager_id:
                    academic_heads.append(academic_dept.manager_id)
            academic_heads_data = [{'head_id':'all','name':'All'}]
            for academic_head in academic_heads:
                head_data = {}
                head_data['head_id'] = academic_head.id
                head_data['name'] = academic_head.name
                academic_heads_data.append(head_data)
            logger.error(academic_heads_data)
            if manager_id:
                manager = self.env['hr.employee'].sudo().browse(int(manager_id))
            elif department_obj:

                managers = self.env['hr.employee'].sudo().search([('department_id','=',department_obj[0].id),('child_ids','!=',False)])
                
                logger.error("managers")
                logger.error(managers)
            logger.error("manager")
            logger.error(manager)


        elif self.env.user.has_group('logic_performance_tracker.group_perf_academic_head'):
            manager = self.env.user.employee_id
            academic_heads_data = [{'head_id':manager.id,'name':manager.name}]
            
        if start_date and end_date:
            upaya_domain.extend([('date','>=',start_date),('date','<=',end_date)])
            yes_plus_domain.extend([('date_one','>=',start_date),('date_one','<=',end_date)])
            sfc_domain.extend([('date','>=',start_date),('date','<=',end_date)])
            exam_domain.extend([('date','>=',start_date),('date','<=',end_date)])
            one_to_one_domain.extend([('added_date','>=',start_date),('added_date','<=',end_date)])
            mock_interview_domain.extend([('date','>=',start_date),('date','<=',end_date)])
            cip_domain.extend([('date','>=',start_date),('date','<=',end_date)])
            bring_buddy_domain.extend([('date','>=',start_date),('date','<=',end_date)])

        logger.error(str(managers))
        if manager or managers:
            logger.error("inside ss")
            if managers:
                employees = self.env['hr.employee'].sudo().search([('department_id','=',department_obj[0].id),('parent_id','in',managers.ids)])
            else:
                logger.error("inside else, manager: "+manager.name)
                employees = self.env['hr.employee'].sudo().search([('department_id','=',department_obj[0].id),('parent_id','=',manager.id)])
            logger.error("employees: "+str(employees))
            employee_user_ids = employees.mapped('user_id.id')
            logger.error("employee_user_ids: "+str(employee_user_ids))
            
            upaya_domain.extend([('coordinator_id','in',employee_user_ids),('coordinator_id','!=',False)])
            yes_plus_domain.extend([('coordinator_id','in',employee_user_ids),('coordinator_id','!=',False)])
            sfc_domain.extend([('coordinator','in',employee_user_ids),('coordinator','!=',False)])
            exam_domain.extend([('coordinator','in',employee_user_ids),('coordinator','!=',False)])
            one_to_one_domain.extend([('coordinator_id','in',employee_user_ids),('coordinator_id','!=',False)])
            mock_interview_domain.extend([('coordinator','in',employee_user_ids),('coordinator','!=',False)])
            cip_domain.extend([('coordinator_id','in',employee_user_ids),('coordinator_id','!=',False)])
            bring_buddy_domain.extend([('coordinator_id','in',employee_user_ids),('coordinator_id','!=',False)])

        upaya_count = self.env['upaya.form'].sudo().search_count(upaya_domain)
        yes_plus_count = self.env['yes_plus.logic'].sudo().search_count(yes_plus_domain)
        sfc_count = self.env['student.faculty'].sudo().search_count(sfc_domain)
        exam_count = self.env['exam.details'].sudo().search_count(exam_domain)
        one_to_one_count = self.env['one_to_one.meeting'].sudo().search_count(one_to_one_domain)
        mock_interview_count = self.env['logic.mock_interview'].sudo().search_count(mock_interview_domain)
        cip_excel_count = self.env['logic.cip.form'].sudo().search_count(cip_domain)
        bring_buddy_count = self.env['bring.your.buddy'].sudo().search_count(bring_buddy_domain)

        dashboard_data = {
            'upaya_count':upaya_count,
            'yes_plus_count':yes_plus_count, 
            'sfc_count': sfc_count, 
            'exam_count':exam_count,
            'one_to_one_count':one_to_one_count,
            'mock_interview_count':mock_interview_count,
            'cip_excel_count':cip_excel_count,
            'bring_buddy_count':bring_buddy_count,
            'academic_heads': academic_heads_data,
            }

        employee_upaya_domain = [('state','=','complete')]
        employee_yes_plus_domain = [('state','=','complete')]
        employee_one_to_one_domain = []
        employee_sfc_domain = [('state','=','confirm')]
        employee_exam_domain = []
        employee_mock_interview_domain = [('state','=','done')]
        employee_cip_domain = [('state','=','completed')]
        employee_bring_buddy_domain = [('state','=','done')]

        if start_date and end_date:
            employee_upaya_domain.extend([('date', '>=',start_date), ('date','<=',end_date)])
            employee_yes_plus_domain.extend([('date_one', '>=',start_date), ('date_one','<=',end_date)])
            employee_one_to_one_domain.extend([('added_date', '>=',start_date), ('added_date','<=',end_date)])
            employee_sfc_domain.extend([('date', '>=',start_date), ('date','<=',end_date)])
            employee_exam_domain.extend([('date', '>=',start_date), ('date','<=',end_date)])
            employee_mock_interview_domain.extend([('date', '>=',start_date), ('date','<=',end_date)])
            employee_cip_domain.extend([('date', '>=',start_date), ('date','<=',end_date)])
            employee_bring_buddy_domain.append(('coordinator_id','in',employee_user_ids))

            if managers:
                dashboard_data['qualitatives'] = self.env['base.qualitative.analysis'].retrieve_performance(managers=managers)
            elif manager:
                dashboard_data['qualitatives'] = self.env['base.qualitative.analysis'].retrieve_performance(manager=manager)

        else:
            if managers:
                dashboard_data['qualitatives'] = self.env['base.qualitative.analysis'].retrieve_performance(managers=managers,start_date=start_date,end_date=end_date)
            elif manager:
                dashboard_data['qualitatives'] = self.env['base.qualitative.analysis'].retrieve_performance(manager=manager,start_date=start_date,end_date=end_date)
        
        for employee in employees:
            employees_data[employee.id] = {}
            employees_data[employee.id]['name'] = employee.name
            employees_data[employee.id]['upaya_count'] = self.env['upaya.form'].sudo().search_count(employee_upaya_domain+[('coordinator_id','=',employee.user_id.id),('coordinator_id','!=',False)])
            employees_data[employee.id]['yes_plus_count'] = self.env['yes_plus.logic'].sudo().search_count(employee_yes_plus_domain+[('coordinator_id','=',employee.user_id.id),('coordinator_id','!=',False)])
            employees_data[employee.id]['one2one_count'] = self.env['one_to_one.meeting'].sudo().search_count(employee_one_to_one_domain+[('coordinator_id','=',employee.user_id.id),('coordinator_id','!=',False)])
            employees_data[employee.id]['sfc_count'] = self.env['student.faculty'].sudo().search_count(employee_sfc_domain+[('coordinator','=',employee.user_id.id),('coordinator','!=',False)])
            employees_data[employee.id]['exam_count'] = self.env['exam.details'].sudo().search_count(employee_exam_domain+[('coordinator','=',employee.user_id.id),('coordinator','!=',False)])
            employees_data[employee.id]['mock_interview_count'] = self.env['logic.mock_interview'].sudo().search_count(employee_mock_interview_domain+[('coordinator','=',employee.user_id.id),('coordinator','!=',False)])
            employees_data[employee.id]['cip_excel_count'] = self.env['logic.cip.form'].sudo().search_count(employee_cip_domain+[('coordinator_id','=',employee.user_id.id),('coordinator_id','!=',False)])
            employees_data[employee.id]['bring_buddy_count'] = self.env['bring.your.buddy'].sudo().search_count(employee_bring_buddy_domain+[('coordinator_id','=',employee.user_id.id),('coordinator_id','!=',False)])


        dashboard_data['coordinator_data'] = employees_data
        return dashboard_data
    
    @api.model
    def retrieve_employee_academic_data(self,employee_id,start_date=False,end_date=False):
        logger = logging.getLogger("Debugger")
        logger.error("from"+start_date)
        logger.error("end"+end_date)

        employee = self.env['hr.employee'].sudo().browse(employee_id)
        if len(start_date)==0 or len(end_date)==0:
            upaya_objs = self.env['upaya.form'].sudo().search([('coordinator_id','!=',False),('coordinator_id','=',employee.user_id.id)])
            yes_plus_objs = self.env['yes_plus.logic'].sudo().search([('coordinator_id','!=',False),('coordinator_id','=',employee.user_id.id)])
            one_to_one_objs = self.env['one_to_one.meeting'].sudo().search([('coordinator_id','!=',False),('coordinator_id','=',employee.user_id.id)])
        
        else:
            start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)

            upaya_objs = self.env['upaya.form'].sudo().search([('coordinator_id','!=',False),('coordinator_id','=',employee.user_id.id),('date','>=',start_date),('date','<=',end_date)])
            yes_plus_objs = self.env['yes_plus.logic'].sudo().search([('coordinator_id','!=',False),('coordinator_id','=',employee.user_id.id),('date_one','>=',start_date),('date_one','<=',end_date)])
            one_to_one_objs = self.env['one_to_one.meeting'].sudo().search([('coordinator_id','!=',False),('coordinator_id','=',employee.user_id.id),('added_date','>=',start_date),('added_date','<=',end_date)])
        
        upaya_len = len(upaya_objs) if upaya_objs else 0
        yes_plus_len = len(yes_plus_objs) if yes_plus_objs else 0
        one_to_one_len = len(one_to_one_objs) if one_to_one_objs else 0

        longest_len = max(upaya_len,yes_plus_len,one_to_one_len) 
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
            employee_datas.append(current_row_data)

        logger.error(employee_datas)
        if len(employee_datas)>0:
            return employee_datas
        else:
            return False