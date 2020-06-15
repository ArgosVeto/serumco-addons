# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date,datetime


class medical_inpatient_registration(models.Model):
    _name = 'medical.inpatient.registration'

    name = fields.Char(string="Registration Code", copy=False, readonly=True, index=True)
    patient_id = fields.Many2one('medical.patient',string="Patient",required=True)
    bed_id = fields.Many2one('medical.hospital.bed',string="Hospital Bed")
    hospitalization_date = fields.Datetime(string="Hospitalization date",required=True)
    discharge_date = fields.Datetime(string="Expected Discharge date",required=True)
    attending_physician_id = fields.Many2one('medical.physician',string="Attending Physician")
    operating_physician_id = fields.Many2one('medical.physician',string="Operating Physician")
    admission_type = fields.Selection([('routine','Routine'),('maternity','Maternity'),('elective','Elective'),('urgent','Urgent'),('emergency','Emergency  ')],required=True,string="Admission Type")
    admission_reason_id = fields.Many2one('medical.pathology',string="Reason for Admission")
    info = fields.Text(string="Extra Info")
    bed_transfers_ids = fields.One2many('bed.transfer','inpatient_id',string='Transfer Bed',readonly=True)
    diet_belief_id = fields.Many2one('medical.diet.belief',string='Belief')
    therapeutic_diets_ids = fields.One2many('medical.inpatient.diet','inpatient_id',string='Therapeutic_diets')
    diet_vegetarian = fields.Selection([('none','None'),('vegetarian','Vegetarian'),('lacto','Lacto Vegetarian'),('lactoovo','Lacto-Ovo-Vegetarian'),('pescetarian','Pescetarian'),('vegan','Vegan')],string="Vegetarian")
    nutrition_notes = fields.Text(string="Nutrition notes / Directions")
    state = fields.Selection([('free','Free'),('confirmed','Confirmed'),('hospitalized','Hospitalized'),('done','Done'),('cancel','Cancel')],string="State",default="free")
    nursing_plan = fields.Text(string="Nursing Plan")
    discharge_plan = fields.Text(string="Discharge Plan")
    icu = fields.Boolean(string="ICU")
    medication_ids = fields.One2many('medical.inpatient.medication','medical_medicament_id',string='Medication')
    icu_admissions_ids = fields.One2many('medical.inpatient.icu','name',string='ICU Ids',readonly=True)
    
    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('medical.inpatient.registration') or 'INPAC'
        result = super(medical_inpatient_registration, self).create(vals)
        return result
    
    def registration_confirm(self):
        self.write({'state': 'confirmed'})

    def registration_admission(self):
        self.write({'state': 'hospitalized'})

    def registration_cancel(self):
        self.write({'state': 'cancel'})
        self.bed_id.write({'state':'free'})

    def patient_discharge(self):
        self.write({'state': 'done'}
                   )
        self.bed_id.write({'state':'free'})


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
