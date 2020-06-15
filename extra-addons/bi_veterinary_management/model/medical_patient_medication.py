# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class medical_patient_medication(models.Model):
    _name = 'medical.patient.medication'
    _rec_name = 'medical_medicament_id'

    medical_medicament_id = fields.Many2one('medical.medicament', 'Medicament' )
    new_born_id =  fields.Many2one('medical.newborn', 'New Born')
    course_completed = fields.Boolean('Course Completed')
    patient_id = fields.Many2one('medical.patient','Physician')
    medicament_id = fields.Many2one('medical.medicament',string='Medicament',required=True)
    medical_patient_medication_id = fields.Many2one('medical.patient',string='Medication')
    is_active = fields.Boolean(string='Active', default = True)
    start_treatment = fields.Datetime(string='Start Of Treatment',required=True)
    course_completed = fields.Boolean(string="Course Completed")
    doctor_id = fields.Many2one('medical.physician',string='Physician')
    indication_pathology_id = fields.Many2one('medical.pathology',string='Indication')
    end_treatment = fields.Datetime(string='End Of Treatment',required=True)
    discontinued = fields.Boolean(string='Discontinued')
    medical_drug_form_id = fields.Many2one('medical.drug.form',string='Form')
    medical_drug_route_id = fields.Many2one('medical.drug.route',string=" Administration Route ")
    dose = fields.Float(string='Dose')
    qty = fields.Integer(string='X')
    dose_unit_id = fields.Many2one('medical.dose.unit',string='Dose Unit')
    duration = fields.Integer(string="Treatment Duration")
    duration_period = fields.Selection([('minutes','Minutes'),
                                        ('hours','hours'),
                                        ('days','Days'),
                                        ('months','Months'),
                                        ('years','Years'),
                                        ('indefine','Indefine')],string='Treatment Period')
    medication_dosage_id = fields.Many2one('medical.medication.dosage',string='Frequency')
    admin_times = fields.Char(string='Admin Hours')
    frequency = fields.Integer(string='Frequency')
    frequency_unit = fields.Selection([('seconds','Seconds'),
                                       ('minutes','Minutes'),
                                       ('hours','hours'),
                                       ('days','Days'),
                                       ('weeks','Weeks'),
                                       ('wr','When Required')],string='Unit')
    notes =fields.Text(string='Notes')

