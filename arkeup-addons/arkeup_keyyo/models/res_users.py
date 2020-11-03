# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    sip = fields.Char('SIP Login')
    keyyo_line_server_id = fields.Many2one('keyyo.line.server', 'Keyyo Line')

    @api.constrains('sip')
    def _check_unique_sip(self):
        if self.search([('id', '!=', self.id), ('sip', '=', self.sip), ('sip', '!=', False)], limit=1):
            raise ValidationError(_('SIP must be unique!'))
        return True
