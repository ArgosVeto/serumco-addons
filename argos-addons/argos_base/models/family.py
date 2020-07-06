# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class Family(models.Model):
    _name = "family.family"
    _description = "Family"

    name = fields.Char('Name', required=True)