# -*- coding: utf-8 -*-

from odoo import api, fields, models
import math


class ResPartnerWeight(models.Model):
    _name = 'res.partner.weight'
    _description = 'Patient Weight'
    _order = 'date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name')
    date = fields.Date('Date')
    values = fields.Float('Values')
    source = fields.Char('Source')
    note = fields.Char('Notes')
    partner_id = fields.Many2one('res.partner', 'Patient', ondelete='cascade')
    score = fields.Selection(
        [('1_9', '1/9'), ('2_9', '2/9'), ('3_9', '3/9'), ('4_9', '4/9'), ('5_9', '5/9'), ('6_9', '6/9'), ('7_9', '7/9'),
         ('8_9', '8/9'), ('9_9', '9/9')], 'Score')
    area = fields.Float('Area', compute='_compute_area')
    nec = fields.Float('Nec', compute='_compute_nec', store=True)

    @api.depends('values')
    def _compute_area(self):
        for rec in self:
            if rec.values:
                rec.area = math.pow(rec.values, (2/3)) * 0.101
            else:
                rec.area = False

    @api.depends('score')
    def _compute_nec(self):
        for rec in self:
            if rec.score:
                score = dict(self._fields['score'].selection).get(rec.score)
                rec.nec = eval(score)
            else:
                rec.nec = 0.0