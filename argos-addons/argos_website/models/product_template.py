# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_new = fields.Boolean('Is New')

    @api.onchange('categ_id')
    def _onchange_categ_id(self):
        self.public_categ_ids = [(6, 0, self.categ_id.public_category_id.ids)]
