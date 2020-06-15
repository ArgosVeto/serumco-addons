# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date,datetime

class medical_inpatient_medication(models.Model):
    _name = 'medical.inpatient.medication'
    _rec_name = 'medical_medicament_id'

    medical_medicament_id = fields.Many2one('medical.medicament',string='Medicament',required=True)
    is_active = fields.Boolean(string='Active')
    start_treatment = fields.Datetime(string='Start Of Treatment',required=True)
    course_completed = fields.Boolean(string="Course Completed")
    doctor = fields.Many2one('medical.physician',string='Physician')
    indication = fields.Many2one('medical.pathology',string='Indication')
    end_treatment = fields.Datetime(string='End Of Treatment',required=True)
    discontinued = fields.Boolean(string='Discontinued')
    form = fields.Many2one('medical.drug.form',string='Form')
    route = fields.Many2one('medical.drug.route',string=" Administration Route ")
    dose = fields.Float(string='Dose')
    qty = fields.Integer(string='X')
    medical_dose_unit_id = fields.Many2one('medical.dose.unit',string='Dose Unit')
    duration = fields.Integer(string="Treatment Duration")
    duration_period = fields.Selection([('minutes','Minutes'),
                                        ('hours','hours'),
                                        ('days','Days'),
                                        ('months','Months'),
                                        ('years','Years'),
                                        ('indefine','Indefine')],string='Treatment Period')
    common_dosage = fields.Many2one('medical.medication.dosage',string='Frequency')
    admin_times = fields.Char(string='Admin Hours')
    frequency = fields.Integer(string='Frequency')
    frequency_unit = fields.Selection([('seconds','Seconds'),
                                       ('minutes','Minutes'),
                                       ('hours','hours'),
                                       ('days','Days'),
                                       ('weeks','Weeks'),
                                       ('wr','When Required')],string='Unit')
    adverse_reaction =fields.Text(string='Notes')
    medical_inpatient_registration_id = fields.Many2one('medical.inpatient.registration',string='Medication')
    admin_times_ids = fields.One2many('medical.inpatient.medication.admin.time','medical_inpatient_medicament_id',string='Admin')
    log_history_ids = fields.One2many('medical.inpatient.medication.log','medication_log_id',string='Log History')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s