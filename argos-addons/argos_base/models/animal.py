# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools
from datetime import datetime


class Animal(models.Model):
    _name = "animal.animal"
    _description = "Animal"

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
    is_dead = fields.Boolean('Dead')
    death_date = fields.Date('Death Date')
    death_reason = fields.Selection([('natural', 'Natural'), ('accidental', 'Accidental'), ('medical', 'Medical')],
                                    default='natural')
    is_missing = fields.Boolean('Missing')
    missing_date = fields.Date('Missing Date')
    category_id = fields.Many2one('animal.category', 'Species')
    race_id = fields.Many2one('animal.race', 'Race')
    sex = fields.Selection([('male', 'Male'), ('female', 'Female')], 'Sex')
    robe_id = fields.Many2one('animal.robe', 'Robe')
    birth_date = fields.Date('Birth Date')
    age = fields.Float('Age')
    is_sterilized = fields.Boolean('Sterilized')
    is_reproductive = fields.Boolean('Reproductive')
    is_dangerous = fields.Boolean('Dangerous')
    tattoo_date = fields.Date('Tattoo Date')
    tattoo_location = fields.Char('Tattoo Location')
    chip_identification = fields.Char('Chip Identification')
    chip_date = fields.Date('Insertion Date')
    chip_location = fields.Char('Chip Location')
    image = fields.Binary('Image')
    passport = fields.Char('Passport')
    issue_date = fields.Date('Issue Date')
    location = fields.Char('Location')
    clinic_id = fields.Many2one('res.partner', 'Main Clinic')
    veterinary_id = fields.Many2one('res.partner', 'Attending Veterinarian')
    insurance_id = fields.Many2one('animal.insurance', 'Insurance')
    environment_ids = fields.Many2many('living.environment', string='Living Environment')
    diet_ids = fields.Many2many('animal.diet', string='Recommended Diet')
    pathology_ids = fields.Many2many('animal.pathology', string='Pathology')
    phone = fields.Char('Phone')
    email = fields.Char('Email')
    note = fields.Text('Notes')
    owner_ids = fields.Many2many('res.partner', string='Owners')

    @api.model
    def _get_animal_by_name(self, name=False, category=False, customer_name=False, phone=False):
        partner = self.env['res.partner']._get_partner_by_name(customer_name, phone)
        category = self.env['animal.category']._get_animal_category(category)
        animal = self.search([('name', '=', name), ('category_id', '=', category.id), ('partner_id', '=', partner.id)],
                             limit=1)
        if animal:
            return animal
        return self.create({'name': name, 'category_id': category.id, 'partner_id': partner.id})
