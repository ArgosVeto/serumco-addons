# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    description_sale = fields.Text('Sales Description')
    description_pickingout = fields.Text('Description on Delivery Orders')
    renewal = fields.Char('Renewal')

    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        self.update({
            'description_sale': self.product_id.description_sale,
            'description_pickingout': self.product_id.description_pickingout,
            'renewal': self.product_id.renewal,
        })
        return res
