from odoo import models,fields,api
import logging
from . import actions_common
import random


class MarketingTracker(models.Model):
    _name="marketing.tracker"

    @api.model
    def retrieve_dashboard_data(self,start_date=False,end_date=False,manager_id=False):
        rgba_colors = ['rgba(178, 56, 154, 0.75)', 'rgba(57, 141, 244, 0.52)', 'rgba(61, 14, 226, 0.88)', 'rgba(154, 29, 178, 0.51)', 'rgba(126, 101, 181, 0.05)', 'rgba(21, 80, 20, 0.70)', 'rgba(130, 79, 252, 0.09)', 'rgba(161, 125, 151, 0.61)', 'rgba(126, 124, 212, 0.81)', 'rgba(158, 94, 192, 0.75)', 'rgba(5, 19, 109, 0.87)', 'rgba(91, 247, 56, 0.89)', 'rgba(158, 182, 64, 0.12)', 'rgba(188, 190, 44, 0.53)', 'rgba(127, 164, 35, 0.92)', 'rgba(166, 173, 138, 0.32)', 'rgba(183, 241, 33, 0.89)', 'rgba(228, 183, 46, 0.94)', 'rgba(141, 226, 67, 0.39)', 'rgba(134, 126, 5, 0.13)', 'rgba(32, 190, 250, 0.85)', 'rgba(161, 59, 186, 0.20)', 'rgba(44, 217, 96, 0.68)', 'rgba(214, 67, 23, 0.77)', 'rgba(182, 127, 43, 0.94)', 'rgba(189, 3, 175, 0.71)', 'rgba(169, 148, 168, 0.69)', 'rgba(207, 205, 71, 0.74)', 'rgba(51, 140, 78, 0.42)', 'rgba(5, 246, 98, 0.81)', 'rgba(86, 128, 43, 0.90)', 'rgba(175, 77, 156, 0.63)', 'rgba(171, 104, 178, 0.31)', 'rgba(217, 229, 63, 0.47)', 'rgba(153, 138, 39, 0.09)', 'rgba(48, 141, 171, 0.01)', 'rgba(112, 207, 164, 0.50)', 'rgba(179, 184, 214, 0.61)', 'rgba(241, 14, 96, 0.44)', 'rgba(227, 53, 23, 0.54)', 'rgba(218, 215, 218, 0.87)', 'rgba(171, 194, 173, 0.57)', 'rgba(195, 154, 186, 0.04)', 'rgba(127, 118, 87, 0.01)', 'rgba(52, 222, 91, 0.32)', 'rgba(140, 238, 113, 0.55)', 'rgba(182, 249, 246, 0.76)', 'rgba(148, 12, 56, 0.61)', 'rgba(239, 154, 91, 0.33)', 'rgba(69, 251, 118, 0.25)']
        logger = logging.getLogger("Debugger: ")
        dashboard_data = {}
        department_obj = self.env['hr.department'].sudo().search([('name','=','Marketing')])
        manager,managers,department_heads_data = actions_common.get_manager_managers_heads_data(self,department_obj,manager_id)
        dashboard_data['department_heads'] = department_heads_data
        if manager or managers:
            employees = actions_common.get_employees(self,department_obj,manager,managers)
            employee_user_ids = employees.mapped('user_id.id')

        dashboard_data['qualitatives'] = actions_common.get_raw_qualitative_data(self,employees,start_date,end_date)

        districts = dict(self.env['seminar.leads'].fields_get()['district']['selection'])
        district_names = list(dict(self.env['seminar.leads'].fields_get()['district']['selection']).values())

        dashboard_data['leads_data'] = {'districts':district_names,'leads_dataset':[]}
        for employee in employees:
            actions_common.create_employee_qualitative_performance(self,dashboard_data['qualitatives'],employee)
            lead_counts = []
            leads_data = {
                'label': employee.name,
                'backgroundColor': rgba_colors.pop(random.randint(0,20)),
                'borderColor': 'rgba(27, 92, 196, 0.95)',
                'borderWidth': 1,
                'data': [0 for i in range(len(district_names))]
            }            
            for district in districts.keys():
                district_lead_count = self.retrieve_employee_district_wise_lead_count(district,employee,start_date,end_date)
                lead_counts.append(district_lead_count)
            leads_data['data'] = lead_counts
            dashboard_data['leads_data']['leads_dataset'].append(leads_data)

        dashboard_data['org_datas'],dashboard_data['dept_names'] = actions_common.get_org_datas_dept_names(manager,managers)

        dashboard_data['qualitatives'],dashboard_data['qualitative_overall_averages'] = actions_common.get_ordered_qualitative_data(self,dashboard_data['qualitatives'],employees)
        dashboard_data['other_performances'] = actions_common.get_miscellaneous_performances(self,employees,start_date,end_date)

        return dashboard_data

    def retrieve_employee_district_wise_lead_count(self,district,employee,start_date=False,end_date=False):

        logger = logging.getLogger("Debugger: ")
        lead_count = 0
        seminar_domain = [('district','=',district),('state','=','done'),('create_uid','=',employee.user_id.id)]
        if start_date and end_date:
            seminar_domain.extend([('seminar_date','>=',start_date),('seminar_date','<=',end_date)])
        seminars = self.env['seminar.leads'].sudo().search(seminar_domain)
        for seminar in seminars:
            lead_count+=len(seminar.seminar_ids)
        return lead_count
        # leads_data = {
        #     'label': 'Peters',
        #     'backgroundColor': rgba_colors.pop(random.randint(0,19)),
        #     'borderColor': 'rgba(27, 92, 196, 0.95)',
        #     'borderWidth': 1,
        #     'data': list(lead_counts.values())
        # }

