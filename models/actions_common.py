from odoo import models,fields,api
from odoo.exceptions import UserError
from datetime import date
import logging

def get_date_obj_from_string(from_date,end_date):
    from_date = from_date.split("-")
    from_date = date(year=int(from_date[0]),month=int(from_date[1]), day=int(from_date[2]))
    end_date = end_date.split("-")
    end_date = date(year=int(end_date[0]),month=int(end_date[1]), day=int(end_date[2]))
    return from_date,end_date

def get_manager_managers_heads_data(self,department_obj,manager_id=False):
    logger = logging.getLogger("Debugger: ")

    managers=False
    manager=False
    if self.env.user.has_group('logic_performance_tracker.group_perf_admin'):

        depts = self.env['hr.department'].sudo().search([('parent_id','=',department_obj[0].id)])
        dept_heads = []
        for dept in depts:
            if dept.manager_id:
                dept_heads.append(dept.manager_id)
        heads_data = [{'head_id':'all','department_name':'All'}]
        for dept_head in dept_heads:
            head_data = {}
            head_data['head_id'] = dept_head.id
            head_data['department_name'] = dept_head.department_id.name
            heads_data.append(head_data)
        logger.error(heads_data)


        if manager_id:
            manager = self.env['hr.employee'].sudo().browse(int(manager_id))
        elif department_obj:

            managers = self.env['hr.employee'].sudo().search([('id','in',[dept_head.id for dept_head in dept_heads])])
            
            logger.error("managers")
            logger.error(managers)
            logger.error("department childs: "+str(department_obj[0].child_ids))
        logger.error("manager")
        logger.error(manager)
    else:
        manager = self.env.user.employee_id
        heads_data = [{'head_id':manager.id,'name':manager.name}]
        
    return manager,managers,heads_data

def get_employees(self,department_obj,manager=False,managers=False):
    logger = logging.getLogger("Debugger: ")

    if managers:
        logger.error("dept childs: "+str(department_obj[0].child_ids.ids))
        employees = self.env['hr.employee'].sudo().search([('department_id','in',department_obj[0].child_ids.ids),('parent_id','in',managers.ids)])
        employees+=managers

    else:
        logger.error("inside else, manager: "+manager.name)
        employees = self.env['hr.employee'].sudo().search([('department_id','=',manager.department_id.id),('parent_id','=',manager.id)])
        employees+=manager
    return employees

def create_employee_qualitative_performance(self,qualitatives,employee):
    logger = logging.getLogger("Debugger: ")

    qualitative_average = 0
    qualitative_values = {}
    if qualitatives.get(employee.name):
        for attribute in qualitatives[employee.name].keys():
            qualitative_average += qualitatives[employee.name][attribute]['average_rating']
            qualitative_values[attribute] = qualitatives[employee.name][attribute]['average_rating']
        qualitative_average = round(qualitative_average/len(qualitatives[employee.name].keys()), 2)
        logger.error("qual aver: "+str(qualitative_average))
    logger.error("qual values: "+str(qualitative_values))
    
    emp_qual_obj = self.env['employee.qualitative.performance'].sudo().search([('employee','=',employee.id)])
    if emp_qual_obj:
        emp_qual_obj.write({
            'overall_average': qualitative_average
        })
    else:
        self.env['employee.qualitative.performance'].sudo().create({
            'employee': employee.id,
            'overall_average': qualitative_average,
        })

def get_raw_qualitative_data(self,employees=False,start_date=False,end_date=False):
    if start_date and end_date:
        qualitatives = self.env['base.qualitative.analysis'].retrieve_performance(employees=employees,start_date=start_date,end_date=end_date)
    else:
        qualitatives = self.env['base.qualitative.analysis'].retrieve_performance(employees=employees)
    return qualitatives

def get_ordered_qualitative_data(self,qualitatives,employees):

    logger = logging.getLogger("Debugger: ")
    qualitative_overall_objs = self.env['employee.qualitative.performance'].sudo().search([('employee','in',employees.ids)],order="overall_average desc")
    qualitative_overall_average_datas = {}
    for qualitative_overall_obj in qualitative_overall_objs:
        qualitative_overall_average_datas[qualitative_overall_obj.employee.name] = qualitative_overall_obj.overall_average
        if not qualitatives.get(qualitative_overall_obj.employee.name):
            qualitatives[qualitative_overall_obj.employee.name] = {}
    logger.error("qualitative_overall_average_datas: "+str(qualitative_overall_average_datas))
    logger.error("dashboard_data['qualitatives']: "+str(qualitatives))
    return qualitatives,qualitative_overall_average_datas 

def get_org_datas_dept_names(manager,managers):
    if managers:
        org_datas = [manager.get_organisation_data(manager) for manager in managers]
        dept_names = [manager.department_id.name for manager in managers]
    elif manager:
        org_datas = [manager.get_organisation_data(manager)]
        dept_names = [manager.department_id.name]
    return org_datas,dept_names

def get_miscellaneous_performances(self,employees,start_date,end_date):
    if start_date or end_date:
        other_performances = self.env['logic.task.other'].retrieve_performance(employees,start_date,end_date)
    else:
        other_performances =  self.env['logic.task.other'].retrieve_performance(employees)
    return other_performances

class StateAction(models.Model):
    _name = "performance.tracker"

    # @api.model
    def perf_tracker_open_action(self):
        if self.env.user.has_group('logic_performance_tracker.group_perf_admin') or self.env.user.has_group('logic_performance_tracker.group_perf_digital_head'):
            action = self.env.ref("logic_performance_tracker.digital_performance_action").sudo().read()[0]
            return action
        elif self.env.user.has_group('logic_performance_tracker.group_perf_admin') or self.env.user.has_group('logic_performance_tracker.group_perf_academic_head'):
            action = self.env.ref("logic_performance_tracker.academic_performance_action").sudo().read()[0]
            return action
        elif self.env.user.has_group('logic_performance_tracker.group_perf_marketing_head') or self.env.user.has_group('logic_performance_tracker.group_perf_academic_head'):
            action = self.env.ref("logic_performance_tracker.marketing_performance_action").sudo().read()[0]
            return action

        else:
            raise UserError("You do not have access to this application!")

    # @api.model
    # def action_open_view(self,model_name,state):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': model_name,
    #         'view_mode': 'tree',
    #         'res_model': model_name,
    #         'domain': [('state','=',state)],
    #         'target': 'current',
    #     }
    
    # @api.model
    # def retrieve_dashboard_data(self,model_name):
    #     records = self.env[model_name].search([])
    #     dashboard_data = {}
    #     states = {}
    #     for record in records:
    #         try:
    #             states[record.state][1]+=1
    #         except:
    #             states[record.state] = [dict(record._fields['state'].selection).get(record.state),1]
    #     dashboard_data['states'] = states
    #     dashboard_data['performances'] = self.env['digital.executive.performance'].action_executive_performance()
    #     return dashboard_data

def get_academic_domains(self,department_obj,start_date=False,end_date=False,manager=False,managers=False,employee_user_ids=False):
    logger = logging.getLogger("Debugger: ")
    upaya_domain = [('state','=','complete')]
    yes_plus_domain = [('state','=','complete')]
    sfc_domain = [('state','=','confirm')]
    exam_domain = []
    one_to_one_domain = []
    mock_interview_domain = [('state','=','done')]
    cip_domain = [('state','=','completed')]
    bring_buddy_domain = [('state','=','done')]

    logger.error(department_obj)

    if start_date and end_date:
        upaya_domain.extend([('date','>=',start_date),('date','<=',end_date)])
        yes_plus_domain.extend([('date_one','>=',start_date),('date_one','<=',end_date)])
        sfc_domain.extend([('date','>=',start_date),('date','<=',end_date)])
        exam_domain.extend([('date','>=',start_date),('date','<=',end_date)])
        one_to_one_domain.extend([('added_date','>=',start_date),('added_date','<=',end_date)])
        mock_interview_domain.extend([('date','>=',start_date),('date','<=',end_date)])
        cip_domain.extend([('date','>=',start_date),('date','<=',end_date)])
        bring_buddy_domain.extend([('date','>=',start_date),('date','<=',end_date)])

    if (manager or managers or employee_user_ids):
        logger.error("inside ss")
        if not employee_user_ids:
            employees = get_employees(self,department_obj,manager,managers)
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
    return {
        'upaya_domain':upaya_domain,
        'yes_plus_domain':yes_plus_domain,
        'sfc_domain':sfc_domain,
        'exam_domain':exam_domain,
        'one_to_one_domain':one_to_one_domain,
        'mock_interview_domain':mock_interview_domain,
        'cip_domain':cip_domain,
        'bring_buddy_domain':bring_buddy_domain
    }

def get_academic_counts(self,academic_domains):
    return {
        'upaya_count' : self.env['upaya.form'].sudo().search_count(academic_domains['upaya_domain']),
        'yes_plus_count' : self.env['yes_plus.logic'].sudo().search_count(academic_domains['yes_plus_domain']),
        'sfc_count' : self.env['student.faculty'].sudo().search_count(academic_domains['sfc_domain']),
        'exam_count' : self.env['exam.details'].sudo().search_count(academic_domains['exam_domain']),
        'one_to_one_count' : self.env['one_to_one.meeting'].sudo().search_count(academic_domains['one_to_one_domain']),
        'mock_interview_count' : self.env['logic.mock_interview'].sudo().search_count(academic_domains['mock_interview_domain']),
        'cip_excel_count' : self.env['logic.cip.form'].sudo().search_count(academic_domains['cip_domain']),
        'bring_buddy_count' : self.env['bring.your.buddy'].sudo().search_count(academic_domains['bring_buddy_domain']),
    }