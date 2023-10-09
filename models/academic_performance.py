from odoo import fields,models,api

class AcademicCoordinatorPerformance(models.Model):
    _name="academic.coordinator.performance"
    _order="total_completed"
    employee = fields.Many2one("hr.employee",string="Employee")
    upaya_count = fields.Integer()
    yes_plus_count = fields.Integer()
    one2one_count = fields.Integer()
    sfc_count = fields.Integer()
    exam_count = fields.Integer()
    mock_interview_count = fields.Integer()
    cip_excel_count = fields.Integer()
    bring_buddy_count = fields.Integer()
    total_completed = fields.Integer()
    previous_total = fields.Integer()

