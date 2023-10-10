from odoo import fields,api,models
import logging

import sys

# Set the recursion limit to a higher value
sys.setrecursionlimit(3000)  # Set the desired limit

class HrEmployeeInherit(models.Model):
    _inherit = "hr.employee"
    in_charge_id = fields.Many2one("hr.employee",string="In Charge")
    is_in_charge = fields.Boolean(string="Is In charge")
    in_charge_child_ids = fields.One2many("hr.employee","in_charge_id",string="In Charge Childs")

    def get_organisation_data(self, employee):
        org_data = {'id': employee.id, 'name': employee.name, 'title': employee.job_title,'image':employee.image_1920, 'children': []}
        child_ids = employee.in_charge_child_ids if employee.in_charge_child_ids else employee.child_ids
        child_ids = []
        if employee.in_charge_child_ids:
            child_ids+=employee.in_charge_child_ids
        if employee.child_ids:
            child_ids+=employee.child_ids
        for subordinate in child_ids:
            org_data['children'].append(self.get_organisation_data(subordinate))

        return org_data
        # org_data = {}
        # logger = logging.getLogger("Debugger: ")
        # child_ids = False
        # if manager:
        #     already_added_ids = [manager.id]
        #     org_data['id'] = manager.id
        #     org_data['name'] = manager.name
        #     org_data['title'] = manager.job_title
        #     org_data['image'] = manager.image_1920
        #     org_data['children'] = []
        #     in_charges = self.env['hr.employee'].search([('in_charge_child_ids','!=',False),('parent_id','=',manager.id)])
        #     for in_charge in in_charges:
        #         already_added_ids.append(in_charge.id)
        #         in_charge_data = {}
        #         in_charge_data['id'] = in_charge.id
        #         in_charge_data['name'] = in_charge.name
        #         in_charge_data['title'] = in_charge.job_title
        #         in_charge_data['image'] = manager.image_1920

        #         in_charge_data['children'] = []
        #         if in_charge.in_charge_child_ids:
        #             child_ids = in_charge.in_charge_child_ids
        #         else:
        #             child_ids = in_charge.child_ids
        #         for sub_ord in child_ids:
        #             already_added_ids.append(sub_ord.id)
        #             sub_ord_data = {}
        #             sub_ord_data['id'] = sub_ord.id
        #             sub_ord_data['name'] = sub_ord.name
        #             sub_ord_data['title'] = sub_ord.job_title
        #             sub_ord_data['image'] = manager.image_1920

        #             in_charge_data['children'].append(sub_ord_data)
                    
        #         org_data['children'].append(in_charge_data)

        #     other_subords = self.env['hr.employee'].search([('in_charge_child_ids','=',False),('id','not in',already_added_ids),('parent_id','=',manager.id)])
        #     for sub_ord in other_subords:
        #         sub_ord_data = {}
        #         sub_ord_data['id'] = sub_ord.id
        #         sub_ord_data['name'] = sub_ord.name
        #         sub_ord_data['title'] = sub_ord.job_title
        #         sub_ord_data['image'] = manager.image_1920

        #         org_data['children'].append(sub_ord_data)

        #     logger.error("org_data: "+str(org_data))
                
        # return org_data


    # def get_organisation_data(self, employee):
    #     org_data = {'id': employee.id, 'name': employee.name, 'title': employee.job_title,'image':employee.image_1920, 'children': []}

    #     for subordinate in employee.child_ids:
    #         org_data['children'].append(self.get_organisation_data(subordinate))

    #     return org_data