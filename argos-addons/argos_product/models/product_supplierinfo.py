# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    maker_partner_id = fields.Many2one('res.partner', 'Product Maker')
    is_discount = fields.Boolean('Is discount', default=False)
    is_import = fields.Boolean('Is import', default=False)
