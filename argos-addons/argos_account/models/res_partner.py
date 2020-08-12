# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class ResPartner(models.Model):
    _inherit = 'res.partner'

    payment_mode = fields.Selection(
        [('transfer', 'Transfer'), ('cash', 'Cash'), ('check', 'Check')], 'Payment Mode')
    no_payment = fields.Boolean('Block payment')
