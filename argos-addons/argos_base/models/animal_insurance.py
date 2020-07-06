# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class AnimalInsurance(models.Model):
    _name = "animal.insurance"
    _description = "Animal Insurance"

    name = fields.Char('Insurance Name', required=True)
