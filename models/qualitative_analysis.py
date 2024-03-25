from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

class QualitativeEmployeeOverall(models.Model):
    _name = "employee.qualitative.performance"
    employee = fields.Many2one("hr.employee")
    overall_average = fields.Float()

class QualitativeInherit(models.Model):
    _inherit = "base.qualitative.analysis"

    @api.model
    def retrieve_performance(self, employees=False,start_date=False,end_date=False):
        # if managers:
        #     # raise UserError(managers)
        #     child_ids = set()
        #     for manager_rec in managers:
        #         for id in manager_rec.child_ids.ids:
        #             child_ids.add(id)
        #     child_ids = tuple(child_ids)
        # elif manager:
        #     child_ids = manager.child_ids.ids

        # if not start_date or not end_date:
        #     if manager or managers:
        #         records = self.env['base.qualitative.analysis'].sudo().search([('name','in',child_ids)])
        #     else:
        #         records = self.env['base.qualitative.analysis'].sudo().search([])
        # else:
        #     if manager or managers:
        #         records = self.env['base.qualitative.analysis'].sudo().search([('name','in',child_ids),('added_date','>=',start_date),('added_date','<=',end_date)])
        #     else:
        #         records = self.env['base.qualitative.analysis'].sudo().search([('added_date','>=',start_date),('added_date','<=',end_date)])  
        # employees = []
        # # if managers:
        # #     raise UserError(records)

        # for record in records:
        #     # name field is employee m2o field
        #     employees.append(record.name.id)
        performances = {}
        employees = employees.ids

        for employee_id in employees:
            if not start_date or not end_date:
                quality_records = self.env['base.qualitative.analysis'].sudo().search([('name','=',employee_id)])
            else:
                quality_records = self.env['base.qualitative.analysis'].sudo().search([('name','=',employee_id),('added_date','>=',start_date),('added_date','<=',end_date)])
            employee_attributes = {}
            for quality_rec in quality_records:
                for attributes in quality_rec.attribute_ids:
                    for attribute in attributes:
                        if not employee_attributes.get(attribute.attribute.id):
                            employee_attributes[attribute.attribute.id] = {}
                            employee_attributes[attribute.attribute.id]['attribute_type'] = attribute.attribute.attribute_type
                            employee_attributes[attribute.attribute.id]['rating'] = int(attribute.performance)
                            employee_attributes[attribute.attribute.id]['count'] = 1
                            employee_attributes[attribute.attribute.id]['average_rating'] = int(attribute.performance)

                        else:
                            employee_attributes[attribute.attribute.id]['rating'] += int(attribute.performance)
                            employee_attributes[attribute.attribute.id]['count'] += 1
                            employee_attributes[attribute.attribute.id]['average_rating'] = round(employee_attributes[attribute.attribute.id]['rating']/employee_attributes[attribute.attribute.id]['count'],2)
            employee_name = self.env['hr.employee'].browse(employee_id).name
            
            # employee_attributes['overall_average'] = 0
            # logger = logging.getLogger("Debugger: ") 
            # logger.error("emps attrs: "+str(employee_attributes))
            # for emp_attribute in list(employee_attributes.keys())[1:]:
            #     employee_attributes['overall_average'] += employee_attributes[emp_attribute]['average_rating']
            # employee_attributes['overall_average'] = round(employee_attributes['overall_average']/len(employee_attributes.keys()),2)
            performances[employee_name] = employee_attributes
        return performances

    # @api.model
    # def retrieve_dashboard_data(self):
    #     performances = self.env['base.qualitative.analysis'].sudo().retrieve_performance(False)
    #     return performances


class QuantitativeEmployeeOverall(models.Model):
    _name = "employee.quantitative.performance"
    employee = fields.Many2one("hr.employee")
    overall_average = fields.Float()


class QuantitativeInherit(models.Model):
    _inherit = "quantitative.analysis"

    @api.model
    def retrieve_performance(self, employees=False, start_date=False, end_date=False):
        # if managers:
        #     # raise UserError(managers)
        #     child_ids = set()
        #     for manager_rec in managers:
        #         for id in manager_rec.child_ids.ids:
        #             child_ids.add(id)
        #     child_ids = tuple(child_ids)
        # elif manager:
        #     child_ids = manager.child_ids.ids

        # if not start_date or not end_date:
        #     if manager or managers:
        #         records = self.env['base.qualitative.analysis'].sudo().search([('name','in',child_ids)])
        #     else:
        #         records = self.env['base.qualitative.analysis'].sudo().search([])
        # else:
        #     if manager or managers:
        #         records = self.env['base.qualitative.analysis'].sudo().search([('name','in',child_ids),('added_date','>=',start_date),('added_date','<=',end_date)])
        #     else:
        #         records = self.env['base.qualitative.analysis'].sudo().search([('added_date','>=',start_date),('added_date','<=',end_date)])
        # employees = []
        # # if managers:
        # #     raise UserError(records)

        # for record in records:
        #     # name field is employee m2o field
        #     employees.append(record.name.id)
        performances = {}
        employees = employees.ids

        for employee_id in employees:
            if not start_date or not end_date:
                quality_records = self.env['quantitative.analysis'].sudo().search([('employee_id', '=', employee_id)])
            else:
                quality_records = self.env['quantitative.analysis'].sudo().search(
                    [('employee_id', '=', employee_id), ('added_date', '>=', start_date), ('added_date', '<=', end_date)])
            employee_attributes = {}
            for quality_rec in quality_records:
                for attributes in quality_rec.attribute_ids:
                    for attribute in attributes:
                        if not employee_attributes.get(attribute.attribute.id):
                            employee_attributes[attribute.attribute.id] = {}
                            employee_attributes[attribute.attribute.id][
                                'attribute_type'] = attribute.attribute.attribute_type
                            employee_attributes[attribute.attribute.id]['rating'] = int(attribute.performance)
                            employee_attributes[attribute.attribute.id]['count'] = 1
                            employee_attributes[attribute.attribute.id]['average_rating'] = int(attribute.performance)

                        else:
                            employee_attributes[attribute.attribute.id]['rating'] += int(attribute.performance)
                            employee_attributes[attribute.attribute.id]['count'] += 1
                            employee_attributes[attribute.attribute.id]['average_rating'] = round(
                                employee_attributes[attribute.attribute.id]['rating'] /
                                employee_attributes[attribute.attribute.id]['count'], 2)
            employee_name = self.env['hr.employee'].browse(employee_id).name

            # employee_attributes['overall_average'] = 0
            # logger = logging.getLogger("Debugger: ")
            # logger.error("emps attrs: "+str(employee_attributes))
            # for emp_attribute in list(employee_attributes.keys())[1:]:
            #     employee_attributes['overall_average'] += employee_attributes[emp_attribute]['average_rating']
            # employee_attributes['overall_average'] = round(employee_attributes['overall_average']/len(employee_attributes.keys()),2)
            performances[employee_name] = employee_attributes
        return performances