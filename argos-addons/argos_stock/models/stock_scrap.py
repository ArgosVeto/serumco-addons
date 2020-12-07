# -*- coding: utf-8 -*-

from odoo import fields, models


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    scrap_reason = fields.Selection([
        ('expiration_date', 'Expiration date passed'),
        ('use_date', 'Use date after first use passed'),
        ('storage_condition', 'Storage conditions not respected'),
        ('product_deteriorated', 'Products deteriorated in the clinic'),
        ('return_medicine', 'Customer return cannot be reintegrated to stock - medicine'),
        ('return_other', 'Customer return cannot be reintegrated to stock - other'),
        ('batch_recall', 'batch recall by laboratory - destruction on site')
    ], 'Scrap reason', required=True)

    def action_validate(self):
        if self._context.get('default_picking_id', False):
            picking = self.env['stock.picking'].browse(self._context.get('default_picking_id'))
            picking.write({'scrap_reason': self.scrap_reason})
        return super(StockScrap, self).action_validate()
