# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    subscription_ids = fields.One2many('sale.subscription', 'patient_id', 'Subscriptions')
    patient_subscription_count = fields.Integer('Patient Subscription Count', compute='_compute_patient_subscription_count')

    @api.depends('subscription_ids')
    def _compute_patient_subscription_count(self):
        for rec in self:
            rec.patient_subscription_count = len(rec.subscription_ids)
