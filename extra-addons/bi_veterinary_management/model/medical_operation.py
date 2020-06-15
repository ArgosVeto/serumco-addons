# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class medical_operation(models.Model):
    _name = 'medical.operation'

    procedure_id = fields.Many2one('medical.procedure',string='Code')
    notes = fields.Text(string='Notes')
    medical_surgery_id = fields.Many2one('medical.surgery','Surgery')

