# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    slot_id = fields.Many2one('planning.slot', 'Planning Slot')
