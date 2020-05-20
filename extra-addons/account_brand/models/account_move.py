# Copyright (C) 2020 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'res.brand.mixin']

    brand_id = fields.Many2one(states={'open': [('readonly', True)], 'in_payment': [('readonly', True)], 'paid': [('readonly', True)],
                                       'cancel': [('readonly', True)]})


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    brand_id = fields.Many2one(related='move_id.brand_id', readonly=True, store=True)
