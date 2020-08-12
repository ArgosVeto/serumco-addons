# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    state = fields.Selection([('to_approve', 'To Approve'), ('approved', 'Approved')], default='to_approve',
                             string='State')

    def send_validation_request(self):
        try:
            email_template = self.env.ref('argos_account.validation_mail_template')
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            ctx = {
                'url': '%s/web#id=%s&model=%s' %(base_url, self.id, self._name),
            }
            email_template.with_context(ctx).send_mail(self.id, force_send=True, raise_exception=True)
        except Exception as e:
            _logger.error(repr(e))

    @api.model
    def create(self, vals):
        res = super(ResPartnerBank, self).create(vals)
        res.send_validation_request()
        return res

    def action_approve_account(self):
        self.write({'state': 'approved'})
