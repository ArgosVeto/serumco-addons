# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    has_tutor_curator = fields.Boolean('Tutorship/Curatorship')
    tutor_curator_id = fields.Many2one('res.partner', 'Tutor/Curator')
    send_letter = fields.Boolean('Send Letter')
    send_email = fields.Boolean('Send Email')
    send_sms = fields.Boolean('Send Sms')
    to_call = fields.Boolean('Call')
    signup_expiration = fields.Datetime(groups='base.group_erp_manager,argos_base.mrdv_group_user')
    signup_token = fields.Char(groups='base.group_erp_manager,argos_base.mrdv_group_user')
    signup_type = fields.Char(groups='base.group_erp_manager,argos_base.mrdv_group_user')
    social_reason = fields.Char('Social Reason')

    @api.model
    def _get_partner_by_name(self, name=False, phone=False):
        domain = [('name', '=', name)]
        if phone:
            domain.extend([('phone', '=', phone)])
        partner = self.search(domain, limit=1)
        if partner:
            return partner
        return self.create({'name': name, 'phone': phone})

    @api.constrains('lastname')
    def _check_lastname(self):
        if not self._context.get('from_bo'):
            return
        if self._context.get('copy'):
            return
        for rec in self.filtered(lambda p: not p.is_company):
            if rec.lastname and not rec.lastname.isupper():
                raise ValidationError(_('Lastname must be upper'))

    @api.constrains('firstname')
    def _check_firstname(self):
        if not self._context.get('from_bo'):
            return
        for rec in self.filtered(lambda p: not p.is_company):
            if rec.firstname and not rec.firstname[0].isupper():
                raise ValidationError(_('First letter of firstname must be upper'))

    @api.constrains('lastname', 'firstname', 'email')
    def _check_unique_partner(self):
        for rec in self.filtered(lambda p: not p.is_company):
            if rec.lastname and rec.firstname and rec.email:
                domain = [
                    ('id', '!=', rec.id),
                    ('lastname', '=', rec.lastname),
                    ('firstname', '=', rec.firstname),
                    ('email', '=', rec.email),
                ]
                if self.search_count(domain):
                    raise ValidationError(_('Partner must be unique'))

    def send_confirmation_mail(self):
        self.ensure_one()
        try:
            email_template = self.env.ref('argos_base.confirmation_mail_template')
            email_template.send_mail(self.id, force_send=True, raise_exception=True)
        except Exception as e:
            _logger.error(repr(e))

    @api.model
    def create(self, vals):
        record = super(ResPartner, self).create(vals)
        if self._context.get('from_bo', False):
            record.send_confirmation_mail()
        return record
