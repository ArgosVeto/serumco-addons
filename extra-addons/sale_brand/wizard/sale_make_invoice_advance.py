# Copyright (C) 2020 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.model
    def _create_invoice(self, order, so_line, amount):
        invoice = super(SaleAdvancePaymentInv)._create_invoice(order, so_line, amount)
        invoice.brand_id = order.brand_id
        invoice._onchange_partner_id()
        return invoice
