# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class LocationLocation(models.Model):
    _name = 'location.location'

    name = fields.Char('Tattoo location')
    type = fields.Selection([('chip', 'Chip'), ('tattoo', 'Tattoo')], 'Type')