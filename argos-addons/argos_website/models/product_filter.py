# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductFilter(models.Model):
    _name = 'product.filter'

    name = fields.Char('Name')
    is_filter_visible = fields.Boolean('Filter visible in web')
    product_filter_line_ids = fields.One2many('product.filter.line', 'product_filter_id', 'Product filter lines')

    filters_line_ids = fields.One2many('product.template.filter.line', 'filter_id', 'Lines')
    product_tmpl_ids = fields.Many2many('product.template', string="Related Products", compute='_compute_products', store=True)

    @api.depends('filters_line_ids.product_id')
    def _compute_products(self):
        for pa in self:
            pa.product_tmpl_ids = pa.filters_line_ids.product_id

class ProductFilterLine(models.Model):
    _name = 'product.filter.line'

    name = fields.Char('Name')
    product_filter_id = fields.Many2one('product.filter')

class ProductTemplateFilter(models.Model):
    _inherit = 'product.template'

    product_filter_ids = fields.One2many("product.template.filter.line", 'product_id')

class ProductTemplateFilterline(models.Model):
    _name = 'product.template.filter.line'

    active = fields.Boolean(default=True)
    filter_id = fields.Many2one('product.filter')
    filter_line_ids = fields.Many2many('product.filter.line', domain="[('product_filter_id', '=', filter_id)]",)
    product_id = fields.Many2one('product.template')
