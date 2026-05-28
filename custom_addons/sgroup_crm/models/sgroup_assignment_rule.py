# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SgroupAssignmentRule(models.Model):
    _name = 'sgroup.assignment.rule'
    _description = 'Quy tắc phân chia Lead'
    _order = 'id'

    name = fields.Char(string='Tên quy tắc', required=True)
    project_id = fields.Many2one('sgroup.project', string='Dự án áp dụng', required=True, help='Chọn dự án để khớp tự động khi Lead về.', ondelete='restrict')
    active = fields.Boolean(string='Hoạt động', default=True)
    line_ids = fields.One2many('sgroup.assignment.rule.line', 'rule_id', string='Chi tiết phân phối')

    _sql_constraints = [
        ('project_uniq', 'unique(project_id)', 'Mỗi dự án chỉ được cấu hình tối đa một quy tắc phân lead!')
    ]

class SgroupAssignmentRuleLine(models.Model):
    _name = 'sgroup.assignment.rule.line'
    _description = 'Chi tiết phân phối Lead'
    _order = 'sequence, id'

    rule_id = fields.Many2one('sgroup.assignment.rule', string='Quy tắc', ondelete='cascade', required=True)
    employee_id = fields.Many2one('sgroup.employee', string='Nhân viên Sale', domain="[('status', '=', 'active')]", required=True)
    capacity = fields.Integer(string='Hạn ngạch / vòng (Capacity)', default=1, help='Số lượng lead tối đa nhân viên này được nhận trong một vòng xoay.')
    assigned_count = fields.Integer(string='Đã chia trong vòng', default=0, readonly=True, help='Số lượng lead nhân viên này đã nhận trong vòng xoay hiện tại.')
    sequence = fields.Integer(string='Thứ tự', default=10)
