# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SgroupCustomer(models.Model):
    _name = 'sgroup.customer'
    _description = 'Khách hàng'
    _order = 'create_date desc'

    name = fields.Char(string='Tên khách hàng', required=True)
    phone = fields.Char(string='Số điện thoại', required=True)
    email = fields.Char(string='Email')
    project_id = fields.Many2one('sgroup.project', string='Dự án quan tâm', ondelete='restrict')
    employee_id = fields.Many2one('sgroup.employee', string='Nhân viên phụ trách', domain="[('status', '=', 'active')]")
    status = fields.Selection([
        ('new', 'Mới'),
        ('contacting', 'Đang liên hệ'),
        ('potential', 'Tiềm năng'),
        ('deposited', 'Chốt cọc'),
        ('no_need', 'Không nhu cầu')
    ], string='Tình trạng khách hàng', default='new', required=True)
    level = fields.Selection([
        ('f1', 'F1'),
        ('f2', 'F2'),
        ('f3', 'F3'),
        ('f4', 'F4'),
        ('f5', 'F5'),
        ('undefined', 'Chưa xác định')
    ], string='Cấp độ khách hàng', default='undefined', required=True)
    source = fields.Char(string='Nguồn khách hàng')
    created_date = fields.Date(string='Ngày tạo', default=fields.Date.context_today)

    _phone_unique = models.Constraint(
        'unique(phone)',
        'Số điện thoại khách hàng đã tồn tại!'
    )
