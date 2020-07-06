# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class LivingEnvironment(models.Model):
    _name = "living.environment"
    _description = "Living Environment"

    name = fields.Char('Name', required=True)
