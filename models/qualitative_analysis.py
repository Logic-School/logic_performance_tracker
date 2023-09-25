from odoo import models, fields, api
from odoo.exceptions import UserError

class QualitativeInherit(models.Model):
    _inherit = "base.qualitative.analysis"

    @api.model
    def retrieve_performance(self, manager=False, start_date=False,end_date=False,managers=False):
        performances = {}
        if managers:
            # raise UserError(managers)
            child_ids = set()
            for manager_rec in managers:
                for id in manager_rec.child_ids.ids:
                    child_ids.add(id)
            child_ids = tuple(child_ids)
        elif manager:
            child_ids = manager.child_ids.ids

        if not start_date or not end_date:
            if manager or managers:
                records = self.env['base.qualitative.analysis'].sudo().search([('name','in',child_ids)])
            else:
                records = self.env['base.qualitative.analysis'].sudo().search([])
        else:
            if manager or managers:
                records = self.env['base.qualitative.analysis'].sudo().search([('name','in',child_ids),('added_date','>=',start_date),('added_date','<=',end_date)])
            else:
                records = self.env['base.qualitative.analysis'].sudo().search([('added_date','>=',start_date),('added_date','<=',end_date)])  
        employees = []
        # if managers:
        #     raise UserError(records)

        for record in records:
            # name field is employee m2o field
            employees.append(record.name.id)
        for employee_id in employees:
            if not start_date or not end_date:
                quality_records = self.env['base.qualitative.analysis'].sudo().search([('name','=',employee_id)])
            else:
                quality_records = self.env['base.qualitative.analysis'].sudo().search([('name','=',employee_id),('added_date','>=',start_date),('added_date','<=',end_date)])
            employee_attributes = {}
            for quality_rec in quality_records:
                for attributes in quality_rec.attribute_ids:
                    for attribute in attributes:
                        if not employee_attributes.get(attribute.attribute.attribute_type):
                            employee_attributes[attribute.attribute.attribute_type] = {}
                            employee_attributes[attribute.attribute.attribute_type]['rating'] = int(attribute.performance)
                            employee_attributes[attribute.attribute.attribute_type]['count'] = 1
                            employee_attributes[attribute.attribute.attribute_type]['average_rating'] = int(attribute.performance)


                        else:
                            employee_attributes[attribute.attribute.attribute_type]['rating'] += int(attribute.performance)
                            employee_attributes[attribute.attribute.attribute_type]['count'] += 1
                            employee_attributes[attribute.attribute.attribute_type]['average_rating'] = round(employee_attributes[attribute.attribute.attribute_type]['rating']/employee_attributes[attribute.attribute.attribute_type]['count'],2)

            employee_name = self.env['hr.employee'].browse(employee_id).name
            
            performances[employee_name] = employee_attributes
        return performances

    # @api.model
    # def retrieve_dashboard_data(self):
    #     performances = self.env['base.qualitative.analysis'].sudo().retrieve_performance(False)
    #     return performances