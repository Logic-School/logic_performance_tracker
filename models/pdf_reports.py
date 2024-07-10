import base64
from . import actions_common, leave_data, employee_performance
import logging
from . import academic_data


def get_employee_performance_data(self, employee_id, start_date, end_date):
    employee = self.env['hr.employee'].sudo().browse(int(employee_id))
    employee_data = {}

    employee_data['common_performance'] = get_employee_common_performance_data(self, employee, start_date, end_date)

    if employee.department_id:
        if employee.department_id.parent_id.name == 'Sales':
            employee_data['sales_data'] = get_employee_sales_data(self, employee, start_date, end_date)
        elif employee.department_id.parent_id.name == 'Crash':
            employee_data['sales_data'] = get_employee_sales_data(self, employee, start_date, end_date, crash=True)
            employee_data['crash_data'] = get_employee_crash_data(self, employee, start_date, end_date)
        if start_date and end_date:
            start_date, end_date = actions_common.get_date_obj_from_string(start_date, end_date)
        if employee.department_id.parent_id.name == 'Marketing':
            employee_data['marketing_data'] = get_employee_marketing_data(self, employee, start_date, end_date)
        elif employee.department_id.parent_id.name == 'ACADEMICS':
            employee_data['academic_data'] = get_employee_academic_data(self, employee, start_date, end_date)
    employee_data['personal_data'] = self.env['logic.employee.performance'].sudo().get_employee_personal_data(employee)
    employee_data['leave_data'] = leave_data.get_employee_leave_data(self, employee, start_date, end_date)

    employee_data['to_do_tasks'] = actions_common.get_employee_personal_to_do(self, employee, start_date, end_date)
    employee_data['miscellaneous_tasks'] = actions_common.get_employee_personal_misc(self, employee, start_date, end_date)

    if start_date and end_date:
        # start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)
        employee_data['start_date'] = start_date.strftime("%d / %m / %Y")
        employee_data['end_date'] = end_date.strftime("%d / %m / %Y")
    print(employee_data, "employee_to_do")
    return employee_data


def pdf_to_base64(file):
    file_bytes = base64.b64encode(file.read())
    # base_64 = file_bytes.decode("ascii")
    return file_bytes


def get_employee_common_performance_data(self, employee, start_date=False, end_date=False):
    common_performance_data = self.env['logic.common.task.performance'].sudo().create_employee_common_task_performance(
        employee, start_date, end_date)

    return common_performance_data


def get_employee_academic_data(self, employee, start_date=False, end_date=False):
    employee_academic_data = {}
    employee_academic_data['is_academic_head'] = employee.department_id.manager_id.id == employee.id
    if employee_academic_data['is_academic_head']:
        employee_academic_data['academic_head_data'] = get_academic_head_data(self, employee)
    employee_academic_data['batch_datas'] = get_employee_batch_datas(self, employee, start_date, end_date)
    return employee_academic_data


def get_employee_crash_data(self, employee, start_date=False, end_date=False):
    print('craassshhhh')
    employee_crash_data = {}
    employee_crash_data['is_crash_head'] = employee.department_id.manager_id.id == employee.id
    # if employee_crash_data['is_crash_head']:
    #     employee_crash_data['crash_head_data'] = get_crash_head_data(self, employee)
    # employee_crash_data['crash_datas'] = get_crash_datas(self, employee, start_date, end_date)
    return {}


def get_academic_head_data(self, employee):
    academic_head_data = {}
    batch_count = 0
    courses = self.env['logic.base.courses'].sudo().search(
        [('academic_head', '=', employee.user_id.id), ('name', 'not in', ('Nill', "DON'T USE", 'Nil')),
         ('type', '!=', 'crash')])
    course_names = courses.mapped('name')
    branch_names = self.env['logic.base.branches'].sudo().search([('branch_name', '!=', 'Nil')]).mapped('branch_name')
    batches = self.env['logic.base.batch'].sudo().search([('course_id', 'in', courses.ids)])
    subordinates = employee.child_ids
    academic_head_data['batch_count'] = len(batches)
    academic_head_data['course_count'] = len(courses)
    academic_head_data['subordinates_count'] = len(subordinates)
    subordinates_data = {}
    for subordinate in subordinates:
        subordinates_data[subordinate.name] = {}
        subordinates_data[subordinate.name]['batches_data'] = []
        batches = self.env['logic.base.batch'].sudo().search([('academic_coordinator', '=', subordinate.user_id.id)])
        for batch in batches:
            batch_data = {}
            batch_data['batch_name'] = batch.name
            batch_data['students_rating'] = self.env['academic.tracker'].sudo().get_batchwise_coordinator_rating(
                employee, batch)
            batch_data['students_count'] = self.env['logic.students'].sudo().search_count([('batch_id', '=', batch.id)])
            subordinates_data[subordinate.name]['batches_data'].append(batch_data)
    return {'branch_names': branch_names, 'course_names': course_names, 'subordinates_data': subordinates_data}


def get_employee_batch_datas(self, employee, start_date=False, end_date=False):
    batches = self.env['logic.base.batch'].sudo().search([('academic_coordinator', '=', employee.user_id.id)])
    batch_datas = []
    for batch_obj in batches:
        batch_strength = self.env['logic.students'].sudo().search_count([('batch_id', '=', batch_obj.id)])
        batch_data = {'batch_name': batch_obj.name, 'batch_strength': batch_strength}
        batch_data['upaya_data'] = academic_data.get_upaya_data(self, batch_obj)
        batch_data['yes_plus_data'] = academic_data.get_yes_plus_data(self, batch_obj)
        batch_data['presentation_data'] = academic_data.get_presentation_data(self, batch_obj)
        batch_data['excel_data'] = academic_data.get_excel_data(self, batch_obj)
        batch_data['cip_data'] = academic_data.get_cip_data(self, batch_obj)
        batch_data['bb_data'] = academic_data.get_bb_data(self, batch_obj)
        batch_data['mock_interview_data'] = academic_data.get_mock_interview_data(self, batch_obj)
        batch_data['attendance_data'] = academic_data.get_attendance_data(self, batch_obj)
        batch_data['exam_data'] = academic_data.get_exam_data(self, batch_obj)
        batch_data['one_to_one_data'] = academic_data.get_one_to_one_data(self, batch_obj)
        batch_datas.append(batch_data)
    return batch_datas


def get_employee_sales_data(self, employee, start_date=False, end_date=False, crash=False):
    sales_data = {}
    sales_data['source_leads_data'] = self.env['sales.tracker'].sudo().retrieve_employee_all_source_wise_lead_data(
        str(employee.id), start_date, end_date)
    sales_data['overall_source_leads_data'] = {'total_leads_count': 0, 'total_converted_leads': 0,
                                               'total_conversion_rate': 0, 'total_hot_leads': 0, 'total_warm_leads': 0,
                                               'total_cold_leads': 0}
    for lead_source in sales_data['source_leads_data'].keys():
        sales_data['overall_source_leads_data']['total_leads_count'] += sales_data['source_leads_data'][lead_source][
            'leads_count']
        sales_data['overall_source_leads_data']['total_converted_leads'] += \
        sales_data['source_leads_data'][lead_source]['converted_lead_count']
        sales_data['overall_source_leads_data']['total_hot_leads'] += sales_data['source_leads_data'][lead_source][
            'hot_leads_count']
        sales_data['overall_source_leads_data']['total_warm_leads'] += sales_data['source_leads_data'][lead_source][
            'warm_leads_count']
        sales_data['overall_source_leads_data']['total_cold_leads'] += sales_data['source_leads_data'][lead_source][
            'cold_leads_count']

    if sales_data['overall_source_leads_data']['total_leads_count'] > 0:
        sales_data['overall_source_leads_data']['total_conversion_rate'] = round((sales_data[
                                                                                      'overall_source_leads_data'][
                                                                                      'total_converted_leads'] /
                                                                                  sales_data[
                                                                                      'overall_source_leads_data'][
                                                                                      'total_leads_count']) * 100, 2)

    sales_data['course_leads_data'] = self.env['sales.tracker'].sudo().retrieve_employee_all_course_wise_lead_data(
        str(employee.id), start_date, end_date, crash=crash)
    sales_data['overall_course_leads_data'] = {'total_leads_count': 0, 'total_converted_leads': 0,
                                               'total_conversion_rate': 0, 'total_course_revenue': 0}
    for course in sales_data['course_leads_data'].keys():
        sales_data['overall_course_leads_data']['total_leads_count'] += sales_data['course_leads_data'][course][
            'leads_count']
        sales_data['overall_course_leads_data']['total_converted_leads'] += sales_data['course_leads_data'][course][
            'converted_lead_count']
        sales_data['overall_course_leads_data']['total_course_revenue'] += sales_data['course_leads_data'][course][
            'course_revenue']
    if sales_data['overall_course_leads_data']['total_leads_count'] > 0:
        sales_data['overall_course_leads_data']['total_conversion_rate'] += round((sales_data[
                                                                                       'overall_course_leads_data'][
                                                                                       'total_converted_leads'] /
                                                                                   sales_data[
                                                                                       'overall_course_leads_data'][                                                                             'total_leads_count']) * 100, 2)
    return sales_data

def get_employee_marketing_data(self, employee, start_date=False, end_date=False):
    logger = logging.getLogger('Seminar Debug: ')
    marketing_data = {'seminar_data': {}}
    marketing_data['overall_leads_data'] = {'total_leads_count': 0, 'total_seminar_count': 0, 'total_webinar_count': 0,
                                            'total_converted_leads': 0, 'total_conversion_rate': 0}

    districts = dict(self.env['seminar.leads'].sudo().fields_get()['district']['selection'])
    logger.error(districts)

    for district in districts.keys():
        marketing_data['seminar_data'][districts[district]] = {}
        district_leads_data = self.env['marketing.tracker'].retrieve_employee_district_wise_lead_data(district,
                                                                                                      employee,
                                                                                                      start_date,
                                                                                                      end_date)
        marketing_data['seminar_data'][districts[district]]['leads_count'] = district_leads_data['leads_count']
        marketing_data['seminar_data'][districts[district]]['converted_leads_count'] = district_leads_data[
            'converted_leads_count']
        marketing_data['seminar_data'][districts[district]]['leads_conversion_rate'] = district_leads_data[
            'leads_conversion_rate']
        marketing_data['seminar_data'][districts[district]]['webinar_count'] = district_leads_data['webinar_count']
        marketing_data['seminar_data'][districts[district]]['seminar_count'] = district_leads_data['seminar_count']

    for district in districts.keys():
        marketing_data['overall_leads_data']['total_leads_count'] += \
        marketing_data['seminar_data'][districts[district]]['leads_count']
        marketing_data['overall_leads_data']['total_converted_leads'] += \
        marketing_data['seminar_data'][districts[district]]['converted_leads_count']
        marketing_data['overall_leads_data']['total_seminar_count'] += \
        marketing_data['seminar_data'][districts[district]]['seminar_count']
        marketing_data['overall_leads_data']['total_webinar_count'] += \
        marketing_data['seminar_data'][districts[district]]['webinar_count']

    if marketing_data['overall_leads_data']['total_leads_count'] > 0:
        marketing_data['overall_leads_data']['total_conversion_rate'] = round((marketing_data['overall_leads_data'][
                                                                                   'total_converted_leads'] /
                                                                               marketing_data['overall_leads_data'][
                                                                                   'total_leads_count']) * 100, 2)

    logger.error(marketing_data)
    return marketing_data


def get_marketing_report_data(self, employees, start_date=False, end_date=False):
    marketing_data = {}
    if start_date and end_date:
        start_date, end_date = actions_common.get_date_obj_from_string(start_date, end_date)
        marketing_data['start_date'] = start_date.strftime("%d / %m / %Y")
        marketing_data['end_date'] = end_date.strftime("%d / %m / %Y")
    marketing_data['seminar_leaderboard_data'] = get_seminar_leaderboard_data(self, employees, start_date, end_date)
    marketing_data['common_task_performances'] = get_common_performance_data(self, employees, start_date, end_date)

    return marketing_data


def get_crash_report_data(self, employees, start_date=False, end_date=False):
    crash_data = {}
    if start_date and end_date:
        start_date, end_date = actions_common.get_date_obj_from_string(start_date, end_date)
        crash_data['start_date'] = start_date.strftime("%d / %m / %Y")
        crash_data['end_date'] = end_date.strftime("%d / %m / %Y")
    # crash_data['seminar_leaderboard_data'] = get_seminar_leaderboard_data(self, employees, start_date, end_date)
    crash_data['common_task_performances'] = get_common_performance_data(self, employees, start_date, end_date)

    return crash_data


def get_seminar_leaderboard_data(self, employees, start_date=False, end_date=False):
    for employee in employees:
        self.env['marketing.tracker'].sudo().create_employee_seminar_leaderboard_data(employee, start_date, end_date)
    seminar_leaderboard_data = self.env['marketing.tracker'].sudo().get_seminar_leaderboard_data(employees)
    return seminar_leaderboard_data


def get_sales_report_data(self, employees, start_date=False, end_date=False):
    sales_data = {}
    sales_data['coursewise_sales_data'], sales_data['coursewise_total_sales_data'] = get_coursewise_sales_data(self,
                                                                                                               employees,
                                                                                                               start_date,
                                                                                                               end_date)
    if start_date and end_date:
        start_date, end_date = actions_common.get_date_obj_from_string(start_date, end_date)
        sales_data['start_date'] = start_date.strftime("%d / %m / %Y")
        sales_data['end_date'] = end_date.strftime("%d / %m / %Y")
    sales_data['leads_leaderboard_data'] = get_leads_leaderboard_data(self, employees, start_date, end_date)
    sales_data['course_names'] = self.env['logic.base.courses'].sudo().search(
        [('name', 'not in', ('Nill', "DON'T USE", 'Nil')), ('type', '!=', 'crash')]).mapped('name')

    sales_data['common_task_performances'] = get_common_performance_data(self, employees, start_date, end_date)
    return sales_data


def get_leads_leaderboard_data(self, employees, start_date=False, end_date=False):
    for employee in employees:
        self.env['sales.tracker'].sudo().create_employee_leads_leaderboard_data(employee, start_date, end_date)
    return self.env['sales.tracker'].sudo().get_leads_leaderboard_data(employees, start_date, end_date)


def get_coursewise_sales_data(self, employees, start_date=False, end_date=False, crash=False):
    coursewise_data = {}
    if not crash:
        courses = self.env['logic.base.courses'].sudo().search(
            [('name', 'not in', ('Nill', "DON'T USE", 'Nil')), ('type', '!=', 'crash')])
    else:
        courses = self.env['logic.base.courses'].sudo().search(
            [('name', 'not in', ('Nill', "DON'T USE", 'Nil')), ('type', '=', 'crash')])

    coursewise_total_data = {}
    for employee in employees:
        emp_id_name = employee.name
        course_leads_data = self.env['sales.tracker'].sudo().retrieve_employee_all_course_wise_lead_data(
            str(employee.id), start_date, end_date)
        total_revenue = 0
        for course in course_leads_data.keys():
            total_revenue += course_leads_data[course]['course_revenue']
        # course_leads_data['total_revenue'] = total_revenue
        coursewise_data[emp_id_name] = {'coursewise_data': course_leads_data, 'total_revenue': total_revenue}

    if start_date and end_date:
        start_date, end_date = actions_common.get_date_obj_from_string(start_date, end_date)

    overall_total_revenue = 0
    for course in courses:
        if not start_date or not end_date:
            admission_count = self.env['leads.logic'].sudo().search_count(
                [('leads_assign', 'in', employees.ids), ('base_course_id', '=', course.id),
                 ('admission_status', '=', True), ('admission_date', '!=', False)])
        else:
            admission_count = self.env['leads.logic'].sudo().search_count(
                [('leads_assign', 'in', employees.ids), ('admission_date', '>=', start_date),
                 ('admission_date', '<=', end_date), ('base_course_id', '=', course.id),
                 ('admission_status', '=', True)])
        coursewise_total_data[course.name] = course.course_fee * admission_count
        overall_total_revenue += coursewise_total_data[course.name]
    coursewise_total_data['total_revenue'] = overall_total_revenue
    return coursewise_data, coursewise_total_data


def get_academic_report_data(self, manager_id, start_date=False, end_date=False):
    academic_data = False
    if manager_id:
        academic_data = self.env['academic.tracker'].retrieve_dashboard_data(start_date, end_date,
                                                                             manager_id=int(manager_id))
    if start_date and end_date:
        start_date, end_date = actions_common.get_date_obj_from_string(start_date, end_date)
        academic_data['start_date'] = start_date.strftime("%d / %m / %Y")
        academic_data['end_date'] = end_date.strftime("%d / %m / %Y")
    return academic_data


def get_common_performance_data(self, employees, start_date=False, end_date=False):
    for employee in employees:
        self.env['logic.common.task.performance'].sudo().create_employee_common_task_performance(employee, start_date,                                                                                       end_date)
    return self.env['logic.common.task.performance'].sudo().get_employee_common_task_performances(employees)
