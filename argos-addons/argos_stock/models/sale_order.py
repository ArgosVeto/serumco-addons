# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    prescription_count = fields.Integer('Prescription', compute='_compute_prescription_count')
    is_duplicate = fields.Boolean('Is Duplicate')

    def button_view_prescription(self):
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Delivery'),
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
        return self.env.ref('argos_stock.action_print_prescription').report_action(self)

    def make_duplicate(self):
        self.ensure_one()
        self.is_duplicate = True
        return True

    def button_prescription_send(self):
        self.ensure_one()
        template = self.env.ref('argos_stock.mail_template_prescription_send')
        lang = self._context.get('lang')
        if template.lang:
            lang = template._render_template(template.lang, 'sale.order', self.id)
        context = {
            'default_model': 'sale.order',
            'default_res_id': self.id,
            'default_use_template': bool(template.id),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'proforma': self._context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': context,
        }

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit(self):
        type_obj = self.env['stock.picking.type']
        types = type_obj.search(
            [('code', '=', 'outgoing'), ('warehouse_id.operating_unit_id', '=', self.operating_unit_id.id)]
        )
        if not types:
            raise ValidationError(_('This operating unit has no configured warehouse.'))
        self.warehouse_id = types[:1].warehouse_id.id
