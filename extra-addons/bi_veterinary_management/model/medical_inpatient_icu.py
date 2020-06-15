# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date,datetime

class medical_inpatient_icu(models.Model):
    _name = 'medical.inpatient.icu'
    
    name = fields.Many2one('medical.inpatient.registration',string="Registration Code",required=True)
    admitted =fields.Boolean(string="Admitted",required=True,default=True)
    icu_admission_date = fields.Datetime(string="ICU Admission",required=True)
    icu_stay = fields.Char(string="Duration",required=True,size=128)
    discharged_from_icu =fields.Boolean(string="Discharged")
    icu_discharge_date  = fields.Datetime(string='Discharge')
    medical_ventilation_history_ids = fields.One2many('medical.icu.ventilation','medical_inpatient_icu_id',string='MV History')
    
    def onchange_patient(self,name):
        inpatient_brw = self.env['medical.inpatient.registration'].browse(name)
        inpatient_name = inpatient_brw.name
        
        inpatient_icu_obj = self.env['medical.inpatient.icu']
        inpatient_icu_ids = inpatient_icu_obj.search([('name.name','=',inpatient_name)])
        if len(inpatient_icu_ids) > 1:
            raise UserError(_('Our records indicate that the patient is already admitted at ICU. '))
         
    def onchange_with_descharge(self,admitted,discharged_from_icu):
        res = {}
        if discharged_from_icu == True:
            res.update({'admitted':False})
        else:
            res.update({'admitted':True})
        return {'value':res}
    
    def onchange_with_admitted(self,admitted,discharged_from_icu):
        res = {}
        if admitted == True:
            res.update({'discharged_from_icu':False})
        else:
            res.update({'discharged_from_icu':True})
        return {'value':res}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s