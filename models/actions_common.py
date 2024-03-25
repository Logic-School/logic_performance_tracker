from odoo import models,fields,api
from odoo.exceptions import UserError
from datetime import date
import logging
import pdfkit
from . import pdf_reports

class StateAction(models.Model):
    _name = "performance.tracker"

    # @api.model
    def perf_tracker_open_action(self):
        if self.env.user.has_group('logic_performance_tracker.group_perf_crash_head'):
            action = self.env.ref("logic_performance_tracker.crash_performance_action").sudo().read()[0]
            return action
        elif self.env.user.has_group('logic_performance_tracker.group_perf_admin'):
            action = self.env.ref("logic_performance_tracker.tracker_dashboard_action").sudo().read()[0]
            return action
        elif self.env.user.has_group('logic_performance_tracker.group_perf_digital_head'):
            action = self.env.ref("logic_performance_tracker.digital_performance_action").sudo().read()[0]
            return action
        elif self.env.user.has_group('logic_performance_tracker.group_perf_academic_head'):
            action = self.env.ref("logic_performance_tracker.academic_performance_action").sudo().read()[0]
            return action
        elif self.env.user.has_group('logic_performance_tracker.group_perf_operations_head'):
            action = self.env.ref("logic_performance_tracker.operations_performance_action").sudo().read()[0]
            return action

        elif self.env.user.has_group('logic_performance_tracker.group_perf_marketing_head'):
            action = self.env.ref("logic_performance_tracker.marketing_performance_action").sudo().read()[0]
            return action
        elif self.env.user.has_group('logic_performance_tracker.group_perf_sales_head'):
            action = self.env.ref("logic_performance_tracker.sales_performance_action").sudo().read()[0]
            return action
        elif self.env.user.has_group('logic_performance_tracker.group_perf_it_head'):
            action = self.env.ref("logic_performance_tracker.it_performance_action").sudo().read()[0]
            return action
        elif self.env.user.has_group('logic_performance_tracker.group_perf_accounts_head'):
            action = self.env.ref("logic_performance_tracker.accounts_performance_action").sudo().read()[0]
            return action

        elif self.env.user.has_group('logic_performance_tracker.group_perf_residential_head'):
            action = self.env.ref("logic_performance_tracker.residential_performance_action").sudo().read()[0]
            return action

        elif self.env.user.has_group('logic_performance_tracker.group_perf_hr_head'):
            action = self.env.ref("logic_performance_tracker.hr_performance_action").sudo().read()[0]
            return action
        else:
            raise UserError("You do not have access to this application!")
        
    @api.model
    def get_performance_report_pdf(self,html_template, employee_name):
        logger = logging.getLogger('PDF Debug: ')
        options = {'enable-local-file-access': None, 'page-size':'A4','encoding': "UTF-8"}
        pdfkit.from_string(html_template,'/tmp/performance.pdf',options=options)
        with open('/tmp/performance.pdf','rb') as pdf_data:
            b64_pdf = pdf_reports.pdf_to_base64(pdf_data)
            logger.error("b64pdf"+str(type(b64_pdf)))
            return {'pdf_b64':b64_pdf, 'filename': str(employee_name)+'.pdf'}
    
    @api.model
    def retrieve_dashboard_data(self):
        dashboard_data = {}
        sales_department_obj = self.env['hr.department'].sudo().search([('name', '=', 'Sales')])
        sales_dept_childs = self.env['hr.department'].sudo().search([('parent_id', '=', sales_department_obj[0].id)])
        dashboard_data['sales_employees_count'] = self.env['hr.employee'].sudo().search_count([('department_id', 'in', sales_dept_childs.ids)])

        it_department_obj = self.env['hr.department'].sudo().search([('name', '=', 'IT')])
        it_dept_childs = self.env['hr.department'].sudo().search([('parent_id', '=', it_department_obj[0].id)])
        dashboard_data['it_employees_count'] = self.env['hr.employee'].sudo().search_count(
            [('department_id', 'in', it_dept_childs.ids)])

        academic_department_obj = self.env['hr.department'].sudo().search([('name','=','ACADEMICS')])
        academic_dept_childs = self.env['hr.department'].sudo().search([('parent_id','=',academic_department_obj[0].id)])
        dashboard_data['academic_employees_count'] = self.env['hr.employee'].sudo().search_count([('department_id','in',academic_dept_childs.ids)])

        digital_department_obj = self.env['hr.department'].sudo().search([('name','=','Digital')])
        digital_dept_childs = self.env['hr.department'].sudo().search([('parent_id','=',digital_department_obj[0].id)])
        dashboard_data['digital_employees_count'] = self.env['hr.employee'].sudo().search_count([('department_id','in',digital_dept_childs.ids)])

        marketing_department_obj = self.env['hr.department'].sudo().search([('name','=','Marketing')])
        marketing_dept_childs = self.env['hr.department'].sudo().search([('parent_id','=',marketing_department_obj[0].id)])
        dashboard_data['marketing_employees_count'] = self.env['hr.employee'].sudo().search_count([('department_id','in',marketing_dept_childs.ids)])

        accounts_department_obj = self.env['hr.department'].sudo().search([('name','=','Accounts')])
        accounts_dept_childs = self.env['hr.department'].sudo().search([('parent_id','=',accounts_department_obj[0].id)])
        dashboard_data['accounts_employees_count'] = self.env['hr.employee'].sudo().search_count([('department_id','in',accounts_dept_childs.ids)])
        
        crash_department_obj = self.env['hr.department'].sudo().search([('name','=','Crash')])
        crash_dept_childs = self.env['hr.department'].sudo().search([('parent_id','=',crash_department_obj[0].id)])
        dashboard_data['crash_employees_count'] = self.env['hr.employee'].sudo().search_count([('department_id','in',crash_dept_childs.ids)])

        operations_department_obj = self.env['hr.department'].sudo().search([('name', '=', 'Operations')])
        operations_dept_childs = self.env['hr.department'].sudo().search([('parent_id', '=', operations_department_obj[0].id)])
        dashboard_data['operations_employees_count'] = self.env['hr.employee'].sudo().search_count(
            [('department_id', 'in', operations_dept_childs.ids)])

        hr_department_obj = self.env['hr.department'].sudo().search([('name', '=', 'HR')])
        hr_dept_childs = self.env['hr.department'].sudo().search(
            [('parent_id', '=', hr_department_obj[0].id)])
        dashboard_data['hr_employees_count'] = self.env['hr.employee'].sudo().search_count(
            [('department_id', 'in', hr_dept_childs.ids)])
        
        residential_department_obj = self.env['hr.department'].sudo().search([('name', '=', 'Residential')])
        residential_dept_childs = self.env['hr.department'].sudo().search([('parent_id', '=', residential_department_obj[0].id)])
        dashboard_data['residential_employees_count'] = self.env['hr.employee'].sudo().search_count([('department_id','in',residential_dept_childs.ids)])

        return dashboard_data

def get_date_obj_from_string(from_date,end_date):
    logger = logging.getLogger("Date debug")
    logger.error('from_date'+str(from_date))
    logger.error('end_date'+str(end_date))

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
        # heads_data = [{'head_id':'all','department_name':'All'}]
        heads_data = []
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
        employees = self.env['hr.employee'].sudo().search([('department_id','in',department_obj[0].child_ids.ids), ('parent_id','in',managers.ids)])
        employees+=managers

    else:
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
    return qualitative_average

def get_raw_qualitative_data(self,employees=False,start_date=False,end_date=False):
    if start_date and end_date:
        qualitatives = self.env['base.qualitative.analysis'].retrieve_performance(employees=employees,start_date=start_date,end_date=end_date)
    else:
        qualitatives = self.env['base.qualitative.analysis'].retrieve_performance(employees=employees)
    return qualitatives

def create_employee_quantitative_performance(self,quantitatives,employee):
    logger = logging.getLogger("Debugger: ")

    quantitative_average = 0
    quantitative_values = {}
    if quantitatives.get(employee.name):
        for attribute in quantitatives[employee.name].keys():
            quantitative_average += quantitatives[employee.name][attribute]['average_rating']
            quantitative_values[attribute] = quantitatives[employee.name][attribute]['average_rating']
        quantitative_average = round(quantitative_average/len(quantitatives[employee.name].keys()), 2)
        logger.error("qual aver: "+str(quantitative_average))
    logger.error("qual values: "+str(quantitative_values))

    emp_qual_obj = self.env['employee.quantitative.performance'].sudo().search([('employee','=',employee.id)])
    if emp_qual_obj:
        emp_qual_obj.write({
            'overall_average': quantitative_average
        })
    else:
        self.env['employee.quantitative.performance'].sudo().create({
            'employee': employee.id,
            'overall_average': quantitative_average,
        })
    return quantitative_average

def get_raw_quantitative_data(self,employees=False,start_date=False,end_date=False):
    if start_date and end_date:
        quantitatives = self.env['quantitative.analysis'].retrieve_performance(employees=employees,start_date=start_date,end_date=end_date)
    else:
        quantitatives = self.env['quantitative.analysis'].retrieve_performance(employees=employees)
    return quantitatives

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

def get_ordered_quantitative_data(self,quantitatives,employees):

    logger = logging.getLogger("Debugger: ")
    quantitative_overall_objs = self.env['employee.quantitative.performance'].sudo().search([('employee','in',employees.ids)],order="overall_average desc")
    quantitative_overall_average_datas = {}
    for quantitative_overall_obj in quantitative_overall_objs:
        quantitative_overall_average_datas[quantitative_overall_obj.employee.name] = quantitative_overall_obj.overall_average
        if not quantitatives.get(quantitative_overall_obj.employee.name):
            quantitatives[quantitative_overall_obj.employee.name] = {}
    logger.error("quantitative_overall_average_datas: "+str(quantitative_overall_average_datas))
    logger.error("dashboard_data['quantitative']: "+str(quantitatives))
    return quantitatives,quantitative_overall_average_datas

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

def get_academic_windows(self,employee):
    academic_windows = self.env['logic.base.batch'].sudo().fields_get()['batch_window']['selection']
    academic_windows_data = []

    logger = logging.getLogger("debugger: ")
    logger.error("academic_windows"+str(academic_windows))
    for window in academic_windows:
        batch_count = self.env['logic.base.batch'].sudo().search_count([('batch_window','=',window[0]),('academic_coordinator','=',employee.user_id.id)])
        academic_windows_data.append({
            'id': window[0], 'name':window[1] + ' (' + str(batch_count) + ' Batches)'
            })
    logger.error("academic_windows_data"+str(academic_windows_data))

    return academic_windows_data


def get_academic_domains(self,department_obj,start_date=False,end_date=False,manager=False,managers=False,employee_user_ids=False,batch=False):
    logger = logging.getLogger("Debugger: ")
    upaya_domain = [('state','=','complete')]
    yes_plus_domain = [('state','=','complete')]
    sfc_domain = [('state','in',('confirm','sent_to_approve','approved','payment_request','paid'))]
    exam_domain = []
    one_to_one_domain = []
    mock_interview_domain = [('state','=','done')]
    cip_domain = [('state','=','completed')]
    bring_buddy_domain = [('state','=','done')]
    presentation_domain = []
    attendance_domain = []
    fpp_domain = [('state','=','completed')]

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
        presentation_domain.extend([('date','>=',start_date),('date','<=',end_date)])
        attendance_domain.extend([('date','>=',start_date),('date','<=',end_date)])
        fpp_domain.extend([('scheduled_date_one','>=',start_date),('scheduled_date_one','<=',end_date)])

    if batch:
        upaya_domain.extend([('batch_id','=',batch.id)])
        yes_plus_domain.extend([('batch_id','=',batch.id)])
        sfc_domain.extend([('batch_id','=',batch.id)])
        exam_domain.extend([('batch','=',batch.id)])
        # one_to_one_domain.extend([('added_date','>=',start_date),('added_date','<=',end_date)])
        # mock_interview_domain.extend([('date','>=',start_date),('date','<=',end_date)])
        cip_domain.extend([('batch_id','=',batch.id)])
        bring_buddy_domain.extend([('batch_id','=',batch.id)])
        presentation_domain.extend([('batch_id','=',batch.id)])
        attendance_domain.extend([('batch_id','=',batch.id)])
        fpp_domain.extend([('batch_id','=',batch.id)])

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
        presentation_domain.extend([('coordinator','in',employee_user_ids),('coordinator','!=',False)])
        attendance_domain.extend([('coordinator','in',employee_user_ids),('coordinator','!=',False)])
        fpp_domain.extend([('coordinator_id','in',employee_user_ids),('coordinator_id','!=',False)])

    return {
        'upaya_domain':upaya_domain,
        'yes_plus_domain':yes_plus_domain,
        'sfc_domain':sfc_domain,
        'exam_domain':exam_domain,
        'one_to_one_domain':one_to_one_domain,
        'mock_interview_domain':mock_interview_domain,
        'cip_domain':cip_domain,
        'bring_buddy_domain':bring_buddy_domain,
        'attendance_domain':attendance_domain,
        'presentation_domain':presentation_domain,
        'fpp_domain': fpp_domain,
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
        'presentation_count': self.env['logic.presentations'].sudo().search_count(academic_domains['presentation_domain']),
        'attendance_count': self.env['attendance.session'].sudo().search_count(academic_domains['attendance_domain']),
        'fpp_count': self.env['financial.planning.form'].sudo().search_count(academic_domains['fpp_domain']),
    }

def get_employee_to_do_data(self,employee,start_date=False,end_date=False):
    to_do_domain = [('state','=','completed'),'|',('assigned_to','=',employee.user_id.id),('coworkers_ids','in',[employee.user_id.id] )]
    if start_date and end_date:
        to_do_domain.extend([('completed_date','>=',start_date),('completed_date','<=',end_date)])
    to_do_count = self.env['to_do.tasks'].sudo().search(to_do_domain)
    return {'to_do_count': to_do_count}

def get_month_list():
    return {
        1: 'january',
        2: 'february',
        3: 'march',
        4: 'april',
        5: 'may',
        6: 'june',
        7: 'july',
        8: 'august',
        9: 'september',
        10: 'october',
        11: 'november',
        12: 'december',
    }

def get_day_month_year_from_timedelta(timedelta):
    logger = logging.getLogger("Timedelta Debug: ")
    total_days = timedelta.days

    logger.error('total_days'+str(total_days))

    # Calculate years, months, and remaining days
    years = total_days // 365
    remaining_days = total_days % 365
    months = remaining_days // 30
    days = remaining_days % 30

    return days, months, years

def get_employee_personal_to_do(self, employee, start_date=False, end_date=False):
    logger = logging.getLogger("To do debug: ")
    print(start_date, end_date, 'dates')
    personal_to_do = {}
    to_do_domain = [('state', '=', 'completed'), '|', ('assigned_to', '=', employee.user_id.id),
                    ('coworkers_ids', 'in', [employee.user_id.id]), ('state', '=', 'completed')]

    common_performance = self.env['to_do.tasks'].sudo().search(to_do_domain)
    if start_date and end_date:
        common_performance = common_performance.filtered(lambda filtered_to_do: filtered_to_do.assigned_date >= start_date and filtered_to_do.assigned_date <= end_date)
    for j in common_performance:
        print(j.name, 'common performance')
        if not personal_to_do.get(j.name):
            personal_to_do[j.name] = {'state': 'null'}
        state = j.state
        assigned_date = j.assigned_date
        rating = j.rating
        completed_date = j.completed_date
        if start_date and end_date:
            print(start_date, end_date, 'dates')
            if start_date <= assigned_date <= end_date:
                print(j.name, 'common performance filterd')
                personal_to_do[j.name]['state'] = j.state
                personal_to_do[j.name]['assigned_date'] = assigned_date
                personal_to_do[j.name]['rating'] = rating
                personal_to_do[j.name]['completed_date'] = completed_date
        else:
            print('not')
            personal_to_do[j.name]['state'] = state
            personal_to_do[j.name]['assigned_date'] = assigned_date
            personal_to_do[j.name]['rating'] = rating
            personal_to_do[j.name]['completed_date'] = completed_date

    return personal_to_do

def get_employee_personal_misc(self, employee, start_date=False, end_date=False):
    personal_misc = {}
    misc_domain = [('task_creator', '=', employee.user_id.id), ('state', '=', 'completed')]

    misc_performance = self.env['logic.task.other'].sudo().search(misc_domain)
    if start_date and end_date:
        common_performance = misc_performance.filtered(lambda filtered_misc: filtered_misc.date >= start_date and filtered_misc.date <= end_date)
    for j in misc_performance:

        if not personal_misc.get(j.name):
            personal_misc[j.name] = {'state': 'null'}
        state = j.state
        date = j.date
        task_submission_status = j.task_submission_status
        if start_date and end_date:

            if start_date <= date <= end_date:
                print(j.name, 'common performance filterd')

                personal_misc[j.name]['state'] = j.state
                personal_misc[j.name]['assigned_date'] = date
                personal_misc[j.name]['task_submission_status'] = task_submission_status
        else:

            personal_misc[j.name]['state'] = state
            personal_misc[j.name]['date'] = date
            personal_misc[j.name]['task_submission_status'] = task_submission_status
    print('misc')
    return personal_misc

def get_employee_personal_feedback(self, employee, start_date=False, end_date=False):
    logger = logging.getLogger("To do debug: ")
    print(start_date, end_date, 'dates')
    personal_feedback = {}
    feedback = [('employee_id', '=', employee.id)]

    common_performance = self.env['directors.feedback'].sudo().search(feedback)
    print(common_performance, 'feedback')

    for j in common_performance:
        print(j)
