# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_add_subline_allowed = fields.Boolean('Allow Add Subline')

    @api.onchange('is_add_subline_allowed')
    def onchange_is_add_subline_allowed(self):
        self.pack_modifiable = self.is_add_subline_allowed
