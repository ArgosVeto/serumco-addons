# -*- coding: utf-8 -*-
# Developed by Auguria Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details

from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    def name_short_without_code(self):
        names = dict(self.product_id.with_context(display_default_code=False).name_get())
        return names.get(self.product_id.id, False)