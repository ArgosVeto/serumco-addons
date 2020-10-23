# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools
from odoo.exceptions import ValidationError
import logging
from stdnum.fr.siret import is_valid as is_valid_siret
from stdnum.fr.siren import is_valid as is_valid_siren

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
    is_centravet = fields.Boolean('Is Centravet Supplier')
    kinetec_code = fields.Char('Kinetec Code')
    siren = fields.Char('Siren', size=9)

    @api.model
    def _get_partner_by_name(self, name=False, phone=False):
        domain = [('name', '=', name)]
        if phone:
            domain.extend([('phone', '=', phone)])
        partner = self.search(domain, limit=1)
        if partner:
            return partner
        return self.create({'name': name, 'phone': phone})

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
    def _format_name_vals(self, vals):
        if vals.get('lastname') and not vals['lastname'].isupper():
            vals['lastname'] = vals['lastname'].upper()
        if vals.get('firstname') and not vals['firstname'].istitle():
            vals['firstname'] = vals['firstname'].title()
        return vals

    @api.model
    def create(self, vals):
        if self._context.get('from_bo', False):
            vals = self._format_name_vals(vals)
        record = super(ResPartner, self).create(vals)
        if self._context.get('from_bo', False):
            record.send_confirmation_mail()
        return record

    def write(self, vals):
        if self._context.get('from_bo', False):
            vals = self._format_name_vals(vals)
        return super(ResPartner, self).write(vals)

    @api.constrains('siret')
    def _check_partner_siret(self):
        if not self._context.get('from_bo', False):
            return
        for rec in self:
            if rec.siret and not is_valid_siret(rec.siret):
                raise ValidationError(_('Invalid format of Siret.'))

    @api.constrains('siren')
    def _check_partner_siren(self):
        if not self._context.get('from_bo', False):
            return
        for rec in self:
            if rec.siren and not is_valid_siren(rec.siren):
                raise ValidationError(_('Invalid format of Siren.'))
