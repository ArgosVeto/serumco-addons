# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime

class medical_vaccination(models.Model):
    _name = 'medical.vaccination'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product',string='Name',required=True)
    institution_id = fields.Many2one('res.partner',string='Institution')
    next_dose_date = fields.Datetime(string='Next Dose')
    vaccine_expiration_date = fields.Datetime(string='Expiration Date',required=True)
    observations = fields.Char(string='Observations')
    dose = fields.Integer(string='Dose Number',required=True)
    date = fields.Datetime(string='Date' ,required=True)
    vaccine_lot = fields.Char(string='Lot Number')
    medical_patient_vaccines_id = fields.Many2one('medical.patient',string='Vaccination')