# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class ResPartnerWeight(models.Model):
    _name = 'res.partner.weight'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('Name')
    date = fields.Date('Date')
    values = fields.Float('Values')
    source = fields.Char('Source')
    note = fields.Char('Notes')
    patient_id = fields.Many2one('res.partner', 'Patient')