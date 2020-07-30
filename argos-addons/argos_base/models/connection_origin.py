# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class ConnectionOrigin(models.Model):
    _name = "connection.origin"
    _description = "Connection Origin"

    name = fields.Char('Name')
