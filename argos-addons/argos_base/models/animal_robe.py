# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class AnimalRobe(models.Model):
    _name = "animal.robe"
    _description = "Animal Robe"

    name = fields.Char('Robe Name', required=True)
