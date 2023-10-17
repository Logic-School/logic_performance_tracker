from odoo import fields,api,models
import logging
from collections import deque

import sys

# Set the recursion limit to a higher value

def get_sorted_record_list(records):
    records_as_list = []
    for record in records:
         records_as_list.append(record)
    sorted_recs = []
    max_len = 0
    max_ind = 0
    while(len(records_as_list)!=0):
        i=0
        max_ind = 0
        for record in records_as_list:
            if len(record.in_charge_child_ids) > max_len:
                max_len = len(record.in_charge_child_ids)
                max_ind = i
            i+=1
        sorted_recs.append(records_as_list.pop(max_ind))

    return sorted_recs

class HrEmployeeInherit(models.Model):
    _inherit = "hr.employee"
    in_charge_id = fields.Many2one("hr.employee",string="In Charge")
    is_in_charge = fields.Boolean(string="Is In charge")
    in_charge_child_ids = fields.One2many("hr.employee","in_charge_id",string="In Charge Childs")



    def get_organisation_data(self,employee, processed_ids=None):
            if processed_ids is None:
                processed_ids = set()

            # Skip if the employee has already been processed
            if employee.id in processed_ids:
                return None

            # Add the current employee to the set of processed IDs
            processed_ids.add(employee.id)

            # Determine the set of children based on availability of in_charge_child_ids
            # children_ids = employee.in_charge_child_ids if employee.in_charge_child_ids else employee.child_ids
            in_charge_child_ids = self.env['hr.employee'].search([('in_charge_id','=',employee.id)],order="name asc")
            child_ids = self.env['hr.employee'].search([('parent_id','=',employee.id)],order="name asc")
            children_ids = in_charge_child_ids + child_ids
            children_ids = get_sorted_record_list(children_ids)

            # Build the hierarchy for the current employee
            org_data = {
                'id': employee.id,
                'name': employee.name,
                'title': employee.job_title,
                'image':employee.image_1920,
                'children': [],
            }

            # Recursively get hierarchy for children
            for child_id in children_ids:
                child_hierarchy = self.get_organisation_data(child_id, processed_ids)
                if child_hierarchy:
                    org_data['children'].append(child_hierarchy)

            return org_data





    # def get_organisation_data(self, employee):
    #     org_data = {'id': employee.id, 'name': employee.name, 'title': employee.job_title,'image':employee.image_1920, 'children': []}
        
    #     child_ids = False
    #     if not employee.in_charge_id:
    #         if not child_ids:
    #             child_ids = employee.filtered(lambda child: child.in_charge_ids!=False)
    #         else:
    #             child_ids|=

    #     if child_ids:

    #         # child_ids.filtered(lambda child: child.child_ids not in employee.parent_id.child_ids)
    #         for subordinate in child_ids:
    #             org_data['children'].append(self.get_organisation_data(subordinate))

    #     return org_data
        # org_data = {}
        # logger = logging.getLogger("Debugger: ")
        # child_ids = False
        # if employee:
        #     already_added_ids = [employee.id]
        #     org_data['id'] = employee.id
        #     org_data['name'] = employee.name
        #     org_data['title'] = employee.job_title
        #     org_data['image'] = employee.image_1920
        #     org_data['children'] = []
        #     in_charges = self.env['hr.employee'].search([('in_charge_child_ids','!=',False),('parent_id','=',employee.id)])
        #     for in_charge in in_charges:
        #         already_added_ids.append(in_charge.id)
        #         in_charge_data = {}
        #         in_charge_data['id'] = in_charge.id
        #         in_charge_data['name'] = in_charge.name
        #         in_charge_data['title'] = in_charge.job_title
        #         in_charge_data['image'] = in_charge.image_1920

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
        #             sub_ord_data['image'] = sub_ord.image_1920

        #             in_charge_data['children'].append(sub_ord_data)
                    
        #         org_data['children'].append(in_charge_data)

        #     other_subords = self.env['hr.employee'].search([('in_charge_child_ids','=',False),('id','not in',already_added_ids),('parent_id','=',employee.id)])
        #     for sub_ord in other_subords:
        #         sub_ord_data = {}
        #         sub_ord_data['id'] = sub_ord.id
        #         sub_ord_data['name'] = sub_ord.name
        #         sub_ord_data['title'] = sub_ord.job_title
        #         sub_ord_data['image'] = sub_ord.image_1920

        #         org_data['children'].append(sub_ord_data)

        #     logger.error("org_data: "+str(org_data))
                
        # return org_data


    # def get_organisation_data(self, employee):
    #     org_data = {'id': employee.id, 'name': employee.name, 'title': employee.job_title,'image':employee.image_1920, 'children': []}

    #     for subordinate in employee.child_ids:
    #         org_data['children'].append(self.get_organisation_data(subordinate))

    #     return org_data