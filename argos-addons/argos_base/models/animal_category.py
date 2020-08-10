# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class AnimalCategory(models.Model):
    _name = "animal.category"
    _description = "Animal Category"

    name = fields.Char('Category Name', required=True)
    is_incineris_species = fields.Boolean()

    @api.model
    def _get_animal_category(self, category):
        return self.search([('name', '=', category)], limit=1)
