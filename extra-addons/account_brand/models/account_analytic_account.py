# Copyright (C) 2020 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticAccount(models.Model):
	_name = 'account.analytic.account'
	_inherit = ['account.analytic.account', 'res.brand.mixin']


class AccountAnalyticLine(models.Model):
	_inherit = 'account.analytic.line'

	brand_id = fields.Many2one(related='account_id.brand_id', readony=True, store=True)
