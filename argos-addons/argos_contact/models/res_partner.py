# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.addons.argos_base.models import tools
from dateutil.relativedelta import  relativedelta


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_dead = fields.Boolean('Dead')
    death_date = fields.Date('Death Date')
    death_reason = fields.Selection([('natural', 'Natural'), ('accidental', 'Accidental'), ('medical', 'Medical')], default='natural')
    is_missing = fields.Boolean('Missing')
    missing_date = fields.Date('Missing Date')
    race_id = fields.Many2one('res.partner.parameter', 'Race', domain=[('type', '=', 'race')])
    robe_id = fields.Many2one('res.partner.parameter', 'Robe', domain=[('type', '=', 'robe')])
    insurance_id = fields.Many2one('res.partner.parameter', 'Insurance', domain=[('type', '=', 'insurance')])
    origin_id = fields.Many2one('res.partner.parameter', 'Connection Origin', domain=[('type', '=', 'connection')])
    gender_id = fields.Many2one('res.partner.parameter', 'Gender', domain=[('type', '=', 'gender')])
    environment_ids = fields.Many2many('res.partner.parameter', 'res_partner_envirnment_rel', 'patient_id', 'environment_id',
                                       'Living Environment', domain=[('type', '=', 'living')])
    diet_ids = fields.Many2many('res.partner.parameter', 'res_partner_diet_rel', 'patient_id', 'diet_id', 'Recommended Diet',
                                domain=[('type', '=', 'diet')])
    is_sterilized = fields.Boolean('Sterilized')
    tattoo_number = fields.Char('Tattoo Number')
    tattoo_date = fields.Date('Tattoo Date')
    chip_identification = fields.Char('Chip Identification')
    issue_date = fields.Date('Issue Date')
    location = fields.Char('Location')
    tattoo_location = fields.Selection([('right_ear', 'Right Ear'), ('left_ear', 'Left Ear'), ('right_thigh', 'Right Thigh'),
                                        ('left_thigh', 'Left Thigh')], 'Tattoo Location')
    chip_date = fields.Date('Insertion Date')
    chip_location_id = fields.Many2one('res.partner.parameter', 'Chip Location', domain=[('type', '=', 'chip')])
    image = fields.Binary('Image')
    passport_id = fields.Many2one('passport.passport', 'Passport')
    pathology_ids = fields.Many2many('res.partner.pathology', 'res_partner_pathology_rel', 'partner_id', 'pathology_id', 'Pathologies')
    weight_ids = fields.One2many('res.partner.weight', 'partner_id', 'Weights')
    weight = fields.Float('Weight', compute='_compute_last_weight')
    owner_ids = fields.Many2many('res.partner', 'res_partner_patient_rel', 'patient_id', 'owner_id', 'Owners',
                                 domain="[('contact_type', '=', 'contact')]")
    contact_type = fields.Selection([('contact', 'Contact'), ('patient', 'Patient')], 'Contact Type', default='contact')
    patient_ids = fields.Many2many('res.partner', 'res_partner_patient_rel', 'owner_id', 'patient_id', 'Patients List',
                                   domain="[('contact_type', '=', 'patient')]")
    species_id = fields.Many2one('res.partner.category', 'Species', domain=[('type', '=', 'patient')])
    contact_category = fields.Selection([('person_patient', 'Person With Patient'), ('company_patient', 'Company With Patient'),
                                         ('person_no_patient', 'Person Without Patient'),
                                         ('company_no_patient', 'Company Without Patient')], 'Contact Category',
                                        default='company_no_patient', compute='_compute_contact_category', store=True)
    age_formatted = fields.Char('Age', compute='_compute_age_formatted')
    date_insurance_start = fields.Date('Date insurance start')
    date_insurance_end = fields.Date('Date insurance end')
    policy_insurance = fields.Char('Policy insurance')
    tag_ids = fields.Many2many('res.partner.parameter', 'res_partner_tag_rel', 'patient_id', 'tag_id', 'Tags', domain=[('type', '=', 'tag')])

    @api.depends('company_type', 'patient_ids')
    def _compute_contact_category(self):
        for record in self.filtered(lambda p: p.contact_type == 'contact'):
            if record.patient_ids:
                record.contact_category = 'company_patient' if record.company_type == 'company' else 'person_patient'
            else:
                record.contact_category = 'company_no_patient' if record.company_type == 'company' else 'person_no_patient'

    @api.model
    def _get_patient_by_name(self, name=False, category=False, customer_name=False, phone=False):
        partner = self._get_partner_by_name(customer_name, phone)
        category = self.env['res.partner.category'].search([('name', '=', category)], limit=1)
        patient = self.search([('name', '=', name),
                               ('contact_type', '=', 'patient'),
                               ('species_id', '=', category.id),
                               ('owner_ids', 'in', partner.ids)], limit=1)
        if patient:
            return patient
        return self.create({'name': name, 'contact_type': 'patient', 'species_id': category.id,
                            'owner_ids': [(6, 0, partner.ids)]})

    def write(self, vals):
        if vals.get('is_dead'):
            vals['active'] = False
        return super(ResPartner, self).write(vals)

    @api.depends("birthdate_date")
    def _compute_age_formatted(self):
        for rec in self:
            years, months, weeks = 0, 0, 0
            if rec.birthdate_date:
                relative_age = relativedelta(fields.Datetime.to_datetime(rec.birthdate_date), fields.Datetime.now())
                years = abs(relative_age.years)
                months = abs(relative_age.months)
                weeks = int(abs(relative_age.days) / 7)
            rec.age_formatted = str(years) + _(' years(s) ') + str(months) + _(' month(s) ') + str(weeks) + _(' week(s)')

    @api.depends('weight_ids')
    def _compute_last_weight(self):
        for rec in self:
            if rec.weight_ids:
                rec.weight = rec.weight_ids[0].values
            else:
                rec.weight = False