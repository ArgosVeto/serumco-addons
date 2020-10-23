# -*- coding: utf-8 -*-

from odoo import fields, models


class OperatingUnitRoom(models.Model):
    _name = 'operating.unit.room'
    _description = 'Operating Unit Room'

    name = fields.Char('Name')
    operating_unit_id = fields.Many2one('operating.unit', 'Clinic')
    area = fields.Float('Area (decimal number in m²)')
