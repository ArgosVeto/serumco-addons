# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')

    @api.onchange('requested_by')
    def onchange_requested_by(self):
        self.operating_unit_id = self.requested_by.default_operating_unit_id

    @api.onchange('operating_unit_id')
    def onchange_operating_unit(self):
        type_obj = self.env["stock.picking.type"]
        types = type_obj.search(
            [("code", "=", "incoming"), ("warehouse_id.operating_unit_id", "=", self.operating_unit_id.id)]
        )
        if not types:
            types = type_obj.search(
                [("code", "=", "incoming"), ("warehouse_id.company_id", "=", self.env.user.company_id.id)]
            )
        self.picking_type_id = types[:1]
