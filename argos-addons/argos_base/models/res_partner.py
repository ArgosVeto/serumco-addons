# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class ResPartner(models.Model):
    _inherit = 'res.partner'

    last_name = fields.Char('Last Name')
    first_name = fields.Char('First Name')
    has_tutor_curator = fields.Boolean('Tutorship/Curatorship')
    tutor_curator_id = fields.Many2one('res.partner', 'Tutor/Curator')
    clinic_id = fields.Many2one('res.partner', 'Main Clinic')
    animal_ids = fields.Many2many('animal.animal', string='Animal List')
    send_letter = fields.Boolean('Send Letter')
    send_email = fields.Boolean('Send Email')
    send_sms = fields.Boolean('Send Sms')
    to_call = fields.Boolean('Call')
    origin_id = fields.Many2one('connection.origin', 'Connection Origin')
    gmvet_id = fields.Char('GmVet ID')

    @api.model
    def _get_partner_by_name(self, name=False, phone=False):
        partner = self.search([('name', '=', name), ('phone', '=', phone)], limit=1)
        if partner:
            return partner
        return self.create({'name': name, 'phone': phone})

    @api.onchange('last_name', 'first_name')
    def _onchange_last_first_name(self):
        lastname = self.last_name if self.last_name else ''
        firstname = ' ' + self.first_name if self.first_name else ''
        self.name = '%s%s' %(lastname, firstname)
