# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    routing = fields.Boolean('Routing')