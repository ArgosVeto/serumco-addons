# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderRefer(models.TransientModel):
    _inherit = 'sale.order.refer'

    def get_refer_values(self, order):
        values = super(SaleOrderRefer, self).get_refer_values(order)
        company = values.get('company_id')
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', company)], limit=1)
        values.update({'warehouse_id': warehouse.id})
        return values