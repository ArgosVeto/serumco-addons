# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class ResPartner(models.Model):
    _inherit = 'res.partner'

    operating_unit_id = fields.Many2one('operating.unit', 'Clinic', required=False)
