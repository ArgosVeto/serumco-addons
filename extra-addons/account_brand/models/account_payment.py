# Copyright (C) 2020 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPayment(models.Model):
	_inherit = 'account.payment'

	def _prepare_payment_moves(self):
		moves = super(AccountPayment, self)._prepare_payment_moves()
		for move in moves:
			move.update({'brand_id': self._get_brand_from_invoices()})
		return moves

	def _get_brand_from_invoices(self):
		self.ensure_one()
		return self.invoice_ids and self.invoice_ids[0].brand_id.id or False
