
from odoo import models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _prepare_internal_svl_vals(self, quantity, unit_cost):
        self.ensure_one()
        # Quantity is negative for out valuation layers.
        vals = {
            'product_id': self.id,
            'value': quantity * unit_cost,
            'unit_cost': unit_cost,
            'quantity': quantity,
        }
        return vals