from odoo import fields,models,api

class ViewInherit(models.Model):
    _inherit = 'ir.ui.view'
    type = fields.Selection(selection_add=[('dashboard_card', "Dashboard Cards")])

class ActWindowViewInherit(models.Model):
    _inherit = 'ir.actions.act_window.view'
    view_mode = fields.Selection(selection_add=[('dashboard_card', "Dashboard Cards")],ondelete={'dashboard_card': 'cascade'})