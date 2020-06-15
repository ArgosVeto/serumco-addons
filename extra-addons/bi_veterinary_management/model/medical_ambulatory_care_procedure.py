# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class medical_ambulatory_care_procedure(models.Model):
    _name = 'medical.ambulatory_care_procedure'

    code_id = fields.Many2one('medical.procedure',string="Code",required=True)   
    notes = fields.Text(string="Notes") 
    medical_patient_ambulatory_care_procedure_id = fields.Many2one('medical.patient.ambulatory_care',string="Procedure")