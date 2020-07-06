# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    @api.model
    def _get_operating_unit_by_location(self, location=False):
        return self.search([('name', '=', location)], limit=1)