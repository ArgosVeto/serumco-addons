# Copyright (C) 2020 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):
	_name = 'purchase.order'
	_inherit = ['purchase.order', 'res.brand.mixin']

	brand_id = fields.Many2one(states={'sent': [('readonly', True)], 'purchase': [('readonly', True)], 'done': [('readonly', True)],
	                                   'cancel': [('readonly', True)]})

	def action_view_invoice(self):
		"""
		Override to add brand in default value of invoice
		:return:
		"""
		self.ensure_one()
		result = super(PurchaseOrder, self).action_view_invoice()
		result['context']['default_brand_id'] = self.brand_id.id
		return result


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    brand_id = fields.Many2one(related='order_id.brand_id', readonly=True, store=True)

