# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    is_incineris_species = fields.Boolean()

