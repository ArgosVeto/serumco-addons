# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools
import urllib.parse as urlparse
from datetime import datetime


class Animal(models.Model):
    _name = "animal.animal"
    _description = "Animal"

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
    partner_id = fields.Many2one('res.partner', 'Main Owner')
    is_dead = fields.Boolean('Dead')
    death_date = fields.Date('Death Date')
    death_reason = fields.Selection([('natural', 'Natural'), ('accidental', 'Accidental'), ('medical', 'Medical')])
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
    family_id = fields.Many2one('family.family', string='Family')
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
    conv_key = fields.Char('Convention Key')

    @api.model
    def _get_animal_by_name(self, name=False, category=False, customer_name=False, phone=False):
        partner = self.env['res.partner']._get_partner_by_name(customer_name, phone)
        category = self.env['animal.category']._get_animal_category(category)
        animal = self.search([('name', '=', name), ('category_id', '=', category.id), ('partner_id', '=', partner.id)],
                             limit=1)
        if animal:
            return animal
        return self.create({'name': name, 'category_id': category.id, 'partner_id': partner.id})

    @api.model
    def parse_url(self, url='', params={}):
        url_parse = urlparse.urlparse(url)
        query = url_parse.query
        url_dict = dict(urlparse.parse_qsl(query))
        url_dict.update(params)
        url_new_query = urlparse.urlencode(url_dict)
        url_parse = url_parse._replace(query=url_new_query)
        new_url = urlparse.urlunparse(url_parse)
        return new_url

    def edit_convention(self):
        self.ensure_one()
        url = 'https://convention.incineris.fr/convention.php'
        params = {
            'action': 'create',
            'soft_id': 'SOFTID',
            'conv_key': self.conv_key,
            'pet_name': self.name,
        }
        if self.partner_id:
            params['soft_owner_id'] = self.partner_id.id
            partner_id = self.partner_id
            if partner_id.last_name:
                params['owner_lastname'] = partner_id.last_name
            if partner_id.first_name:
                params['owner_firstname'] = partner_id.first_name
            if partner_id.street:
                params['owner_address'] = partner_id. street
            if partner_id.city:
                params['owner_city'] = partner_id.city
            if partner_id.zip:
                params['owner_zipcode'] = partner_id.zip
            if partner_id.country_id:
                params['owner_country'] = partner_id.country_id.name
            if partner_id.phone:
                params['owner_phone'] = partner_id.phone
            if partner_id.mobile:
                params['owner_mobile'] = partner_id.mobile
            if partner_id.email:
                params['email'] = partner_id.email
        if self.birth_date:
            params['pet_birth_date'] = datetime.strftime(self.birth_date, '%d/%m/%Y')
        if self.death_date:
            params['pet_death_date'] = datetime.strftime(self.death_date, '%d/%m/%Y')
        if self.race_id:
            params['pet_breed'] = self.race_id.name
        if self.birth_date:
            params['pet_birth_date'] = self.birth_date
        if self.chip_identification:
            params['pet_identification'] = self.chip_identification
        if self.clinic_id:
            params['soft_clinic_id'] = self.clinic_id.id
        if self.veterinary_id:
            params['vet_name'] = self.veterinary_id.name
            params['soft_vet_id'] = self.veterinary_id.id
        if self.death_reason:
            params['pet_death_reason'] = self.death_reason
        new_url = self.parse_url(url, params)

        return {
            'type': 'ir.actions.act_url',
            'url': new_url,
            'target': 'new',
        }

    def reprint_convention(self):
        self.ensure_one()
        url = 'https://convention.incineris.fr/convention.php'
        params = {
            'action': 'reprint',
            'soft_id': 'SOFTID',
            'conv_key': self.conv_key,
        }
        new_url = self.parse_url(url, params)
        return {
            'type': 'ir.actions.act_url',
            'url': new_url,
            'target': 'new',
        }

    def delete_convention(self):
        self.ensure_one()
        url = 'https://convention.incineris.fr/convention.php'
        params = {
            'action': 'delete',
            'soft_id': 'SOFTID',
            'conv_key': self.conv_key,
        }
        new_url = self.parse_url(url, params)
        return {
            'type': 'ir.actions.act_url',
            'url': new_url,
            'target': 'new',
        }

