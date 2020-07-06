# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class AnimalRace(models.Model):
    _name = "animal.race"
    _description = "Animal Race"

    name = fields.Char('Race Name', required=True)