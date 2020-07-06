# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class AnimalDiet(models.Model):
    _name = "animal.diet"
    _description = "Animal Diet"

    name = fields.Char('Name', required=True)
