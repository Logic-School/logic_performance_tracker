from odoo import models,fields,api
from odoo.exceptions import UserError
from . import actions_common
class AcademicTracker(models.Model):
    _name = "academic.tracker"
    
    @api.model
    def retrieve_dashboard_data(self,start_date=False,end_date=False):

        if not start_date or not end_date:
            upaya_count = self.env['upaya.form'].sudo().search_count([])
            yes_plus_count = self.env['yes_plus.logic'].sudo().search_count([])
            sfc_count = self.env['student.faculty'].sudo().search_count([])
            exam_count = self.env['exam.details'].sudo().search_count([])
        else:
            start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)

            upaya_count = self.env['upaya.form'].sudo().search_count([('date','>=',start_date),('date','<=',end_date)])
            yes_plus_count = self.env['yes_plus.logic'].sudo().search_count([('date_one','>=',start_date),('date_one','<=',end_date)])
            sfc_count = self.env['student.faculty'].sudo().search_count([('date','>=',start_date),('date','<=',end_date)])
            exam_count = self.env['exam.details'].sudo().search_count([('date','>=',start_date),('date','<=',end_date)])

        dashboard_data = {'upaya_count':upaya_count, 'yes_plus_count':yes_plus_count, 'sfc_count': sfc_count, 'exam_count':exam_count}
        employees_data = {}
        department_obj = self.env['hr.department'].sudo().search([('name','=','ACADEMICS')])
        manager=False
        managers=False

        if self.env.user.has_group('logic_performance_tracker.group_perf_admin'):
            if department_obj:
                managers = self.env['hr.employee'].sudo().search([('department_id','=',department_obj.id),('child_ids','!=',False)])
                employees = self.env['hr.employee'].sudo().search([('department_id','=',department_obj.id)])
                # for employee in employees:
                #     employees_data[employee.id] = {}
                #     employees_data[employee.id]['name'] = employee.name
                #     employees_data[employee.id]['upaya_count'] = self.env['upaya.form'].sudo().search_count([('coordinator_id','=',employee.user_id.id)])
                #     employees_data[employee.id]['yes_plus_count'] = self.env['yes_plus.logic'].sudo().search_count([('coordinator_id','=',employee.user_id.id)])
                #     employees_data[employee.id]['one2one_count'] = self.env['one_to_one.meeting'].sudo().search_count([('coordinator_id','=',employee.user_id.id)])

                # raise UserError(str(employees_data))
        elif self.env.user.has_group('logic_performance_tracker.group_perf_academic_head'):
            manager = self.env.user.employee_id
            employees = self.env['hr.employee'].sudo().search([('department_id','=',department_obj.id),('parent_id','=',manager.id)])
        if not start_date or not end_date:
            
            for employee in employees:
                employees_data[employee.id] = {}
                employees_data[employee.id]['name'] = employee.name
                employees_data[employee.id]['upaya_count'] = self.env['upaya.form'].sudo().search_count([('coordinator_id','=',employee.user_id.id),('state','=','complete')])
                employees_data[employee.id]['yes_plus_count'] = self.env['yes_plus.logic'].sudo().search_count([('coordinator_id','=',employee.user_id.id),('state','=','complete')])
                employees_data[employee.id]['one2one_count'] = self.env['one_to_one.meeting'].sudo().search_count([('coordinator_id','=',employee.user_id.id)])
            
            if managers:
                dashboard_data['qualitatives'] = self.env['base.qualitative.analysis'].retrieve_performance(managers=managers)
            elif manager:
                dashboard_data['qualitatives'] = self.env['base.qualitative.analysis'].retrieve_performance(manager=manager)

        else:
            for employee in employees:
                employees_data[employee.id] = {}
                employees_data[employee.id]['name'] = employee.name
                employees_data[employee.id]['upaya_count'] = self.env['upaya.form'].sudo().search_count([('coordinator_id','=',employee.user_id.id),('state','=','complete'),('date', '>=',start_date), ('date','<=',end_date)])
                employees_data[employee.id]['yes_plus_count'] = self.env['yes_plus.logic'].sudo().search_count([('coordinator_id','=',employee.user_id.id),('state','=','complete'),('date_one', '>=',start_date), ('date_one','<=',end_date)])
                employees_data[employee.id]['one2one_count'] = self.env['one_to_one.meeting'].sudo().search_count([('coordinator_id','=',employee.user_id.id),('added_date', '>=',start_date), ('added_date','<=',end_date)])
            if managers:
                dashboard_data['qualitatives'] = self.env['base.qualitative.analysis'].retrieve_performance(managers=managers,start_date=start_date,end_date=end_date)
            elif manager:
                dashboard_data['qualitatives'] = self.env['base.qualitative.analysis'].retrieve_performance(manager=manager,start_date=start_date,end_date=end_date)
            # dashboard_data['qualitatives'] = self.env['base.qualitative.analysis'].retrieve_performance(manager=)
        dashboard_data['coordinator_data'] = employees_data

        return dashboard_data