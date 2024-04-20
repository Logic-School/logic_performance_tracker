from odoo import models,api,fields
from . import actions_common
import logging
import random
from datetime import date
from . import pdf_reports

class SalesTracker(models.Model):
    _name = "sales.tracker"

    @api.model
    def retrieve_dashboard_data(self,start_date=False,end_date=False,manager_id=False):
        rgba_colors = ['rgba(178, 56, 154, 0.75)', 'rgba(57, 141, 244, 0.52)', 'rgba(61, 14, 226, 0.88)', 'rgba(154, 29, 178, 0.51)', 'rgba(126, 101, 181, 0.05)', 'rgba(21, 80, 20, 0.70)', 'rgba(130, 79, 252, 0.09)', 'rgba(161, 125, 151, 0.61)', 'rgba(126, 124, 212, 0.81)', 'rgba(158, 94, 192, 0.75)', 'rgba(5, 19, 109, 0.87)', 'rgba(91, 247, 56, 0.89)', 'rgba(158, 182, 64, 0.12)', 'rgba(188, 190, 44, 0.53)', 'rgba(127, 164, 35, 0.92)', 'rgba(166, 173, 138, 0.32)', 'rgba(183, 241, 33, 0.89)', 'rgba(228, 183, 46, 0.94)', 'rgba(141, 226, 67, 0.39)', 'rgba(134, 126, 5, 0.13)', 'rgba(32, 190, 250, 0.85)', 'rgba(161, 59, 186, 0.20)', 'rgba(44, 217, 96, 0.68)', 'rgba(214, 67, 23, 0.77)', 'rgba(182, 127, 43, 0.94)', 'rgba(189, 3, 175, 0.71)', 'rgba(169, 148, 168, 0.69)', 'rgba(207, 205, 71, 0.74)', 'rgba(51, 140, 78, 0.42)', 'rgba(5, 246, 98, 0.81)', 'rgba(86, 128, 43, 0.90)', 'rgba(175, 77, 156, 0.63)', 'rgba(171, 104, 178, 0.31)', 'rgba(217, 229, 63, 0.47)', 'rgba(153, 138, 39, 0.09)', 'rgba(48, 141, 171, 0.01)', 'rgba(112, 207, 164, 0.50)', 'rgba(179, 184, 214, 0.61)', 'rgba(241, 14, 96, 0.44)', 'rgba(227, 53, 23, 0.54)', 'rgba(218, 215, 218, 0.87)', 'rgba(171, 194, 173, 0.57)', 'rgba(195, 154, 186, 0.04)', 'rgba(127, 118, 87, 0.01)', 'rgba(52, 222, 91, 0.32)', 'rgba(140, 238, 113, 0.55)', 'rgba(182, 249, 246, 0.76)', 'rgba(148, 12, 56, 0.61)', 'rgba(239, 154, 91, 0.33)', 'rgba(69, 251, 118, 0.25)']
        logger = logging.getLogger("Debugger: ")
        if start_date and end_date:
            start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)
            month = start_date.month
            year=start_date.year
        else:
            year = date.today().year
            month = date.today().month
        dashboard_data = {}
        department_obj = self.env['hr.department'].sudo().search([('name','=','Sales')])
        manager,managers,department_heads_data = actions_common.get_manager_managers_heads_data(self,department_obj,manager_id)
        dashboard_data['department_heads'] = department_heads_data
        if manager or managers:
            employees = actions_common.get_employees(self,department_obj,manager,managers)
            employee_ids = employees.ids

        dashboard_data['qualitatives'] = actions_common.get_raw_qualitative_data(self,employees,start_date,end_date)
        dashboard_data['quantitatives'] = actions_common.get_raw_quantitative_data(self,employees,start_date,end_date)

        lead_sources = self.env['leads.sources'].sudo().search([])
        lead_source_names = lead_sources.mapped('name')
        logger.error("lead_sources: "+str(lead_source_names))

        dashboard_data['leads_data'] = {'lead_sources':lead_source_names,'leads_dataset':[]}
        for employee in employees:
            actions_common.create_employee_qualitative_performance(self,dashboard_data['qualitatives'],employee)
            actions_common.create_employee_quantitative_performance(self,dashboard_data['quantitatives'],employee)

            self.create_employee_leads_leaderboard_data(employee,start_date,end_date)
            self.env['logic.common.task.performance'].sudo().create_employee_common_task_performance(employee,start_date,end_date)

            leads_count = []
            conversion_rates = []
            leads_data = {
                'label': employee.name,
                'backgroundColor': rgba_colors.pop(random.randint(0,20)),
                'borderColor': 'rgba(27, 92, 196, 0.95)',
                'borderWidth': 1,
                'data': []
            }            
            for lead_source in lead_sources:
                source_leads_data = self.env['sales.tracker'].retrieve_employee_source_wise_lead_data(lead_source,employee,start_date,end_date)
                leads_count.append(source_leads_data['leads_count'])
                conversion_rates.append(source_leads_data['leads_conversion_rate'])
            leads_data['data'] = leads_count
            dashboard_data['leads_data']['leads_dataset'].append(leads_data)

        dashboard_data['employee_ids'] = employee_ids
        dashboard_data['lead_sources'] = self.get_lead_sources_data()
        dashboard_data['org_datas'],dashboard_data['dept_names'] = actions_common.get_org_datas_dept_names(manager,managers)
        dashboard_data['leads_performances'] = self.get_leads_leaderboard_data(employees)
        dashboard_data['qualitatives'],dashboard_data['qualitative_overall_averages'] = actions_common.get_ordered_qualitative_data(self,dashboard_data['qualitatives'],employees)
        dashboard_data['quantitatives'],dashboard_data['quantitative_overall_averages'] = actions_common.get_ordered_quantitative_data(self,dashboard_data['quantitatives'],employees)

        dashboard_data['other_performances'] = actions_common.get_miscellaneous_performances(self,employees,start_date,end_date)
        dashboard_data['month'] = actions_common.get_month_list().get(month).capitalize()
        dashboard_data['common_task_performances'] = self.env['logic.common.task.performance'].sudo().get_employee_common_task_performances(employees)

        if start_date and end_date:
            if start_date.month != end_date.month:
                dashboard_data['month'] = False
        dashboard_data['year'] = year

        return dashboard_data
    
    def get_lead_sources_data(self):
        lead_sources_data = []
        lead_sources = self.env['leads.sources'].sudo().search([])
        for lead_source in lead_sources:
            lead_source_data = {}
            lead_source_data['id'] = lead_source.id
            lead_source_data['name'] = lead_source.name
            lead_sources_data.append(lead_source_data)
        return lead_sources_data
    
    @api.model
    def get_sourcewise_charts_data(self,lead_source_id,employee_ids,start_date=False,end_date=False):
        logger = logging.getLogger("Debugger: ")
        logger.error("employee_ids: "+str(employee_ids))
        logger.error("lead_source_id: "+str(lead_source_id))

        lead_domain = [('leads_source','=',int(lead_source_id)), ('course_type','!=','crash'),('leads_assign','in',employee_ids)]
        
        # month,year = self.get_leads_month_year(start_date,end_date)
        leads = self.env['leads.logic'].sudo().search(lead_domain)

        if start_date and end_date:
            start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)

        leads_with_admission,leads_without_admission = self.get_leads_with_and_without_admission(leads,start_date,end_date)
        leads = leads_with_admission + leads_without_admission
        # employees = self.env['hr.employee'].sudo().search[('id','in',employee_ids)]
        def get_pie_chart_data(leads):
            employees_data = {}

            for lead in leads:
                # if lead_with_out_admission.admission_date>=start_date and lead_with_out_admission.admission_date<=end_date:
                if employees_data.get(lead.leads_assign.name):
                    employees_data[lead.leads_assign.name]+=1
                else:
                    employees_data[lead.leads_assign.name] = 1
            
            logger.error("employees_data: "+str(employees_data))
            leads_data = []
            for key in employees_data.keys():
                leads_data.append({'label':key,'value':employees_data[key]})
            return leads_data
        pie_chart_data = get_pie_chart_data(leads)

        def get_stacked_chart_data(lead_source_id,employee_ids,start_date,end_date):
            employees = self.env['hr.employee'].sudo().search([('id','in',employee_ids)])
            employee_name_labels = employees.mapped('name')
            employee_leads_data = {'employee_names':employee_name_labels, 'leads_dataset': [] }
            leads_count_data = {
                'type':'bar',
                'label': 'Leads Count',
                'barPercentage': 0.3,

                # 'yAxisID': 'leads_count',
                'fill': True,
                'backgroundColor': 'rgba(32, 187, 72, 0.8)',
                'borderColor': 'rgba(49, 150, 76, 0.68)',
                'borderWidth': 1,
                'data': []
            }  
            leads_converted_data = {
                'type':'bar',
                'label': 'Converted Leads',
                'barPercentage': 0.3,

                # 'yAxisID': 'converted_leads_count',
                'fill': True,
                'backgroundColor': 'rgba(249, 83, 0, 0.83)',
                'borderColor': 'rgba(249, 83, 0, 0.83)',
                'borderWidth': 1,
                'data': []
            }  
            leads_count = []
            converted_leads_count = []
            lead_source = self.env['leads.sources'].sudo().search([('id','=',int(lead_source_id))])
            for employee in employees:
                source_leads_data = self.env['sales.tracker'].retrieve_employee_source_wise_lead_data(lead_source,employee,start_date,end_date)
                leads_count.append(source_leads_data['leads_count'])
                converted_leads_count.append(source_leads_data['converted_lead_count'])
            leads_count_data['data'] = leads_count
            leads_converted_data['data'] = converted_leads_count
            employee_leads_data['leads_dataset'].append(leads_count_data)
            employee_leads_data['leads_dataset'].append(leads_converted_data)
            return employee_leads_data
        stacked_chart_data = get_stacked_chart_data(lead_source_id,employee_ids,start_date,end_date)
        return {'pie_chart_data':pie_chart_data,'stacked_chart_data':stacked_chart_data}

    @api.model
    def retrieve_employee_all_source_wise_lead_data(self,employee_id,start_date=False,end_date=False):
        if start_date and end_date:
            start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)
        employee = self.env['hr.employee'].sudo().browse(int(employee_id.strip()))
        lead_sources = self.env['leads.sources'].sudo().search([])
        employee_data = {}
        for lead_source in lead_sources:
            employee_data[lead_source.name] = self.retrieve_employee_source_wise_lead_data(lead_source,employee,start_date,end_date)
        return employee_data

    
    def retrieve_employee_source_wise_lead_data(self,lead_source,employee,start_date=False,end_date=False):
        logger = logging.getLogger("Debugger: ")
        month_dict = actions_common.get_month_list()

        leads_count = 0
        lead_conversion_rate = 0
        converted_lead_count = 0
        hot_lead_count = 0
        warm_lead_count = 0
        cold_lead_count = 0

        lead_domain = [('leads_source','=',lead_source.id), ('course_type','!=','crash'),('leads_assign','=',employee.id)]

        leads = self.env['leads.logic'].sudo().search(lead_domain)

        month,year = self.get_leads_month_year(start_date,end_date)
        
        leads_with_admission,leads_without_admission = self.get_leads_with_and_without_admission(leads,start_date,end_date)
        year_lead_target_obj = self.env['leads.target'].sudo().search([('year','=',year),('user_id','=',employee.user_id.id)])
        month_year_lead_target = 0
        if year_lead_target_obj:
            if month:
                month_lead_obj = year_lead_target_obj.month_ids.filtered(lambda month_obj: month_obj.month==month_dict[month])
                month_year_lead_target = month_lead_obj[0].target
                # leads = leads.filtered(lambda lead: lead.date_of_adding.year==year and lead.date_of_adding.month==month)
        
        # leads_count+=len(leads_without_admission)

        for lead_without_admission in leads_without_admission:
            leads_count+=1
            if lead_without_admission.lead_quality=='hot':
                hot_lead_count+=1
            elif lead_without_admission.lead_quality == 'warm':
                warm_lead_count += 1
            elif lead_without_admission.lead_quality == 'cold':
                cold_lead_count += 1

        for lead_with_admission in leads_with_admission:
            leads_count += 1
            if lead_with_admission.lead_quality == 'hot':
                hot_lead_count += 1
            elif lead_with_admission.lead_quality == 'warm':
                warm_lead_count += 1
            elif lead_with_admission.lead_quality == 'cold':
                cold_lead_count += 1

        for lead_conversion in leads_with_admission:
            converted_lead_count += lead_conversion.admission_count
            # if month:
            #     print(lead_conversion.admission_date, 'datessss')
            #     print(lead_conversion.admission_count, 'countssss')
            # else:
            #     print('no')
            # leads = self.env['leads.logic'].sudo().search(lead_domain)
            # for i in leads:
            #     # converted_lead_count += i.admission_count
            #     if month:
            #         if lead_conversion.admission_date.month == month and lead_conversion.admission_date.year == year:
            #             converted_lead_count += i.admission_count
            #     else:
            #         converted_lead_count += i.admission_count

        if leads_count>0:
            lead_conversion_rate = round(100 * (converted_lead_count/leads_count),2)
            # lead_conversion_rate = 100 * round(converted_lead_count/leads_count,3)
        return {'leads_count':leads_count, 'leads_conversion_rate': lead_conversion_rate, 'converted_lead_count': converted_lead_count, 'hot_leads_count':hot_lead_count, 'warm_leads_count':warm_lead_count, 'cold_leads_count':cold_lead_count}
    
    def retrieve_employee_all_course_wise_lead_data(self,employee_id,start_date=False,end_date=False,crash=False):
        if start_date and end_date:
            start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)
        employee = self.env['hr.employee'].sudo().browse(int(employee_id.strip()))
        if not crash:
            courses = self.env['logic.base.courses'].sudo().search([('name','not in',('Nill',"DON'T USE",'Nil')), ('type','!=','crash')])
        else:
            courses = self.env['logic.base.courses'].sudo().search([('name','not in',('Nill',"DON'T USE",'Nil')), ('type','=','crash')])

        employee_data = {}
        for course in courses:
            employee_data[course.name] = self.retrieve_employee_course_wise_lead_data(course,employee,start_date,end_date)
        return employee_data

    def retrieve_employee_course_wise_lead_data(self,course,employee,start_date=False,end_date=False):
        logger = logging.getLogger("Debugger: ")
        month_dict = actions_common.get_month_list()
        leads_count = 0
        lead_conversion_rate = 0
        converted_lead_count = 0
        hot_lead_count = 0
        warm_lead_count = 0
        cold_lead_count = 0
        lead_domain = [('base_course_id','!=',False),('course_type','!=','crash'),('base_course_id','=',course.id),('leads_assign','=',employee.id)]
        leads = self.env['leads.logic'].sudo().search(lead_domain)
        month,year = self.get_leads_month_year(start_date,end_date)
        
        leads_with_admission,leads_without_admission = self.get_leads_with_and_without_admission(leads,start_date,end_date)
        year_lead_target_obj = self.env['leads.target'].sudo().search([('year','=',year),('user_id','=',employee.user_id.id)])
        month_year_lead_target = 0
        if year_lead_target_obj:
            if month:
                month_lead_obj = year_lead_target_obj.month_ids.filtered(lambda month_obj: month_obj.month==month_dict[month])
                month_year_lead_target = month_lead_obj[0].target
                # leads = leads.filtered(lambda lead: lead.date_of_adding.year==year and lead.date_of_adding.month==month)
        for lead_without_admission in leads_without_admission:
            leads_count+=1
            if lead_without_admission.lead_quality=='hot':
                hot_lead_count+=1
            elif lead_without_admission.lead_quality=='warm':
                warm_lead_count+=1
            elif lead_without_admission.lead_quality=='cold':
                cold_lead_count+=1

        for lead_with_admission in leads_with_admission:
            leads_count+=1
            if lead_with_admission.lead_quality=='hot':
                hot_lead_count+=1
            elif lead_with_admission.lead_quality=='warm':
                warm_lead_count+=1
            elif lead_with_admission.lead_quality=='cold':
                cold_lead_count+=1

        for lead_conversion in leads_with_admission:
            converted_lead_count += lead_conversion.admission_count

            # leads = self.env['leads.logic'].sudo().search(lead_domain)
            # for i in leads:
            #     converted_lead_count += i.admission_count
                # if month:
                #     if lead_with_admission.admission_date.month == month and lead_with_admission.admission_date.year == year:
                #         converted_lead_count += i.admission_count
                #         print(i.admission_count, 'admission count')
                # else:
                #     converted_lead_count += i.admission_count
                #     print(i.admission_count, 'admission count')

        if leads_count>0:
            lead_conversion_rate = round(100 * (converted_lead_count/leads_count),2)
            # lead_conversion_rate = 100 * round(converted_lead_count/leads_count,3)

        course_revenue = course.course_fee * converted_lead_count
        return {'course_revenue': course_revenue,'leads_count':leads_count, 'leads_conversion_rate': lead_conversion_rate, 'converted_lead_count': converted_lead_count, 'course_revenue': course_revenue}
    

    def retrieve_leads_target_count(self,employee,start_date=False,end_date=False):
        month_dict = actions_common.get_month_list()
        month=False
        month_year_lead_target = 0
        leads_count = 0
        converted_leads_count = 0
        if start_date and end_date:
            year=start_date.year
            if start_date.month==end_date.month:
                month=start_date.month

        else:
            year = date.today().year
            month = date.today().month
        
        leads = self.env['leads.logic'].sudo().search([('leads_assign','=',employee.id),('course_type','!=','crash'),('admission_status','=',True),('admission_date','!=',False)])

        year_lead_target_obj = self.env['leads.target'].sudo().search([('year','=',year),('user_id','=',employee.user_id.id)])
        if year_lead_target_obj:

            if month:
                month_lead_obj = year_lead_target_obj.month_ids.filtered(lambda month_obj: month_obj.month==month_dict[month])
                month_year_lead_target = month_lead_obj[0].target
                leads = leads.filtered(lambda lead: lead.admission_date.year==year and lead.admission_date.month==month)
            for lead in leads:
                converted_leads_count+=1
        return {'month_year_leads_target': month_year_lead_target, 'month_year_leads_count': leads_count,'month_year_converted_leads_count':converted_leads_count}

    #leads count in model card inside employee performance
    def get_employee_lead_count(self,employee,start_date,end_date):
        lead_domain = [('leads_assign','=',employee.id)]
        leads = self.env['leads.logic'].sudo().search(lead_domain)
        leads_with_admission,leads_without_admission = self.get_leads_with_and_without_admission(leads,start_date,end_date)
        lead_count = len(leads_with_admission) + len(leads_without_admission)
        return lead_count
    
    def create_employee_leads_leaderboard_data(self,employee,start_date=False,end_date=False):
        logger = logging.getLogger("Lead Debug: ")
        month_dict = actions_common.get_month_list()
        lead_domain = [('leads_assign','=',employee.id)]
        adm_total_leads_domain = [('leads_assign','=',employee.id), ('admission_status','=',True)]
        leads = self.env['leads.logic'].sudo().search(lead_domain)
        total_leads = len(leads)
        adm_leads = self.env['leads.logic'].sudo().search(adm_total_leads_domain)
        total_adm_count = len(adm_leads)

        leads_with_admission,leads_without_admission = self.get_leads_with_and_without_admission(leads,start_date,end_date)
        month,year = self.get_leads_month_year(start_date,end_date)
        year_lead_target_obj = self.env['leads.target'].sudo().search([('year','=',year),('user_id','=',employee.user_id.id)])
        month_year_lead_target = 0
        if year_lead_target_obj:
            if month:
                month_lead_obj = year_lead_target_obj.month_ids.filtered(lambda month_obj: month_obj.month==month_dict[month])
                month_year_lead_target = month_lead_obj[0].target

        converted_lead_count = 0
        lead_conversion_rate = 0
        leads_count = 0
        hot_lead_count = 0
        warm_lead_count = 0
        cold_lead_count = 0
        total_lead_count = 0

        for lead_without_admission in leads_without_admission:
            if lead_without_admission.course_type != 'crash':
                leads_count+=1
                if lead_without_admission.lead_quality=='hot':
                    hot_lead_count+=1
                elif lead_without_admission.lead_quality=='warm':
                    warm_lead_count+=1
                elif lead_without_admission.lead_quality=='cold':
                    cold_lead_count+=1

        for lead_with_admission in leads_with_admission:
            if lead_with_admission.course_type != 'crash':
                leads_count+=1
                if lead_with_admission.lead_quality=='hot':
                    hot_lead_count+=1
                elif lead_with_admission.lead_quality=='warm':
                    warm_lead_count+=1
                elif lead_with_admission.lead_quality=='cold':
                    cold_lead_count+=1

                if month:
                    if lead_with_admission.admission_date.month == month and lead_with_admission.admission_date.year==year:
                        converted_lead_count += lead_with_admission.admission_count
                        print('adm count',lead_with_admission.name, employee.name)
                else:
                    converted_lead_count += lead_with_admission.admission_count
                    print('adm count', lead_with_admission.name, employee.name)

        if leads_count>0:
            lead_conversion_rate = 100 * round(converted_lead_count/leads_count,3)

        converted_target_ratio = 0
        if month_year_lead_target>0:
            converted_target_ratio = round(converted_lead_count/month_year_lead_target,3)

        values = {
            'employee': employee.id,
            'lead_count': leads_count,
            'total_lead_count': total_leads,
            'total_adm_count': total_adm_count,
            'conversion_rate': lead_conversion_rate,
            'lead_converted': converted_lead_count,
            'lead_target': month_year_lead_target,
            'converted_target_ratio': converted_target_ratio,
        }
        emp_sales_perf_obj = self.env['logic.employee.sales.performance'].sudo().search([('employee','=',employee.id)])
        if emp_sales_perf_obj:
            emp_sales_perf_obj.write(values)
        else:
            self.env['logic.employee.sales.performance'].sudo().create(values)

    def get_leads_month_year(self,start_date,end_date):
        month=False

        if start_date and end_date:
            # lead_domain.extend([('date_of_adding','>=',start_date),('date_of_adding','<=',end_date)])
            year=start_date.year
            if start_date.month==end_date.month and start_date.year==end_date.year:
                month = start_date.month
        else:
            year = date.today().year
            month = date.today().month
        return month,year

    def get_leads_with_and_without_admission(self,leads,start_date,end_date):
        
        month,year = self.get_leads_month_year(start_date,end_date)
        leads_with_admission = leads.filtered(lambda lead: lead.admission_status==True and lead.admission_date)
        leads_without_admission = leads.filtered(lambda lead: lead.admission_status==False)

        if start_date and end_date:
            leads_with_admission = leads_with_admission.filtered(lambda lead: lead.admission_date>=start_date and lead.admission_date<=end_date)
            leads_without_admission = leads_without_admission.filtered(lambda lead: lead.date_of_adding>=start_date and lead.date_of_adding<=end_date)
        else:
            leads_with_admission = leads_with_admission.filtered(lambda lead: lead.admission_date.month==month and lead.admission_date.year==year)
            leads_without_admission = leads_without_admission.filtered(lambda lead: lead.date_of_adding.month==month and lead.date_of_adding.year==year)

        return leads_with_admission,leads_without_admission


    def get_leads_leaderboard_data(self,employees):
        sales_perf_objs = self.env['logic.employee.sales.performance'].sudo().search([('employee','in',employees.ids)])
        employees_data = {}
        for perf_obj in sales_perf_objs:
            emp_id = str(perf_obj.employee.id) + " "
            employees_data[emp_id] = {}
            employees_data[emp_id]['name'] = perf_obj.employee.name
            employees_data[emp_id]['total_lead_count'] = perf_obj.total_lead_count
            employees_data[emp_id]['total_adm_count'] = perf_obj.total_adm_count
            employees_data[emp_id]['lead_count'] = perf_obj.lead_count
            employees_data[emp_id]['conversion_rate'] = round(perf_obj.conversion_rate,2)
            employees_data[emp_id]['lead_target'] = perf_obj.lead_target
            employees_data[emp_id]['lead_converted'] = perf_obj.lead_converted
            employees_data[emp_id]['converted_target_ratio'] = perf_obj.converted_target_ratio

        return employees_data
    
    @api.model
    def get_sales_performance_report_data(self, start_date=False, end_date=False, manager_id=False):
        employees = self.env['hr.employee'].sudo().search([('parent_id','=',int(manager_id))])
        employees+= self.env['hr.employee'].sudo().browse(int(manager_id))
        employee_data = pdf_reports.get_sales_report_data(self,employees, start_date, end_date)
        return employee_data

class EmployeeSalesPerformance(models.Model):
    _name = "logic.employee.sales.performance"
    _order = "converted_target_ratio desc"

    employee = fields.Many2one("hr.employee",string="Employee")
    lead_count = fields.Integer(string="Lead Count")
    lead_target = fields.Integer(string="Lead Target")
    lead_converted = fields.Integer(string="Lead Achieved")
    converted_target_ratio = fields.Float(string="Lead Converted Target Ratio")
    conversion_rate = fields.Float(string="Conversion Rate")
    total_lead_count = fields.Float(string="Total Lead Count")
    total_adm_count = fields.Float(string="Total Adm Count")
