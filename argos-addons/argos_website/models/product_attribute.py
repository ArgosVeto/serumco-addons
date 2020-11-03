# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    is_attribute_visible = fields.Boolean('Filter visible in Web', help='It indicates that current attribute is visible in shop filter.')