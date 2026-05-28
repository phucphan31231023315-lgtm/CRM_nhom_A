# -*- coding: utf-8 -*-
from odoo import models, fields, api

class SgroupRevenue(models.Model):
    _name = 'sgroup.revenue'
    _description = 'Quản lý Doanh thu'
    _order = 'recorded_date desc, id desc'

    customer_id = fields.Many2one('sgroup.customer', string='Khách hàng', required=True, ondelete='restrict')
    employee_id = fields.Many2one('sgroup.employee', string='Nhân viên phụ trách', domain="[('status', '=', 'active')]", store=True, readonly=False)
    project_id = fields.Many2one('sgroup.project', string='Dự án', ondelete='restrict')
    product = fields.Char(string='Sản phẩm / Căn')
    status = fields.Selection([
        ('booking', 'Booking'),
        ('deposit', 'Đặt cọc'),
        ('contract', 'Ký HĐMB'),
        ('paid', 'Đã thanh toán'),
        ('cancel', 'Hủy')
    ], string='Trạng thái giao dịch', default='booking', required=True)
    booking_amount = fields.Float(string='Số tiền booking')
    deposit_amount = fields.Float(string='Số tiền cọc')
    recorded_date = fields.Date(string='Ngày ghi nhận', default=fields.Date.context_today, required=True)
    notes = fields.Text(string='Ghi chú')

    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        if self.customer_id:
            if self.customer_id.employee_id:
                self.employee_id = self.customer_id.employee_id.id
            if self.customer_id.project_id:
                self.project_id = self.customer_id.project_id.id
