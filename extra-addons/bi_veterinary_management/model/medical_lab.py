# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime
# classes under  menu of laboratry 

class medical_lab(models.Model):

    _name = 'medical.lab'
    _rec_name = 'medical_test_type_id'
    
    medical_test_type_id = fields.Many2one('medical.test_type', 'Test', required = True)
    name = fields.Char(string='ID')
    date_analysis =  fields.Datetime('Date of the Analysis', required = True , default = datetime.now())
    patient_id = fields.Many2one('medical.patient','Patient', required = True) 
    date_requested = fields.Datetime('Date requested', required = True, default = datetime.now())
    
    pathologist_id = fields.Many2one('medical.physician','Pathologist')
    requestor_physician_id = fields.Many2one('medical.physician','Physician', required = True)
    critearea_ids = fields.One2many('medical_test.critearea','medical_lab_id', 'Critearea')
    results= fields.Text('Results')
    diagnosis = fields.Text('Diagnosis')
    
    @api.model
    def create(self,val):
        val['name'] = self.env['ir.sequence'].next_by_code('ltest_seq')
        result = super(medical_lab,self).create(val)
        return result


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:    