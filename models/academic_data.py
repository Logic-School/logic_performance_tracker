from odoo import models,api,fields
import random

def get_upaya_data(self,batch):
    upaya_data = {}
    batch_upaya_obj = self.env['upaya.form'].sudo().search([('batch_id','=',batch.id),('state','=','complete')])
    if batch_upaya_obj:
        upaya_data['is_conducted'] = True
        upaya_data['attended_count'] = len(batch_upaya_obj[0].upaya_attendance_ids.filtered(lambda attend: attend.attendance==True))
    else:
        upaya_data['is_conducted'] = False
        upaya_data['attended_count'] = 0
    return upaya_data

def get_yes_plus_data(self,batch):
    yes_plus_data = {}
    batch_yes_plus_obj = self.env['yes_plus.logic'].sudo().search([('batch_id','=',batch.id),('state','=','complete')])
    if batch_yes_plus_obj:
        yes_plus_data['is_conducted'] = True
        yes_plus_data['average_attendance'] = round(batch_yes_plus_obj[0].yes_avg_attendance,2)
    else:
        yes_plus_data['is_conducted'] = False
        yes_plus_data['average_attendance'] = 0
    return yes_plus_data



def get_presentation_data(self,batch):
    presentation_data = {'presented_count':0}
    batch_presentation_obj = self.env['logic.presentations'].sudo().search([('batch_id','=',batch.id)])
    if batch_presentation_obj:
        presentation_data['presented_count'] = len(batch_presentation_obj[0].student_presentations)
    return presentation_data

def get_excel_data(self,batch):
    excel_data = {'average_attendance':0}
    cip_excel_obj = self.env['logic.cip.form'].sudo().search([('batch_id','=',batch.id)])
    if cip_excel_obj:
        if cip_excel_obj[0].attendance_excel_ids:
            total_attendance = 0
            for excel_rec in cip_excel_obj[0].attendance_excel_ids:
                if cip_excel_obj[0].day_one_date:
                    if excel_rec.day_one_attendance=='full_day':
                        total_attendance+=1
                    elif excel_rec.day_one_attendance=="half_day":
                        total_attendance+=0.5
                if cip_excel_obj[0].day_two_date:
                    if excel_rec.day_two_attendance=='full_day':
                        total_attendance+=1
                    elif excel_rec.day_two_attendance=="half_day":
                        total_attendance+=0.5
                if cip_excel_obj[0].day_three_date:

                    if excel_rec.day_three_attendance=='full_day':
                        total_attendance+=1
                    elif excel_rec.day_three_attendance=="half_day":
                        total_attendance+=0.5
            if cip_excel_obj[0].day_one_date and cip_excel_obj[0].day_two_date and cip_excel_obj[0].day_three_date:
                average_attendance = total_attendance/3
            elif cip_excel_obj[0].day_one_date and cip_excel_obj[0].day_two_date:
                average_attendance = total_attendance/2
            else:
                average_attendance = total_attendance
        else:
            average_attendance = 0
        excel_data['average_attendance'] = round(average_attendance,2)
    return excel_data

def get_cip_data(self,batch):
    cip_data = {'average_attendance':0}
    cip_excel_obj = self.env['logic.cip.form'].sudo().search([('batch_id','=',batch.id)])
    if cip_excel_obj:
        if cip_excel_obj[0].cip_ids:
            total_attendance = 0
            for cip_rec in cip_excel_obj[0].cip_ids:
                if cip_excel_obj[0].cip_day_one:
                    if cip_rec.day_one_cip_attendance=='full_day':
                        total_attendance+=1
                    elif cip_rec.day_one_cip_attendance=="half_day":
                        total_attendance+=0.5
                if cip_excel_obj[0].cip_day_two:
                    if cip_rec.day_two_cip_attendance=='full_day':
                        total_attendance+=1
                    elif cip_rec.day_two_cip_attendance=="half_day":
                        total_attendance+=0.5
                if cip_excel_obj[0].cip_day_three:

                    if cip_rec.day_three_cip_attendance=='full_day':
                        total_attendance+=1
                    elif cip_rec.day_three_cip_attendance=="half_day":
                        total_attendance+=0.5

                    
                if cip_excel_obj[0].cip_day_four:

                    if cip_rec.day_four_cip_attendance=='full_day':
                        total_attendance+=1
                    elif cip_rec.day_four_cip_attendance=="half_day":
                        total_attendance+=0.5

            if cip_excel_obj[0].cip_day_one and cip_excel_obj[0].cip_day_two and cip_excel_obj[0].cip_day_three and cip_excel_obj[0].cip_day_four:
                average_attendance = total_attendance/4
            elif cip_excel_obj[0].cip_day_one and cip_excel_obj[0].cip_day_two and cip_excel_obj[0].cip_day_three:
                average_attendance = total_attendance/3
            elif cip_excel_obj[0].cip_day_one and cip_excel_obj[0].cip_day_two:
                average_attendance = total_attendance/2
            else:
                average_attendance = total_attendance
        else:
            average_attendance = 0
        cip_data['average_attendance'] = round(average_attendance,2)
    return cip_data

def get_bb_data(self,batch):
    bb_data = {'attendance':0}
    bb_obj = self.env['bring.your.buddy'].sudo().search([('batch_id','=',batch.id)])
    if bb_obj:
        bb_data['attendance'] = len(bb_obj[0].batch_students_ids.filtered(lambda stud: stud.day_attendance==True))
    return bb_data

def get_mock_interview_data(self,batch):
    mock_interview_data = {'total_conducted':0}
    batch_students = self.env['logic.students'].sudo().search([('batch_id','=',batch.id)])
    for student in batch_students:
        mock_interview_data['total_conducted']
        mock_interview_count = self.env['logic.mock_interview'].sudo().search_count([('student_name','=',student.id),('state','in',('confirmed','done'))])
        if mock_interview_count>0:
            mock_interview_data['total_conducted']+=1
    return mock_interview_data

def get_attendance_data(self,batch):
    attendance_data = {'average_attendance':0}
    batch_students = self.env['logic.students'].sudo().search([('batch_id','=',batch.id)])
    for student in batch_students:
        student_attendance_avg = 0
        attendance_count = 0
        attendance_recs = self.env['student.attendance'].sudo().search([('student_id','=',student.id)])
        if attendance_recs:
            for attendance_rec in attendance_recs:
                if attendance_rec.morning_attendance:
                    attendance_count+=0.5
                if attendance_rec.evening_attendance:
                    attendance_count+=0.5
            student_attendance_avg = round(attendance_count/len(attendance_recs),2)
        attendance_data['average_attendance']+=student_attendance_avg
    attendance_data['average_attendance'] = round(attendance_data['average_attendance'],2)
    return attendance_data


def get_exam_data(self,batch):
    rgba_colors = ['rgba(178, 56, 154, 0.75)', 'rgba(57, 141, 244, 0.52)', 'rgba(61, 14, 226, 0.88)', 'rgba(154, 29, 178, 0.51)', 'rgba(126, 101, 181, 0.05)', 'rgba(21, 80, 20, 0.70)', 'rgba(130, 79, 252, 0.09)', 'rgba(161, 125, 151, 0.61)', 'rgba(126, 124, 212, 0.81)', 'rgba(158, 94, 192, 0.75)', 'rgba(5, 19, 109, 0.87)', 'rgba(91, 247, 56, 0.89)', 'rgba(158, 182, 64, 0.12)', 'rgba(188, 190, 44, 0.53)', 'rgba(127, 164, 35, 0.92)', 'rgba(166, 173, 138, 0.32)', 'rgba(183, 241, 33, 0.89)', 'rgba(228, 183, 46, 0.94)', 'rgba(141, 226, 67, 0.39)', 'rgba(134, 126, 5, 0.13)', 'rgba(32, 190, 250, 0.85)', 'rgba(161, 59, 186, 0.20)', 'rgba(44, 217, 96, 0.68)', 'rgba(214, 67, 23, 0.77)', 'rgba(182, 127, 43, 0.94)', 'rgba(189, 3, 175, 0.71)', 'rgba(169, 148, 168, 0.69)', 'rgba(207, 205, 71, 0.74)', 'rgba(51, 140, 78, 0.42)', 'rgba(5, 246, 98, 0.81)', 'rgba(86, 128, 43, 0.90)', 'rgba(175, 77, 156, 0.63)', 'rgba(171, 104, 178, 0.31)', 'rgba(217, 229, 63, 0.47)']

    # exam_recs = self.env['exam.details'].sudo().search([('batch','=',batch.id),('exam_type','=','quarterly')])
    quart_percents = ['25','50','75','100']
    exam_data = {'exam_datasets':[]}
    exams = self.env['exam.details'].sudo().search([('batch', '=', batch.id)])
    for exam_rec in exams:
        if exam_rec:
            exam_dataset = {
                'type':'bar',
                'label': exam_rec.name,
                'fill': True,
                'barPercentage': 0.5,
                # 'barThickness': 60,
                # 'maxBarThickness': 80,
                'backgroundColor': rgba_colors.pop(random.randint(0,20)),
                'borderColor': rgba_colors.pop(random.randint(0,20)),
                'borderWidth': 1,
                'data': get_exam_pass_fail_percent(self,exam_rec)
            }
            exam_data['exam_datasets'].append(exam_dataset)
    return exam_data

def get_one_to_one_data(self,batch):
    attendance_data = {'total_conducted':0}
    batch_students = self.env['logic.students'].sudo().search([('batch_id','=',batch.id)])
    for student in batch_students:
        one_to_one_count = self.env['one_to_one.meeting'].sudo().search_count([('student_name','=',student.id)])
        if one_to_one_count>0:
            attendance_data['total_conducted']+=1
    return attendance_data

def get_exam_pass_fail_percent(self,exam_rec):
    pass_count = 0
    fail_count = 0
    for result in exam_rec.student_results:
        if result.present:
            if result.marks >= exam_rec.pass_mark:
                pass_count+=1
            else:
                fail_count+=1
        else:
            continue
    if exam_rec.present_students > 0:
        pass_percentage = round((pass_count/exam_rec.present_students)*100, 1)
        fail_percentage = round(100-exam_rec.pass_percentage,1)
    else:
        pass_percentage=0
        fail_percentage=0
    return [pass_percentage]