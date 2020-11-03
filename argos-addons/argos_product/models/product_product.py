# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'
    _order = 'is_top_ten desc, default_code, name, id'