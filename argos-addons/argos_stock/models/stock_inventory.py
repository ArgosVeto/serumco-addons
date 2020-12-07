# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    name = fields.Char(default=fields.Date.today().strftime("%d/%m/%Y"))
    prefill_counted_quantity = fields.Selection(default='zero', readonly=True)
