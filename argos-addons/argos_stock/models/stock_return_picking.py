# -*- coding: utf-8 -*-

from odoo import fields, models


class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    return_reason = fields.Selection([
        ('no_order', 'Not ordered products'),
        ('damaged', 'Products damaged upon receipt'),
        ('improper_date', 'Non-compliant products - expiration date too short'),
        ('improper_conservation', 'Non-compliant products - storage conditions (cold, etc.) not respected'),
        ('improper_promotional', 'Non-compliant products - promotional conditions'),
        ('error', 'Order error'),
        ('batch_recall', 'Batch recall by laboratory')
    ], 'Return reason', required=False)

    def create_returns(self):
        self.ensure_one()
        res = super(StockReturnPicking, self).create_returns()
        if res.get('res_id', False):
            picking = self.env['stock.picking'].browse(res.get('res_id'))
            if picking.picking_type_id.code == 'incoming':
                picking.write({'return_reason': self.return_reason})
        return res

    def _prepare_move_default_values(self, return_line, new_picking):
        res = super(StockReturnPicking, self)._prepare_move_default_values(return_line, new_picking)
        scrap_location = self._get_default_scrap_location_id()
        if res.get('location_dest_id', False) and return_line.product_id.is_medicine and scrap_location \
                and new_picking.picking_type_id.code == 'incoming':
            res['location_dest_id'] = scrap_location.id
        return res

    def _get_default_scrap_location_id(self):
        company = self.env.company
        return self.env['stock.location'].search([('scrap_location', '=', True), ('company_id', 'in', [company.id, False])], limit=1)
