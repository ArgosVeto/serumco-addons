# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    slot_id = fields.Many2one('planning.slot', 'Planning Slot')
    slot_arrival_time = fields.Datetime('Slot Arrival Time', track_visibility='onchange', copy=False)

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if res.slot_id:
            res.slot_arrival_time = res.slot_id.arrival_time
        if res.is_consultation:
            res.arrival_time = fields.Datetime.now()
        return res