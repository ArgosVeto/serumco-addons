# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class AnimalPathology(models.Model):
    _name = "animal.pathology"
    _description = "Animal Pathology"

    name = fields.Char('Pathology Name', required=True)
