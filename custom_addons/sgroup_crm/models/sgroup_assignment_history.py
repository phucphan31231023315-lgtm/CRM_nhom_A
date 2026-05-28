# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SgroupAssignmentHistory(models.Model):
    _name = 'sgroup.assignment.history'
    _description = 'Nhật ký phân lead'
    _order = 'assignment_time desc'

    lead_id = fields.Many2one('sgroup.ad.data', string='Dữ liệu quảng cáo / Lead', ondelete='cascade', required=True)
    employee_id = fields.Many2one('sgroup.employee', string='Nhân viên Sale')
    assignment_time = fields.Datetime(string='Thời gian phân lead', default=fields.Datetime.now, required=True)
    state = fields.Selection([
        ('success', 'Thành công'),
        ('error', 'Lỗi / Cảnh báo')
    ], string='Trạng thái', required=True)
    notes = fields.Text(string='Chi tiết / Ghi chú')
