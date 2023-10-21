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

        depts = self.env['hr.department'].search([('parent_id','=',department_obj[0].id)])
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
        employees&=managers

    else:
        logger.error("inside else, manager: "+manager.name)
        employees = self.env['hr.employee'].sudo().search([('department_id','=',manager.department_id.id),('parent_id','=',manager.id)])
        employees&=manager
    return employees

def create_employee_qualitative_performance(self,dashboard_data,employee):
    logger = logging.getLogger("Debugger: ")

    qualitative_average = 0
    qualitative_values = {}
    if dashboard_data['qualitatives'].get(employee.name):
        for attribute in dashboard_data['qualitatives'][employee.name].keys():
            qualitative_average += dashboard_data['qualitatives'][employee.name][attribute]['average_rating']
            qualitative_values[attribute] = dashboard_data['qualitatives'][employee.name][attribute]['average_rating']
        qualitative_average = round(qualitative_average/len(dashboard_data['qualitatives'][employee.name].keys()), 2)
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

def get_raw_qualitative_data(self,manager=False,managers=False,start_date=False,end_date=False):
    if start_date and end_date:
        if managers:
            qualitatives = self.env['base.qualitative.analysis'].retrieve_performance(managers=managers,start_date=start_date,end_date=end_date)
        elif manager:
            qualitatives = self.env['base.qualitative.analysis'].retrieve_performance(manager=manager,start_date=start_date,end_date=end_date)
    else:
        if managers:
            qualitatives = self.env['base.qualitative.analysis'].retrieve_performance(managers=managers)
        elif manager:
            qualitatives = self.env['base.qualitative.analysis'].retrieve_performance(manager=manager)
    return qualitatives

def get_ordered_qualitative_data(self,dashboard_data,employees):

    logger = logging.getLogger("Debugger: ")
    qualitative_overall_objs = self.env['employee.qualitative.performance'].sudo().search([('employee','in',employees.ids)],order="overall_average desc")
    qualitative_overall_average_datas = {}
    for qualitative_overall_obj in qualitative_overall_objs:
        qualitative_overall_average_datas[qualitative_overall_obj.employee.name] = qualitative_overall_obj.overall_average
        if not dashboard_data['qualitatives'].get(qualitative_overall_obj.employee.name):
            dashboard_data['qualitatives'][qualitative_overall_obj.employee.name] = {}
    logger.error("qualitative_overall_average_datas: "+str(qualitative_overall_average_datas))
    logger.error("dashboard_data['qualitatives']: "+str(dashboard_data['qualitatives']))
    return dashboard_data['qualitatives'],qualitative_overall_average_datas 

def get_org_datas_dept_names(manager,managers):
    if managers:
        org_datas = [manager.get_organisation_data(manager) for manager in managers]
        dept_names = [manager.department_id.name for manager in managers]
    elif manager:
        org_datas = [manager.get_organisation_data(manager)]
        dept_names = [manager.department_id.name]
    return org_datas,dept_names

def get_miscellaneous_performances(self,manager,managers,start_date,end_date):
    if managers:
        if start_date or end_date:
            other_performances = self.env['logic.task.other'].retrieve_performance(False,managers,start_date,end_date)
        else:
            other_performances =  self.env['logic.task.other'].retrieve_performance(False,managers)
    elif manager:
        if start_date or end_date:
            other_performances = self.env['logic.task.other'].retrieve_performance(manager,False,start_date,end_date)
        else:
            other_performances =  self.env['logic.task.other'].retrieve_performance(manager,False)
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