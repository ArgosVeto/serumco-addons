# -*- coding: utf-8 -*-

from odoo import fields, models, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    initial_qty = fields.Float('Initial Quantity', related='move_id.sale_line_id.product_uom_qty')
    delivered_qty = fields.Float('Delivered Quantity', related='move_id.sale_line_id.qty_delivered')
    remaining_qty = fields.Float('Remaining Quantity', compute='_compute_remaining_qty')

    @api.depends('initial_qty', 'delivered_qty', 'qty_done')
    def _compute_remaining_qty(self):
        for line in self:
            line.remaining_qty = line.initial_qty - (line.delivered_qty + line.qty_done)
