# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class ResPartner(models.Model):
    _inherit = 'res.partner'

    payment_mode = fields.Selection(
        [('transfer', 'Transfer'), ('cash', 'Cash'), ('check', 'Check')], 'Payment Mode')
    no_payment = fields.Boolean('Block payment')
    payment_method_ids = fields.Many2many('account.payment.method', 'res_partner_payment_method_rel', 'partner_id',
                                          'method_id', 'Payment Methods')
