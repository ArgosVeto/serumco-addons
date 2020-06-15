# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date,datetime

class medical_inpatient_medication_log(models.Model):
    _name = 'medical.inpatient.medication.log'
    
    admin_time = fields.Datetime(string='Date',readonly=True)
    dose = fields.Float(string='Dose')
    remarks = fields.Text(string='Remarks')
    health_professional_id = fields.Many2one('medical.physician',string='Health Professional',readonly=True)
    dose_unit = fields.Many2one('medical.dose.unit',string='Dose Unt')
    medication_log_id = fields.Many2one('medical.inpatient.medication',string='Log History')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s