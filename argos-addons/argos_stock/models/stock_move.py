# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    administration_route_ids = fields.Many2many('product.route', 'Administration Route',
                                                related="product_id.administration_route_ids", store=False)

    def _get_new_picking_values(self):
        picking_vals = super(StockMove, self)._get_new_picking_values()
        if self.group_id.sale_id.is_consultation:
            picking_vals['is_arg_prescription'] = True
        return picking_vals

