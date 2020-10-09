# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockPickingPrint(models.TransientModel):
    _name = 'stock.picking.print'
    _description = 'Stock Picking Print'

    picking_id = fields.Many2one('stock.picking', 'Picking')
    move_line_ids = fields.Many2many('stock.move.line', 'picking_move_line_rel', 'picking_id', 'move_line_id',
                                     'Stock Move Lines')

    def button_validate(self):
        self.ensure_one()
        picking = self.picking_id
        res = picking.button_validate()
        if res and res.get('res_model') == 'stock.backorder.confirmation':
            backorder = self.env['stock.backorder.confirmation'].browse(res.get('res_id'))
            backorder.with_context(default_move_line_ids=False, default_picking_id=False).process()
        else:
            picking.action_done()
        action = self.env.ref('argos_stock.action_print_precription').report_action(picking)
        action['close_on_report_download'] = True
        return action
