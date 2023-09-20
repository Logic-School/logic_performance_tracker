from odoo import models,fields,api
from odoo.exceptions import UserError
from datetime import date

def get_date_obj_from_string(from_date,end_date):
        from_date = from_date.split("-")
        from_date = date(year=int(from_date[0]),month=int(from_date[1]), day=int(from_date[2]))
        end_date = end_date.split("-")
        end_date = date(year=int(end_date[0]),month=int(end_date[1]), day=int(end_date[2]))
        return from_date,end_date

class StateAction(models.Model):
    _name = "performance.tracker"

    # @api.model
    def perf_tracker_open_action(self):
        if self.env.user.has_group('logic_performance_tracker.group_perf_admin') or self.env.user.has_group('logic_performance_tracker.group_perf_digital_head'):
            action = self.env.ref("logic_performance_tracker.digital_performance_action").sudo().read()[0]
            return action
        elif self.env.user.has_group('logic_performance_tracker.group_perf_admin') or self.env.user.has_group('logic_performance_tracker.group_perf_academic_head'):
            action = self.env.ref("logic_performance_tracker.academic_performance_action").sudo().read()[0]
            return action

        else:
            raise UserError("You do not have access to this application!")

    # @api.model
    # def action_open_view(self,model_name,state):
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': model_name,
    #         'view_mode': 'tree',
    #         'res_model': model_name,
    #         'domain': [('state','=',state)],
    #         'target': 'current',
    #     }
    
    # @api.model
    # def retrieve_dashboard_data(self,model_name):
    #     records = self.env[model_name].search([])
    #     dashboard_data = {}
    #     states = {}
    #     for record in records:
    #         try:
    #             states[record.state][1]+=1
    #         except:
    #             states[record.state] = [dict(record._fields['state'].selection).get(record.state),1]
    #     dashboard_data['states'] = states
    #     dashboard_data['performances'] = self.env['digital.executive.performance'].action_executive_performance()
    #     return dashboard_data