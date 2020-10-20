# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_add_subline_allowed = fields.Boolean('Allow Add Subline')