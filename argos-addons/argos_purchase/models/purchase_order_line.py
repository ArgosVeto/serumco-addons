# -*- coding: utf-8 -*-

from odoo import models, fields


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    emergency = fields.Boolean('Emergency')
    request_line_ids = fields.Many2many('purchase.request.line', 'purchase_request_purchase_order_line_rel', 'purchase_order_line_id',
                                        'purchase_request_line_id', 'Request Lines', readonly=True)
