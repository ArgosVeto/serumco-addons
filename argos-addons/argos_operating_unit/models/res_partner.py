# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    operating_unit_id = fields.Many2one('operating.unit', 'Clinic', required=False)
    partnership_end_date = fields.Date('Partnership End Date')
