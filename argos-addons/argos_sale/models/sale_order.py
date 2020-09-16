# -*- coding: utf-8 -*-

import csv
import io

from odoo import api, fields, models, _
import urllib.parse as urlparse
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_patient_ids = fields.Many2many(related='partner_id.patient_ids', string='Patient List')
    argos_state = fields.Selection([('in_progress', 'In progress'), ('consultation_done', 'Done')])
    partner_id = fields.Many2one(
        domain="[('contact_type', '=', 'contact'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    patient_id = fields.Many2one('res.partner', 'Patient', domain="[('contact_type', '=', 'patient')]")
    species_id = fields.Many2one(related='patient_id.species_id')
    race_id = fields.Many2one(related='patient_id.race_id')
    gender_id = fields.Many2one(related='patient_id.gender_id')
    age = fields.Integer('Age', related='patient_id.age')
    weight = fields.Float('Weight', related='patient_id.weight')
    pathology_ids = fields.Many2many('res.partner.pathology', related='patient_id.pathology_ids')
    employee_id = fields.Many2one('hr.employee')
    is_consultation = fields.Boolean('Is Consultation')
    conv_key = fields.Char('Convention Key', compute='_compute_conv_key')
    consultation_date = fields.Date('Consultation Date', default=lambda self: fields.Date.today())
    consultation_type_id = fields.Many2one('consultation.type', domain=[('is_canvas', '=', False)])
    observation = fields.Text('Observations')
    customer_observation = fields.Text('Customer Observation')
    referent_partner_id = fields.Many2one('res.partner')
    diagnostic_ids = fields.Many2many('documents.tag', 'sale_order_diagnostic_tag_rel', 'sale_order_id',
                                      'diagnostic_id')
    hypothese_ids = fields.Many2many('documents.tag', 'sale_order_hypothese_tag_rel', 'sale_order_id', 'hypothese_id')
    canvas_id = fields.Many2one('consultation.type', domain=[('is_canvas', '=', True)])
    arrival_time = fields.Datetime('Arrival Time', track_visibility='onchange')
    pickup_time = fields.Datetime('Pick-up Time', track_visibility='onchange')

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

    @api.depends('employee_id', 'partner_id', 'patient_id')
    def _compute_conv_key(self):
        soft_id = self.env['ir.config_parameter'].get_param("incineris.soft_id")
        editor_id = soft_id or ''
        for rec in self:
            vet_id = str(rec.employee_id.id)
            owner_id = str(rec.partner_id.id)
            patient_id = str(rec.patient_id.id)
            timestamp = str(fields.Datetime.now())
            rec.conv_key = '-'.join([editor_id, vet_id, owner_id, patient_id, timestamp])

    def action_edit_incineris(self):
        self.ensure_one()
        if not self.is_consultation:
            raise UserError(_('Only consultation can generate incineris convention.'))
        url = self.env['ir.config_parameter'].get_param("incineris_url") or ''
        soft_id = self.env['ir.config_parameter'].get_param("incineris.soft_id")
        species = self.patient_id.species_id and self.patient_id.species_id.is_incineris_species and \
                  self.patient_id.species_id.name or 'nac'
        params = {
            'action': 'create',
            'soft_id': soft_id or '',
            'conv_key': self.conv_key or '',
            'soft_owner_id': self.partner_id.id or '',
            'owner_lastname': self.partner_id.lastname or '',
            'owner_firstname': self.partner_id.firstname or '',
            'owner_address': self.partner_id.street or '',
            'owner_city': self.partner_id.city or '',
            'owner_zipcode': self.partner_id.zip or '',
            'owner_phone': self.partner_id.phone or '',
            'owner_mobile': self.partner_id.mobile or '',
            'email': self.partner_id.email or '',
            'owner_country': self.partner_id.country_id.name or '',
            'owner_civility': self.partner_id.title.shortcut or '',
            'soft_clinic_id': self.operating_unit_id.id or '',
            'vet_name': self.employee_id.name or '',
            'soft_vet_id': self.employee_id.id or '',
            'pet_name': self.patient_id.name or '',
            'pet_species': species.lower(),
            'pet_birth_date': fields.Date.from_string(self.patient_id.birthdate_date).strftime(
                "%d/%m/%Y") if self.patient_id.birthdate_date else '',
            'pet_death_date': fields.Date.from_string(self.patient_id.death_date).strftime(
                "%d/%m/%Y") if self.patient_id.death_date else '',
            'pet_breed': self.patient_id.race_id.name or '',
            'pet_identification': self.patient_id.chip_identification or '',
            'pet_death_reason': self.patient_id.death_reason or '',
        }
        new_url = self.parse_url(url, params)
        return {
            'type': 'ir.actions.act_url',
            'url': new_url,
            'target': 'new',
        }

    def reprint_convention(self):
        self.ensure_one()
        if not self.is_consultation:
            raise UserError(_('Only consultation can generate incineris convention.'))
        if not self.conv_key:
            raise ValidationError(_('Please generate convention first'))
        url = self.env['ir.config_parameter'].get_param("incineris_url") or ''
        soft_id = self.env['ir.config_parameter'].get_param("incineris.soft_id")
        params = {
            'action': 'reprint',
            'soft_id': soft_id,
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
        if not self.is_consultation:
            raise UserError(_('Only consultation can generate incineris convention.'))
        if not self.conv_key:
            raise ValidationError(_('Please generate convention first'))
        url = self.env['ir.config_parameter'].get_param("incineris_url") or ''
        soft_id = self.env['ir.config_parameter'].get_param("incineris.soft_id")
        params = {
            'action': 'delete',
            'soft_id': soft_id,
            'conv_key': self.conv_key,
        }
        new_url = self.parse_url(url, params)
        return {
            'type': 'ir.actions.act_url',
            'url': new_url,
            'target': 'new',
        }

    def send_notification_mail(self):
        self.ensure_one()
        try:
            email_template = self.env.ref('argos_sale.sale_notification_mail_template')
            email_template.send_mail(self.id, force_send=True, raise_exception=True)
        except Exception as e:
            _logger.error(repr(e))

    @api.model
    def create(self, vals):
        vals['arrival_time'] = fields.Datetime.now()
        res = super(SaleOrder, self).create(vals)
        if res.partner_id and res.partner_id.has_tutor_curator:
            res.send_notification_mail()
        return res

    @api.onchange('canvas_id')
    def onchange_canvas_id(self):
        self.observation = self.canvas_id.chapters or ''

    def action_create_invoice(self):
        self.ensure_one
        self.write({
            'pickup_time': fields.Datetime.now(),
            'argos_state': 'consultation_done'
        })
        return self.env.ref('sale.action_view_sale_advance_payment_inv').read()[0]
