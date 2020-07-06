# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class ResPartner(models.Model):
    _inherit = 'res.partner'

    has_tutor_curator = fields.Boolean('Tutorship/Curatorship')
    tutor_curator_id = fields.Many2one('res.partner', 'Tutor/Curator')
    clinic_id = fields.Many2one('res.partner', 'Main Clinic')
    animal_ids = fields.Many2many('animal.animal', string='Animal List')
    send_letter = fields.Boolean('Send Letter')
    send_email = fields.Boolean('Send Email')
    send_sms = fields.Boolean('Send Sms')
    to_call = fields.Boolean('Call')

    @api.model
    def _get_partner_by_name(self, name=False, phone=False):
        partner = self.search([('name', '=', name), ('phone', '=', phone)], limit=1)
        if partner:
            return partner
        else:
            return self.create({
                'name': name,
                'phone': phone
            })
