from odoo import models,fields,api
from . import actions_common
class AcademicTracker(models.Model):
    _name = "academic.tracker"
    
    @api.model
    def retrieve_dashboard_data(self,start_date=False,end_date=False):

        if not start_date or not end_date:
            upaya_count = self.env['upaya.form'].sudo().search_count([])
            yes_plus_count = self.env['yes_plus.logic'].sudo().search_count([])
            sfc_count = self.env['student.faculty'].sudo().search_count([])
            exam_count = self.env['exam.details'].sudo().search_count([])
        else:
            start_date,end_date = actions_common.get_date_obj_from_string(start_date,end_date)

            upaya_count = self.env['upaya.form'].sudo().search_count([('date','>=',start_date),('date','<=',end_date)])
            yes_plus_count = self.env['yes_plus.logic'].sudo().search_count([('date_one','>=',start_date),('date_one','<=',end_date)])
            sfc_count = self.env['student.faculty'].sudo().search_count([('date','>=',start_date),('date','<=',end_date)])
            exam_count = self.env['exam.details'].sudo().search_count([('date','>=',start_date),('date','<=',end_date)])


        dashboard_data = {'upaya_count':upaya_count, 'yes_plus_count':yes_plus_count, 'sfc_count': sfc_count, 'exam_count':exam_count}
        return dashboard_data