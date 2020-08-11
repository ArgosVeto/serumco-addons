# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartnerPathology(models.Model):
    _name = 'res.partner.pathology'
    _description = 'Patient Pathology'

    name = fields.Char('Pathology Name', required=True)
