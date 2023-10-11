from odoo import models,fields,api
from odoo.exceptions import UserError
from . import actions_common
import logging
class DigitalTaskInherit(models.Model):
    _inherit = "digital.task"

    def get_states_data(self,tasks):
        states = {'Sent to Approve':0,'Approved':0,'Assigned':0,'In Progress':0,'Completed':0,'To Post':0,'Posted':0}
        for task in tasks:
            try:
                states[dict(task._fields['state'].selection).get(task.state)]+=1
            except:
                pass
        states_data = []
        for key in states.keys():
            states_data.append({'label':key,'value':states[key]})
        return states_data
            # except:
            #     states[task.state] = [dict(task._fields['state'].selection).get(task.state),1]

    @api.model
    def retrieve_dashboard_data(self,start_date=False,end_date=False):
        logger = logging.getLogger("Debugger")
        tasks = self.env['digital.task'].sudo().search([])
        try:
            manager = self.env.ref('logic_digital_tracker.group_digital_head').users[0].employee_id
            employees = manager.child_ids
        except:
            manager = False
        dashboard_data = {}

        dashboard_data['states_data'] = self.get_states_data(tasks)
        
        if not start_date or not end_date:
            dashboard_data['qualitatives'] = self.env['base.qualitative.analysis'].retrieve_performance(manager=manager)
            dashboard_data['performances'] = self.env['digital.executive.performance'].action_executive_performance(dashboard_data['qualitatives'])
            dashboard_data['other_performances'] = self.env['logic.task.other'].retrieve_performance(manager)
        else:
            start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)
            dashboard_data['qualitatives'] = self.env['base.qualitative.analysis'].retrieve_performance(manager=manager,start_date=start_date,end_date=end_date)
            dashboard_data['performances'] = self.env['digital.executive.performance'].action_executive_performance(dashboard_data['qualitatives'],start_date,end_date)
            dashboard_data['other_performances'] = self.env['logic.task.other'].retrieve_performance(manager,start_date,end_date)

        for employee in employees:  

            qualitative_average = 0
            qualitative_values = {}
            if dashboard_data['qualitatives'].get(employee.name):
                for attribute in dashboard_data['qualitatives'][employee.name].keys():
                    qualitative_average += dashboard_data['qualitatives'][employee.name][attribute]['average_rating']
                    qualitative_values[attribute] = dashboard_data['qualitatives'][employee.name][attribute]['average_rating']
                qualitative_average = round(qualitative_average/len(dashboard_data['qualitatives'][employee.name].keys()), 2)
                logger.error("qual aver: "+str(qualitative_average))
            logger.error("qual values: "+str(qualitative_values))
            
            emp_qual_obj = self.env['employee.qualitative.performance'].search([('employee','=',employee.id)])
            if emp_qual_obj:
                emp_qual_obj.write({
                    'overall_average': qualitative_average
                })
            else:
                self.env['employee.qualitative.performance'].create({
                    'employee': employee.id,
                    'overall_average': qualitative_average,
                })
        
        qualitative_overall_objs = self.env['employee.qualitative.performance'].search([('employee','in',employees.ids)],order="overall_average desc")
        qualitative_overall_average_datas = {}
        for qualitative_overall_obj in qualitative_overall_objs:
            qualitative_overall_average_datas[qualitative_overall_obj.employee.name] = qualitative_overall_obj.overall_average
            if not dashboard_data['qualitatives'].get(qualitative_overall_obj.employee.name):
                dashboard_data['qualitatives'][qualitative_overall_obj.employee.name] = {}
        logger.error("qualitative_overall_average_datas: "+str(qualitative_overall_average_datas))
        logger.error("dashboard_data['qualitatives']: "+str(dashboard_data['qualitatives']))

        dashboard_data['qualitative_overall_averages'] = qualitative_overall_average_datas
        org_datas=[]
        if manager:
            org_datas = [manager.get_organisation_data(manager)]
        dashboard_data['org_datas'] = org_datas
        # raise UserError(dashboard_data)
        return dashboard_data
