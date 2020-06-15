# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime

class medical_patient_pap_history(models.Model):

    _name = 'medical.patient.pap.history'
    
    patient_id = fields.Many2one('medical.patient', 'Patient')
    evolution_id = fields.Many2one('medical.patient.evaluation', 'Evaluation')
    evolution_date =fields.Datetime('Evaluation Date')
    result = fields.Selection([('negative','Negative'),
                               ('asc_us','ASC-US'),
                               ('asc_h','ASC-H'),
                               ('asg','ASG'),
                               ('lsil','LSIL'),
                               ('hisl','HISL'),
                               ('ais','AIS')], 'Result')
    remark = fields.Char('Remark')

# vim=expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: