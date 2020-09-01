# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    is_incineris_species = fields.Boolean()
    type = fields.Selection([('contact', 'Contact'), ('patient', 'Patient')], 'Type', default='contact')
    gmvet_id = fields.Char('Gmvet id')

    @api.model
    def _get_category_by_name(self, name, type):
        parameter = self.search([('name', '=', name), ('type', '=', type)])
        if not parameter:
            return self.create({'name': name, 'type': type})
        return parameter
