# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    prescription_count = fields.Integer('Prescription', compute='_compute_prescription_count')
    is_delivered = fields.Boolean('Is Delivered', compute='_compute_is_delivered')

    @api.depends('picking_ids', 'picking_ids.state')
    def _compute_is_delivered(self):
        for rec in self:
            rec.is_delivered = not bool(rec.picking_ids.filtered(lambda pick: pick.state not in ['done', 'cancel']))

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

    def button_print_picking(self):
        self.ensure_one()
        pickings = self.picking_ids.filtered(lambda pick: pick.state not in ['done', 'cancel'])
        pickings.action_assign()
        move_lines = pickings.move_line_ids
        action = self.env.ref('argos_stock.action_print_picking').read()[0]
        if move_lines:
            action['context'] = {
                'default_move_line_ids': move_lines.ids,
                'default_picking_id': move_lines[0].picking_id.id,
            }
        return action
