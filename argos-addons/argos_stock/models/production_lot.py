# -*- coding: UTF-8 -*-

from odoo import models, fields


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    life_date = fields.Datetime(string='End of Life Date')
