# -*- coding: utf-8 -*-

from odoo import fields, models


class OperatingUnitService(models.Model):
    _name = 'operating.unit.service'
    _description = 'Operating Unit Service'

    name = fields.Char(required=True)
    description = fields.Char('Description')
    service_partner_id = fields.Many2one('res.partner', 'Partner')
