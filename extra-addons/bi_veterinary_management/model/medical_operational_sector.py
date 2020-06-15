# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class medical_operational_sector(models.Model):
    _name = 'medical.operational_sector'
    
    name = fields.Char(string="Name",required=True,size=128)
    info = fields.Text(string="Extra Info")
    operational_area_id = fields.Many2one('medical.operational_area',string="Operational Area")