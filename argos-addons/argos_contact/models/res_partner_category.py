# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    is_incineris_species = fields.Boolean()
    type = fields.Selection([('contact', 'Contact'), ('patient', 'Patient')], 'Type', default='contact')
    gmvet_id = fields.Char('Gmvet id')

    @api.model
    def _get_category_by_name(self, name, type):
        category = self.search([('name', '=', name), ('type', '=', type)])
        if not category:
            return self.create({'name': name, 'type': type})
        return category

    @api.constrains('name')
    def _check_unique_species(self):
        for rec in self.filtered(lambda p: p.type == 'patient'):
            domain = [
                ('id', '!=', rec.id),
                ('name', '=', rec.name),
                ('type', '=', 'patient'),
            ]
            if self.search_count(domain):
                raise ValidationError(_('Species must be unique'))
