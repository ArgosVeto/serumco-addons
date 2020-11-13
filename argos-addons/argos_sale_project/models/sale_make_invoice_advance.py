# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for order in sale_orders:
            for project in order.project_ids:
                project.write({
                    'billed': True,
                    'active': False,
                })
            order.write({'invoice_creation_date': fields.Date.today()})
            if any(line.product_id.act_type in ['euthanasia', 'incineration'] for line in order.order_line):
                order.patient_id.write({
                    'is_dead': True,
                    'death_date': order.consultation_date
                })
        return super(SaleAdvancePaymentInv, self).create_invoices()
