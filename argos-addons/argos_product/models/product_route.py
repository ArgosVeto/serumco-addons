# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductRoute(models.Model):
    _name = 'product.route'
    _description = 'Product Route'

    name = fields.Char('Name', required=True)