# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import urllib.parse as urlparse
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    name = fields.Char(readonly=False)
    partner_animal_ids = fields.Many2many(related='partner_id.animal_ids')
    argos_state = fields.Selection([('in_progress', 'In progress'), ('consultation_done', 'Done')])
    animal_id = fields.Many2one('res.partner', 'Animal')
    category_id = fields.Many2many(related='animal_id.category_id')
    sex = fields.Selection(related='animal_id.gender', string='Sex')
    age = fields.Integer('Age', related='animal_id.age')
    weight = fields.Float('Weight', related='animal_id.weight')
    pathology_ids = fields.Many2many('res.partner.pathology')
    veterinary_id = fields.Many2one('hr.employee')
    is_consultation = fields.Boolean('Is Consultation')
    conv_key = fields.Char('Convention Key', compute='_compute_conv_key')
    consultation_date = fields.Date(default=fields.Date.today(), string='Consultation Date')
    consultation_type = fields.Many2one('consultation.type')
    observation = fields.Text('Observations')
    customer_observation = fields.Text('Customer Observation')
    referent_partner_id = fields.Many2one('res.partner')
    diagnostic_ids = fields.Many2many('documents.tag', 'sale_order_diagnostic_tag_rel', 'sale_order_id',
                                      'diagnostic_id')
    hypothese_ids = fields.Many2many('documents.tag', 'sale_order_hypothese_tag_rel', 'sale_order_id', 'hypothese_id')

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

    @api.depends('veterinary_id', 'partner_id', 'animal_id')
    def _compute_conv_key(self):
        soft_id = self.env['ir.config_parameter'].get_param("incineris.soft_id")
        editor_id = soft_id or ''
        for rec in self:
            vet_id = str(rec.veterinary_id.id)
            owner_id = str(rec.partner_id.id)
            animal_id = str(rec.animal_id.id)
            timestamp = str(fields.Datetime.now())
            rec.conv_key = '-'.join([editor_id, vet_id, owner_id, animal_id, timestamp])

    def action_edit_incineris(self):
        self.ensure_one()
        if not self.is_consultation:
            raise UserError(_('Only consultation can generate incineris convention.'))
        url = self.env['ir.config_parameter'].get_param("incineris_url") or ''
        soft_id = self.env['ir.config_parameter'].get_param("incineris.soft_id")
        species = self.animal_id.category_id.is_incineris_species and self.animal_id.category_id.name or 'nac'
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
            'vet_name': self.veterinary_id.name or '',
            'soft_vet_id': self.veterinary_id.id or '',
            'pet_name': self.animal_id.name or '',
            'pet_species': species.lower(),
            'pet_birth_date': fields.Date.from_string(self.animal_id.birth_date).strftime(
                "%d/%m/%Y") if self.animal_id.birth_date else '',
            'pet_death_date': fields.Date.from_string(self.animal_id.death_date).strftime(
                "%d/%m/%Y") if self.animal_id.death_date else '',
            'pet_breed': self.animal_id.race_id.name or '',
            'pet_identification': self.animal_id.chip_identification or '',
            'pet_death_reason': self.animal_id.death_reason or '',
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
