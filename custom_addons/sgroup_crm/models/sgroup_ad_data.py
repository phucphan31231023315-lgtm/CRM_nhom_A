# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class SgroupAdData(models.Model):
    _name = 'sgroup.ad.data'
    _description = 'Dữ liệu quảng cáo / Lead'
    _order = 'lead_time desc, id desc'

    name = fields.Char(string='Tên khách hàng', required=True)
    phone = fields.Char(string='Số điện thoại', required=True)
    email = fields.Char(string='Email')
    project = fields.Char(string='Dự án (Text)')
    project_id = fields.Many2one('sgroup.project', string='Dự án quan tâm', ondelete='restrict')
    source = fields.Char(string='Nguồn lead')
    campaign = fields.Char(string='Chiến dịch quảng cáo')
    lead_time = fields.Datetime(string='Thời gian phát sinh lead', default=fields.Datetime.now)
    sync_date = fields.Datetime(string='Ngày đồng bộ', default=fields.Datetime.now)
    
    employee_id = fields.Many2one('sgroup.employee', string='Nhân viên phụ trách')
    state = fields.Selection([
        ('draft', 'Mới'),
        ('synced', 'Đã đồng bộ'),
        ('auth_error', 'Lỗi xác thực'),
        ('duplicate_phone', 'Trùng số điện thoại'),
        ('no_rule', 'Chưa thiết lập quy tắc')
    ], string='Trạng thái đồng bộ', default='draft')
    
    history_ids = fields.One2many('sgroup.assignment.history', 'lead_id', string='Lịch sử phân quyền')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            project_name = vals.get('project')
            if project_name and not vals.get('project_id'):
                project_name = project_name.strip()
                # Find project matching name (case-insensitive)
                project_rec = self.env['sgroup.project'].search([('name', '=ilike', project_name)], limit=1)
                if not project_rec:
                    # Create new project automatically
                    project_rec = self.env['sgroup.project'].create({'name': project_name})
                vals['project_id'] = project_rec.id
        
        records = super(SgroupAdData, self).create(vals_list)
        for record in records:
            record.action_auto_assign()
        return records

    def action_auto_assign(self):
        self.ensure_one()
        _logger.info("Executing auto assign for lead %s (phone: %s, project: %s)", self.name, self.phone, self.project_id.name if self.project_id else 'Không có')
        
        # 1. Kiểm tra trùng số điện thoại
        if self.phone:
            # Check other sgroup.ad.data records with this phone (excluding self)
            duplicate_lead = self.env['sgroup.ad.data'].search([
                ('phone', '=', self.phone),
                ('id', '!=', self.id)
            ], limit=1)
            # Check sgroup.customer records with this phone
            duplicate_customer = self.env['sgroup.customer'].search([
                ('phone', '=', self.phone)
            ], limit=1)
            
            if duplicate_lead or duplicate_customer:
                self.write({
                    'state': 'duplicate_phone',
                })
                # Log duplicate history
                self.env['sgroup.assignment.history'].create({
                    'lead_id': self.id,
                    'assignment_time': fields.Datetime.now(),
                    'state': 'error',
                    'notes': _('Cảnh báo trùng số điện thoại: Số điện thoại %s đã tồn tại trên hệ thống.') % self.phone
                })
                return
        
        # 2. Tìm quy tắc phân lead gắn với dự án cụ thể
        if not self.project_id:
            self.write({'state': 'no_rule'})
            self.env['sgroup.assignment.history'].create({
                'lead_id': self.id,
                'assignment_time': fields.Datetime.now(),
                'state': 'error',
                'notes': _('Lead không có thông tin dự án quan tâm.')
            })
            return

        rule = self.env['sgroup.assignment.rule'].search([
            ('project_id', '=', self.project_id.id),
            ('active', '=', True)
        ], limit=1)

        if not rule:
            self.write({'state': 'no_rule'})
            self.env['sgroup.assignment.history'].create({
                'lead_id': self.id,
                'assignment_time': fields.Datetime.now(),
                'state': 'error',
                'notes': _('Chưa thiết lập quy tắc phân lead cho dự án "%s".') % self.project_id.name
            })
            return

        if not rule.line_ids:
            self.write({'state': 'no_rule'})
            self.env['sgroup.assignment.history'].create({
                'lead_id': self.id,
                'assignment_time': fields.Datetime.now(),
                'state': 'error',
                'notes': _('Quy tắc phân lead của dự án "%s" chưa cấu hình nhân viên.') % self.project_id.name
            })
            return

        # 3. Phân phối Lead theo Round-robin
        # Chỉ chia cho nhân viên đang hoạt động nằm trong danh sách nhân viên của quy tắc đó
        lines = rule.line_ids.filtered(lambda l: l.employee_id.status == 'active')
        if not lines:
            self.write({'state': 'no_rule'})
            self.env['sgroup.assignment.history'].create({
                'lead_id': self.id,
                'assignment_time': fields.Datetime.now(),
                'state': 'error',
                'notes': _('Không có nhân viên sale nào hoạt động trong quy tắc phân lead của dự án "%s".') % self.project_id.name
            })
            return

        # Sort lines by sequence
        sorted_lines = lines.sorted(key=lambda l: (l.sequence, l.id))
        
        assigned_line = False
        for line in sorted_lines:
            if line.assigned_count < line.capacity:
                assigned_line = line
                break
                
        # Nếu tất cả nhân viên đã đạt hạn ngạch, reset lại bộ đếm và chọn người đầu tiên
        if not assigned_line:
            _logger.info("All sales reached capacity for rule %s. Resetting counts.", rule.name)
            for line in sorted_lines:
                line.write({'assigned_count': 0})
            assigned_line = sorted_lines[0]

        # 4. Gán lead cho nhân viên được chọn và cập nhật trạng thái "Đã đồng bộ"
        employee = assigned_line.employee_id
        self.write({
            'employee_id': employee.id,
            'state': 'synced'
        })
        
        # Tăng số lượng đã chia của nhân viên đó trong vòng xoay
        assigned_line.write({'assigned_count': assigned_line.assigned_count + 1})

        # 5. Tạo mới hoặc Cập nhật thông tin Khách hàng
        # Vì đã kiểm tra SĐT ở bước 1, nên nếu chạy tới đây chắc chắn SĐT này là duy nhất trong danh sách khách hàng.
        customer = self.env['sgroup.customer'].create({
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'project_id': self.project_id.id,
            'source': self.source or 'Google Form',
            'employee_id': employee.id,
            'status': 'new',
            'level': 'undefined',
            'created_date': fields.Date.context_today(self),
        })
        customer_notes = _('Đã tạo thành công khách hàng mới và bàn giao cho Sale %s.') % employee.name

        # 6. Ghi nhật ký phân lead
        self.env['sgroup.assignment.history'].create({
            'lead_id': self.id,
            'employee_id': employee.id,
            'assignment_time': fields.Datetime.now(),
            'state': 'success',
            'notes': _('Phân phối lead thành công cho nhân viên "%s" theo Quy tắc dự án "%s". %s') % (employee.name, rule.name, customer_notes)
        })
