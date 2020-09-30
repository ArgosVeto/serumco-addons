# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleSubscription(models.Model):
    _inherit = 'sale.subscription'

    partner_id = fields.Many2one(
        domain="[('contact_type', '=', 'contact'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    patient_id = fields.Many2one('res.partner', 'Patient', domain="[('contact_type', '=', 'patient')]")
