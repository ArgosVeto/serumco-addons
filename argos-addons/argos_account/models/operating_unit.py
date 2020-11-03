# -*- coding: utf-8 -*-

from odoo import fields, models


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    payment_method_ids = fields.Many2many(related='partner_id.payment_method_ids', inherited=True, readonly=False)