# -*- coding: utf-8 -*-

import csv
import io

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    prescription_count = fields.Integer('Prescription', compute='_compute_prescription_count')

    def button_view_prescription(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Prescriptions'),
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'views': [(self.env.ref('argos_stock.prescription_argos_form_view').id, 'form')],
            'context': {},
        }
        pickings = self.picking_ids.filtered(lambda p: p.is_arg_prescription)
        if len(pickings) > 1:
            action['domain'] = [('id', 'in', pickings.ids)]
            action['view_mode'] = 'tree,form'
            action['views'] = [(False, 'tree')] + action['views']
        elif pickings:
            action['res_id'] = pickings.id
        return action

    @api.depends('picking_ids', 'picking_ids.is_arg_prescription')
    def _compute_prescription_count(self):
        for order in self:
            order.prescription_count = len(order.picking_ids.filtered(lambda sp: sp.is_arg_prescription))

