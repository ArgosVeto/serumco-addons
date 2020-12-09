# -*- coding: utf-8 -*-

from odoo import models, api, fields


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    emergency = fields.Boolean('Emergency')
