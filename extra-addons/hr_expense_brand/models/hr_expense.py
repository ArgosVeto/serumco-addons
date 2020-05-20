# Copyright (C) 2020 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class HrExpense(models.Model):
	_name = 'hr.expense'
	_inherit = ['hr.expense', 'res.brand.mixin']

	brand_id = fields.Many2one(states={'reported': [('readonly', True)], 'approved': [('readonly', True)], 'done': [('readonly', True)],
	                                   'refused': [('readonly', True)]})

	@api.onchange('brand_id')
	def _onchange_brand_id(self):
		super(HrExpense, self)._onchange_brand_id()
		self.update({'analytic_account_id': self.brand_id.analytic_account_id.id})

	def _prepare_move_values(self):
		result = super(HrExpense, self)._prepare_move_values()
		result.update({'brand_id': self.brand_id.id})
		return result
