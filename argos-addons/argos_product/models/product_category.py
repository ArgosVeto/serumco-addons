# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_antibiotic = fields.Boolean('Is Antibiotic')
    is_critical = fields.Boolean('Is Critical')
    tooltip_text = fields.Text('Tooltip Text')
