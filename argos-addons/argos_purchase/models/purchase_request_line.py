# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit', related='request_id.operating_unit_id')
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type', related='request_id.picking_type_id')