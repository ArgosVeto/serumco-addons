# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    registration_number = fields.Char('Registration Number')
    order_number = fields.Char('Order Number')
    leave_date = fields.Date('Leave Date')
    drive_permit_number = fields.Char('Drive Permit Number')
    issue_location = fields.Char('Issue Location')
    issue_date = fields.Date('Issue Date')
    partner_ids = fields.One2many('res.partner', inverse_name='employee_id')
    operating_unit_ids = fields.Many2many('operating.unit', 'operating_unit_employee_rel', 'employee_id',
                                          'operating_unit_id', 'Operating Units')
    is_veterinary = fields.Boolean('Is Veterinary')
    calypso_key = fields.Integer('Calypso key')
    note = fields.Text('Note for Website')
    hide_notifications = fields.Boolean(string='Hide notifications', help='Hide notifications')
    hide_notes = fields.Boolean(string='Hide notes', help='Hide notes')
    hide_messages = fields.Boolean(string='Hide messages', help='Hide messages')
 