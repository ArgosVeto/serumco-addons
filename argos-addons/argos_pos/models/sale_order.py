# -*- coding: utf-8 -*-

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pos_sold = fields.Boolean(string="Pos Sold", copy=False)

    @api.model
    def new_sent_order_json(self, from_days, config_id):
        order_json_format = []
        # get all order (consultation type only) even it has already a delivery with it
        for order in self.sudo().search(
                [('state', 'in', ['sale', 'draft']), ('is_consultation', '=', True), ('pos_sold', '=', False),
                 ('date_order', '>', from_days)]):
            order_json_format.append(
                order.read(['id', 'name', 'date_order', 'amount_total', 'partner_id', 'order_line', 'state']))
        return {'data': order_json_format}

    @api.depends('order_line.invoice_lines')
    def _get_invoiced(self):
        for order in self:
            if not order.is_consultation:
                super(SaleOrder, self)._get_invoiced()
            else:
                invoices = self.env['pos.order'].search([('sale_order_id', '=', order.id)]).account_move.ids or []
                order.invoice_ids = invoices
                order.invoice_count = len(invoices)

    @api.model
    def quotation_fetch_line(self, quotation_id):
        quotation_obj = self.sudo().browse(int(quotation_id))
        if quotation_obj:
            return quotation_obj.order_line.read(
                ['product_id', 'price_unit', 'product_uom_qty', 'qty_delivered', 'tax_id'])
        return False
