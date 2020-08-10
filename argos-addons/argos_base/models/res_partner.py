# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools

class Clinic(models.Model):
    _name = 'clinical.clinical'


class ResPartner(models.Model):
    _inherit = 'res.partner'

    has_tutor_curator = fields.Boolean('Tutorship/Curatorship')
    tutor_curator_id = fields.Many2one('res.partner', 'Tutor/Curator')
    animal_ids = fields.Many2many('animal.animal', string='Animal List')
    send_letter = fields.Boolean('Send Letter')
    send_email = fields.Boolean('Send Email')
    send_sms = fields.Boolean('Send Sms')
    to_call = fields.Boolean('Call')
    origin_id = fields.Many2one('connection.origin', 'Connection Origin')
    signup_expiration = fields.Datetime(groups='base.group_erp_manager,argos_base.mrdv_group_user')
    signup_token = fields.Char(groups='base.group_erp_manager,argos_base.mrdv_group_user')
    signup_type = fields.Char(groups='base.group_erp_manager,argos_base.mrdv_group_user')

    @api.model
    def _get_partner_by_name(self, name=False, phone=False):
        partner = self.search([('name', '=', name), ('phone', '=', phone)], limit=1)
        if partner:
            return partner
        return self.create({'name': name, 'phone': phone})
