# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class Animal(models.Model):
    _name = "clinical.type"
    _description = "Clinical Type"

    name = fields.Char('Name', required=True)