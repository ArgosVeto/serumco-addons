# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PassportPassport(models.Model):
    _name = 'passport.passport'
    _description = 'Passport Passport'

    name = fields.Char('Passport')
    address = fields.Char('Address', compute='_compute_patient_info')
    city = fields.Char('City')
    delivery_date = fields.Date('Delivery date')
    species_id = fields.Many2one('res.partner.category', 'Species', compute='_compute_patient_info')
    identification = fields.Char('Identification')
    number = fields.Char('Number')
    status = fields.Selection([('available', 'Available'), ('delivered', 'Delivered'), ('destroyed', 'Destroyed')],
                              'Status', default='available')
    zip_code = fields.Char('Zip Code')
    gmvet_id = fields.Char('Gmvet ID')
    patient_ids = fields.One2many('res.partner', 'passport_id', 'Patients')
    patient_name = fields.Char('Patient Name', compute='_compute_patient_info')
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')

    @api.depends('patient_ids', 'patient_ids.name', 'patient_ids.species_id', 'patient_ids.owner_ids',
                 'patient_ids.owner_ids.contact_address')
    def _compute_patient_info(self):
        for rec in self:
            if rec.status != 'available' and rec.patient_ids:
                patient = rec.patient_ids.sorted(key=lambda p: p.issue_date, reverse=True)[0]
                rec.patient_name = patient.name
                rec.species_id = patient.species_id
                if patient.owner_ids:
                    rec.address = patient.owner_ids[0].contact_address
                else:
                    rec.address = False
            else:
                rec.address, rec.species_id, rec.patient_name = False, False, False