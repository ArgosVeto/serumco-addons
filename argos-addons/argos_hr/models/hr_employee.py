# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    registration_number = fields.Char('Registration Number')
    order_number = fields.Char('Order Number')
    leave_date = fields.Date('Leave Date')
    drive_permit_number = fields.Char('Drive Permit Number')
    issue_location = fields.Char('Issue Location')
    issue_date = fields.Date('Issue Date')
    signature = fields.Binary('Signature')
    partner_ids = fields.One2many('res.partner', inverse_name='employee_id')
    operating_unit_ids = fields.Many2many('operating.unit', 'operating_unit_employee_rel', 'employee_id',
                                          'operating_unit_id', 'Operating Units')

    def write(self, vals):
        if 'company_id' in vals:
            vals['partner_ids'] = False
        return super(HrEmployee, self).write(vals)

    def toggle_active(self):
        self.ensure_one()
        if self.active:
            self.partner_ids = False
        return super(HrEmployee, self).toggle_active()
