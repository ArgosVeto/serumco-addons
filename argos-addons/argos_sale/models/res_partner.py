# -*- coding: utf-8 -*-

from odoo import fields, models
import ast


class ResPartner(models.Model):
    _inherit = 'res.partner'

    consultation_ids = fields.Many2many('sale.order', compute='_compute_consultation_ids', string='Consultations')
    act_ids = fields.Many2many('sale.order.line', compute='_compute_act_ids', string='Acts')

    def _compute_consultation_ids(self):
        for rec in self:
            consultations = self.env['sale.order'].search([('is_consultation', '=', True), ('patient_id', '=', rec.id)])
            rec.consultation_ids = [(6, 0, consultations.ids)]

    def _compute_act_ids(self):
        for rec in self:
            acts = self.env['sale.order.line'].search([('order_id.is_consultation', '=', True), ('product_id.act_type', '!=', 'undefined'),
                                                       ('order_id.patient_id', '=', rec.id)])
            rec.act_ids = [(6, 0, acts.ids)]

    def button_create_consultation(self):
        self.ensure_one()
        action = self.env.ref('argos_sale.action_consultations').read()[0]
        action['views'] = [(self.env.ref('argos_sale.consultation_view_order_form').id, 'form')]
        action['context'] = ast.literal_eval(action['context'])
        action['context'].update({
            'default_patient_id': self.id,
            'default_employee_id': self.employee_id.id,
            'default_is_consultation': True,
        })
        return action

    def action_open_orders(self):
        self.ensure_one()
        action = self.env.ref('argos_sale.action_open_sales').read()[0]
        if self.contact_type == 'contact':
            action['domain'] = [('partner_id', '=', self.id)]
        else:
            action['domain'] = [('patient_id', '=', self.id)]
        return action
