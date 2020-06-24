# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class KeyyoLineServer(models.Model):
	_name = 'keyyo.line.server'
	_rec_name = 'name'
	_description = 'Keyyo Line Server'

	name = fields.Char()
	active = fields.Boolean(default=True)
	user_ids = fields.One2many('res.users', 'keyyo_line_server_id', 'Users', readonly=True)

	@api.constrains('sip')
	def _check_unique_name(self):
		if self.search([('id', '!=', self.id), ('name', '=', self.name)], limit=1):
			raise ValidationError(_('Keyyo Line must be unique!'))
		return True
