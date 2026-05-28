# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SgroupEmployee(models.Model):
    _name = 'sgroup.employee'
    _description = 'Nhân viên Sale'
    _order = 'name'

    name = fields.Char(string='Tên nhân viên', required=True)
    phone = fields.Char(string='Số điện thoại')
    email = fields.Char(string='Email')
    team = fields.Char(string='Đội nhóm / Team')
    user_id = fields.Many2one('res.users', string='Tài khoản Odoo')
    status = fields.Selection([
        ('active', 'Hoạt động'),
        ('inactive', 'Tạm ngưng')
    ], string='Tình trạng nhân viên', default='active', required=True)

    _phone_unique = models.Constraint(
        'unique(phone)',
        'Số điện thoại nhân viên đã tồn tại!'
    )
    _email_unique = models.Constraint(
        'unique(email)',
        'Email nhân viên đã tồn tại!'
    )
