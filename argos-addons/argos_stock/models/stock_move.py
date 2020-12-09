# -*- coding: utf-8 -*-

from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    administration_route_ids = fields.Many2many('product.route', 'Administration Route',
                                                related="product_id.administration_route_ids", store=False)

    def _get_new_picking_values(self):
        picking_vals = super(StockMove, self)._get_new_picking_values()
        if self.group_id.sale_id.is_consultation:
            picking_vals['is_arg_prescription'] = True
        return picking_vals

    def _is_internal(self):
        self.ensure_one()
        res = super(StockMove, self)._is_internal()
        operating_internal_move = False
        if self.operating_unit_id != self.operating_unit_dest_id:
            operating_internal_move = True
        return res and operating_internal_move

    def force_entry(self):
        if self.operating_unit_id != self.operating_unit_dest_id:
            return True
        return False
