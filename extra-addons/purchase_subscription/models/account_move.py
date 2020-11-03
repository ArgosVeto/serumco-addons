# -*- coding: utf-8 -*-
# © 2014 - 2017 Sudokeys (Nicolas Potier <nicolas.potier@sudokeys.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = 'account.move'

    subscription_id = fields.Many2one(
        'purchase.subscription', string="Purchase subscription")
