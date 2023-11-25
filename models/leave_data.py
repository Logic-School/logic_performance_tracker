from odoo import models, fields, api
import logging
from datetime import datetime,time, timedelta
def get_employee_leave_data(self,employee,start_date=False,end_date=False):
    logger = logging.getLogger("Leave debug: ")
    employee_data = {}
    leave_types = self.env['hr.leave.type'].sudo().search([])
    for leave_type in leave_types:
        employee_data[leave_type.name] = {'taken_leaves':0}
    leave_objs = self.env['hr.leave'].sudo().search([('state','=','validate'),('employee_id','=',employee.id)])
    if start_date or end_date:
        leave_objs.filtered(lambda leave: leave.date_from.date() >= start_date and leave.date_from.date() <= end_date)
    
    for leave in leave_objs:
        leave_days = leave.number_of_days
        if start_date and end_date:
            if leave.date_to.date() > end_date:
                logger.error("leave.date_to "+str(leave.date_to))
                date_from = datetime.combine(leave.date_from.date(), time.min, tzinfo=leave.date_to.tzinfo)
                end_date_datetime = datetime.combine(end_date, time.min, tzinfo=leave.date_to.tzinfo) + timedelta(days=1)
                logger.error("date_from "+str(date_from))
                logger.error("end_date_datetime "+str(end_date_datetime))
                
                domain = [('company_id', 'in', self.env.company.ids + self.env.context.get('allowed_company_ids', []))]
                logger.error("_get_leave_days_data_batch" + str(employee._get_leave_days_data_batch(date_from, end_date_datetime, domain=domain)))

                logger.error("_get_number_of_days: " + str(employee._get_leave_days_data_batch(date_from, end_date_datetime, domain=domain)[employee.id]['days']))
                leave_days = employee._get_leave_days_data_batch(date_from, end_date_datetime, domain=domain)[employee.id]['days']
        employee_data[leave.holiday_status_id.name]['taken_leaves'] += leave_days
    logger.error("Employee Leaves: "+str(employee_data))
    return employee_data
