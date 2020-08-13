# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_dead = fields.Boolean('Dead')
    death_date = fields.Date('Death Date')
    death_reason = fields.Selection([('natural', 'Natural'), ('accidental', 'Accidental'), ('medical', 'Medical')],
                                    default='natural')
    is_missing = fields.Boolean('Missing')
    missing_date = fields.Date('Missing Date')
    race_id = fields.Many2one('res.partner.parameter', 'Race', domain=[('type', '=', 'race')])
    robe_id = fields.Many2one('res.partner.parameter', 'Robe', domain=[('type', '=', 'robe')])
    insurance_id = fields.Many2one('res.partner.parameter', 'Insurance', domain=[('type', '=', 'insurance')])
    origin_id = fields.Many2one('res.partner.parameter', 'Connection Origin', domain=[('type', '=', 'connection')])
    environment_ids = fields.Many2many('res.partner.parameter', 'res_partner_envirnment_rel', 'patient_id', 'environment_id',
                                       'Living Environment', domain=[('type', '=', 'living')])
    diet_ids = fields.Many2many('res.partner.parameter', 'res_partner_diet_rel', 'patient_id', 'diet_id', 'Recommended Diet',
                                domain=[('type', '=', 'diet')])
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
    veterinary_id = fields.Many2one('res.partner', 'Attending Veterinarian')
    pathology_ids = fields.Many2many('res.partner.pathology', string='Pathology')
    weight = fields.Float('Weight')
    owner_ids = fields.Many2many('res.partner', 'res_partner_owner_rel', 'partner_id', 'owner_id', string='Owners')
    contact_type = fields.Selection([('contact', 'Contact'), ('patient', 'Patient')], 'Contact Type', default='contact')
    patient_ids = fields.Many2many('res.partner', 'res_partner_patient_rel', 'partner_id', 'patient_id', string='Patients List')

    @api.model
    def _get_patient_by_name(self, name=False, category=False, customer_name=False, phone=False):
        partner = self._get_partner_by_name(customer_name, phone)
        category = self.env['res.partner.category'].search([('name', '=', category)], limit=1)
        patient = self.search([('name', '=', name),
                              ('category_id', 'in', category.ids),
                              ('owner_ids', 'in', partner.ids)], limit=1)
        if patient:
            return patient
        return self.create({'name': name, 'category_id': [(6, 0, category.ids)], 'owner_ids': [(6, 0, partner.ids)]})
