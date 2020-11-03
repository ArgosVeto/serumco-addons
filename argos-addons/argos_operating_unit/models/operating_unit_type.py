# -*- coding: utf-8 -*-

from odoo import fields, models


class OperatingUnitType(models.Model):
    _name = 'operating.unit.type'
    _description = 'Operating Unit Type'

    name = fields.Char(required=True)
