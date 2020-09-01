# -*- coding: utf-8 -*-

from odoo import fields, models


class OperatingUnitCertification(models.Model):
    _name = 'operating.unit.certification'
    _description = 'Operating Unit Certification'

    name = fields.Char(required=True)