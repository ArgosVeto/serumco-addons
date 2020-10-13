# -*- coding: utf-8 -*-

from odoo import models, fields, api
import ast


class PlanningSlot(models.Model):
    _inherit = 'planning.slot'

    order_ids = fields.One2many('sale.order', 'slot_id', 'Consultations')
    order_count = fields.Integer(compute='_compute_order_count')
    invoice_count = fields.Integer('Invoice count', compute='_compute_invoice_count')

    @api.depends('order_ids')
    def _compute_order_count(self):
        for rec in self:
            rec.order_count = len(rec.order_ids)

    @api.depends('order_ids.invoice_count')
    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = sum([order.invoice_count for order in rec.order_ids])

    def action_view_orders(self):
        self.ensure_one()
        action = self.env.ref('argos_sale.action_consultations').read()[0]
        action['domain'] = [('slot_id', '=', self.id)]
        action['context'] = ast.literal_eval(action['context'])
        action['context'].update({
            'default_slot_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_patient_id': self.patient_id.id,
            'default_employee_id': self.employee_id.id,
            'default_is_consultation': True,
            'default_consultation_type_id': self.consultation_type_id.id,
            'default_operating_unit_id': self.operating_unit_id.id,
        })
        return action

