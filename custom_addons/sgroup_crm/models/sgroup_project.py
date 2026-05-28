# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SgroupProject(models.Model):
    _name = 'sgroup.project'
    _description = 'Quản lý Dự án'
    _order = 'name, id'

    name = fields.Char(string='Tên dự án', required=True)
    code = fields.Char(string='Mã dự án')
    active = fields.Boolean(string='Hoạt động', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Tên dự án đã tồn tại trên hệ thống!'),
    ]
