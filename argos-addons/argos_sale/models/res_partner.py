# -*- coding: utf-8 -*-

from odoo import fields, models, api
import ast


class ResPartner(models.Model):
    _inherit = 'res.partner'

    consultation_ids = fields.Many2many('sale.order', compute='_compute_consultation_ids', string='Consultations')
    act_ids = fields.Many2many('sale.order.line', compute='_compute_act_ids', string='Acts')
    hospitalization_ids = fields.Many2many('sale.order.line', compute='_compute_hospitalization_ids', string='Hospitalizations', store=False)
    surgery_ids = fields.Many2many('sale.order.line', compute='_compute_surgery_ids',
                                           string='Surgeries')

    def _compute_consultation_ids(self):
        for rec in self:
            consultations = self.env['sale.order'].search([('is_consultation', '=', True), ('patient_id', '=', rec.id)])
            rec.consultation_ids = [(6, 0, consultations.ids)]

    @api.depends('consultation_ids', 'act_ids')
    def _compute_hospitalization_ids(self):
        for rec in self:
            hospitalization = self.env['sale.order.line'].search([('order_id.is_consultation', '=', True),
                                                                  ('product_id.act_type', '=', 'hospitalization'),
                                                                  ('order_id.patient_id', '=', rec.id)])
            rec.hospitalization_ids = [(6, 0, hospitalization.ids)]

    @api.depends('consultation_ids', 'act_ids')
    def _compute_surgery_ids(self):
        for rec in self:
            surgery = self.env['sale.order.line'].search([('order_id.is_consultation', '=', True),
                                                          ('product_id.act_type', '=', 'surgery'),
                                                          ('order_id.patient_id', '=', rec.id)])
            rec.surgery_ids = [(6, 0, surgery.ids)]

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

    def button_create_order(self):
        self.ensure_one()
        action = self.env.ref('sale.action_quotations_with_onboarding').read()[0]
        action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
        if self.owner_ids:
            action['context'] = ast.literal_eval(action['context'])
            action['context'].update({
                'default_partner_id': self.owner_ids[0].id,
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
