# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_invoice_register_payment(self):
        if self.partner_id.supplier_rank > 0 and self.partner_id.no_payment:
            raise ValidationError(_('Can\'t create payment for this partner.'))
        return super(AccountMove, self).action_invoice_register_payment()
