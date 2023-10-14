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
        elif model_name=="logic.cip.form":
            domain = [['coordinator_id','=',employee.user_id.id]]
        elif model_name=="bring.your.buddy":
            domain = [['coordinator_id','=',employee.user_id.id]]
        logger.error("domain: "+str(domain))
        return domain

    @api.model
    def retrieve_employee_performance(self,employee_id):
        logger = logging.getLogger("Debugger: ")
        employee = self.env['hr.employee'].browse(int(employee_id))
        employee_data = {}
        academic_coord_perfs = self.env['academic.coordinator.performance'].sudo().search([('employee','=',employee.id)])
        logger.error("Perf objs: "+str(academic_coord_perfs))
        for coord_perf in academic_coord_perfs:
            employee_data['academic_data'] = {}
            employee_data['academic_data']['name'] = coord_perf.employee.name
            employee_data['academic_data']['upaya_count'] = coord_perf.upaya_count
            employee_data['academic_data']['yes_plus_count'] = coord_perf.yes_plus_count
            employee_data['academic_data']['one2one_count'] = coord_perf.one2one_count
            employee_data['academic_data']['sfc_count'] = coord_perf.sfc_count
            employee_data['academic_data']['exam_count'] = coord_perf.exam_count
            employee_data['academic_data']['mock_interview_count'] = coord_perf.mock_interview_count
            employee_data['academic_data']['cip_excel_count'] = coord_perf.cip_excel_count
            employee_data['academic_data']['bring_buddy_count'] = coord_perf.bring_buddy_count
            employee_data['academic_data']['total_completed'] = coord_perf.total_completed
        return employee_data
