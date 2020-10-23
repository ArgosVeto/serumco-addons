# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id.supplier_rank > 0 and self.partner_id.no_payment:
            raise ValidationError(_('Can\'t create payment for this partner.'))
