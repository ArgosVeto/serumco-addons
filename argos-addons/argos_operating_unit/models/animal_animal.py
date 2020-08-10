# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AnimalAnimal(models.Model):
    _inherit = 'animal.animal'

    operating_unit_id = fields.Many2one('operating.unit', 'Main Clinic', required=False)

