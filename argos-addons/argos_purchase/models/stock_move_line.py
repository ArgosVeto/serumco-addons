# -*- coding: utf-8 -*-

from odoo import models, fields


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    free_unit = fields.Boolean('Free Unit')
