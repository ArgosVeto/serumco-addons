# -*- coding: utf-8 -*-

from odoo import models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_done(self):
        super(StockPicking, self).action_done()
        pickings = self.filtered(lambda pick: pick.picking_type_code == 'incoming')
        for picking in pickings:
            purchase = picking.purchase_id
            if purchase:
                origins = purchase.origin.split(', ') if purchase.origin else False
                if origins:
                    sale_orders = self.env['sale.order'].search(
                        [('name', 'in', origins), ('website_id', '!=', False)])
                    sale_orders.send_reception_sms()
