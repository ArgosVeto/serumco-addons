# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PurchaseConfirmationWizard(models.TransientModel):
    _name = 'purchase.confirmation.wizard'

    description = fields.Char(readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(PurchaseConfirmationWizard, self).default_get(fields)
        if self._context.get('check_shipping_fees', False):
            res['description'] = _('Shipping fees not reached.')
            return res
        return res

    def action_confirm(self):
        order = self.env['purchase.order'].browse(self._context.get('active_id', False))
        if order and self._context.get('check_shipping_fees', False):
            return order.with_context(check_shipping_fees=False).button_confirm()
        return True
