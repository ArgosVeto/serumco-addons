# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime

class medical_patient_cage(models.Model):
    
    _name = 'medical.patient.cage'
    
    @api.onchange('cage_c', 'cage_a', 'cage_g', 'cage_e')
    def get_score(self):
        for each in self:
            each.cage_score = int(each.cage_c)  + int(each.cage_a)  + int(each.cage_g) + int(each.cage_e)
         
    patient_id = fields.Many2one('medical.patient',string="Patient")
    evaluation_date = fields.Datetime(string="Evalution Date")
    cage_c = fields.Boolean(default  = False)
    cage_a = fields.Boolean(default  = False)
    cage_g = fields.Boolean(default  = False)
    cage_e = fields.Boolean(default  = False)
    cage_score = fields.Integer('Cage Score',  default = 0)


# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: