# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class PassportPassport(models.Model):
    _name = 'passport.passport'
    _description = 'Passport Passport'

    name = fields.Char('Passport')
    address = fields.Char('Address')
    city = fields.Char('City')
    delivery_date = fields.Date('Delivery date')
    species_id = fields.Many2one('res.partner.category', 'Species')
    identification = fields.Char('Identification')
    number = fields.Char('Number')
    status = fields.Char('Status')
    zip_code = fields.Char('Zip Code')
    patient_ids = fields.One2many('res.partner', 'passport_id', 'Patients')