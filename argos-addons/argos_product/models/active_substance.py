# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductActiveSubstance(models.Model):
    _name = 'active.substance'
    _description = 'Active Substance'

    name = fields.Char('Name', required=True)