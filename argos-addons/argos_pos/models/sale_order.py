# -*- coding: utf-8 -*-

from openerp import models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.invoice_lines')
    def _get_invoiced(self):
        for order in self:
            if not order.is_consultation:
                super(SaleOrder, self)._get_invoiced()
            else:
                invoices = self.env['pos.order'].search([('sale_order_id', '=', order.id)]).account_move.ids or []
                order.invoice_ids = invoices
                order.invoice_count = len(invoices)
