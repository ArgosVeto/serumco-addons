# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class medical_genetic_risk(models.Model):
    _name = 'medical.genetic.risk'
    _rec_name = 'patient_id'

    patient_id = fields.Many2one('medical.patient',string="Patient")
    disease_gene_id = fields.Many2one('medical.disease.gene',string="Disease Gene")    
