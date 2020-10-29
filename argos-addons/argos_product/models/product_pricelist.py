# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')