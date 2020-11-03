# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductDocumentation(models.Model):
    _name = 'product.documentation'
    _description = 'Product Documentation'

    product_template_id = fields.Many2one('product.template', 'Product Template')
    doc_type = fields.Char('Documentation Type')
    doc_url = fields.Char('Documentation URL')