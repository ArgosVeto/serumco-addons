# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductCategory(models.Model):
    _inherit = 'product.category'
    _inherits = {'product.public.category': 'public_category_id'}

    name = fields.Char(related='public_category_id.name', readonly=False)
    sequence = fields.Integer(related='public_category_id.sequence', readonly=False)
    public_category_id = fields.Many2one('product.public.category', 'Public Category', required=True, ondelete='cascade')


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    name = fields.Char(required=False)
    category_ids = fields.One2many('product.category', 'public_category_id', 'Categories', required=False)
    product_category_parent_id = fields.Many2one(related='category_ids.parent_id', store=True, readonly=True)
    parent_id = fields.Many2one(related='product_category_parent_id.public_category_id', readonly=True)

    def name_get(self):
        res = []
        for category in self:
            res.append((category.id, " / ".join(category.parents_and_self.mapped('name') or '')))
        return res