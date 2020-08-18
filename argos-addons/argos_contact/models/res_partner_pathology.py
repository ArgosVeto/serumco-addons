# -*- coding: utf-8 -*-

from odoo import fields, models


class PathologyCategory(models.Model):
    _name = 'pathology.category'

    name = fields.Char('Name')
    type = fields.Char('Type')
    typical_workshop = fields.Char('Typical Workshop')


class ResPartnerPathology(models.Model):
    _name = 'res.partner.pathology'
    _description = 'Patient Pathology'

    name = fields.Char('Pathology Name', required=True)
    quartier = fields.Char('Quartier')
    category_id = fields.Many2one('pathology.category')