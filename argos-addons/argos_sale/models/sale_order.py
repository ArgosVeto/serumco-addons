# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import urllib.parse as urlparse
from odoo.exceptions import UserError, ValidationError
import logging
import json
import requests
from datetime import datetime, timedelta


_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_patient_ids = fields.Many2many(related='partner_id.patient_ids', string='Patient List')
    argos_state = fields.Selection([('in_progress', 'In progress'), ('consultation_done', 'Done')], copy=False)
    partner_id = fields.Many2one(
        domain="[('contact_type', '=', 'contact'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    patient_id = fields.Many2one('res.partner', 'Patient', domain="[('contact_type', '=', 'patient')]")
    species_id = fields.Many2one(related='patient_id.species_id')
    race_id = fields.Many2one(related='patient_id.race_id')
    gender_id = fields.Many2one(related='patient_id.gender_id')
    age = fields.Char('Age', related='patient_id.age_formatted')
    weight = fields.Float('Weight', related='patient_id.weight')
    pathology_ids = fields.Many2many('res.partner.pathology', related='patient_id.pathology_ids', readonly=False)
    employee_id = fields.Many2one('hr.employee', domain="[('is_veterinary', '=', True)]")
    is_consultation = fields.Boolean('Is Consultation')
    conv_key = fields.Char('Convention Key', copy=False)
    consultation_date = fields.Date('Consultation Date', default=lambda self: fields.Date.today())
    consultation_type_id = fields.Many2one('consultation.type', domain=[('is_canvas', '=', False)])
    observation = fields.Text('Observations')
    customer_observation = fields.Text('Customer Observation')
    referent_partner_id = fields.Many2one('res.partner')
    diagnostic_ids = fields.Many2many('documents.tag', 'sale_order_diagnostic_tag_rel', 'sale_order_id',
                                      'diagnostic_id', domain=[('type', '=', 'diagnostic')])
    hypothese_ids = fields.Many2many('documents.tag', 'sale_order_hypothese_tag_rel', 'sale_order_id', 'hypothese_id',
                                     domain=[('type', '=', 'hypothese')])
    canvas_id = fields.Many2one('consultation.type', domain=[('is_canvas', '=', True)])
    arrival_time = fields.Datetime('Arrival Time', track_visibility='onchange', copy=False)
    pickup_time = fields.Datetime('Pick-up Time', track_visibility='onchange', copy=False)
    refer_employee_id = fields.Many2one('hr.employee', 'Referent', readonly=True)
    is_referral = fields.Boolean('Is a referral', readonly=True)
    origin_order_id = fields.Many2one('sale.order', 'Origin of the consultation', readonly=True)
    refer_order_ids = fields.One2many('sale.order', 'origin_order_id', 'Referred', readonly=True)
    refer_count = fields.Integer('Refers count', compute='_count_refers')
    is_incineris = fields.Boolean('Is Incineris', compute='_compute_is_incineris')
    invoice_creation_date = fields.Date('Invoice creation date')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments', compute='_compute_attachment_ids')

    def _compute_attachment_ids(self):
        for rec in self:
            rec.attachment_ids = self.env['ir.attachment'].search(
                [('res_id', '=', rec.id), ('res_model', '=', rec._name)])

    def _response_status_check(self, code):
        if code == 400:
            ret = 'missing (idCommande) information.'
        elif code == 401:
            ret = 'You doesnt can authentificate or not subscript this service.'
        elif code == 403:
            ret = 'forbidden'
        elif code == 404:
            ret = 'Sale order number doesnt fint in API.'
        elif code == 200:
            ret = 'Success'
        else:
            ret = 'not identified'
        return ret


    #Oliger de reecrire la fonction de connexion (Lilian)
    def get_auth_token(self, log_res_id=None, log_model_name=None):
        """
        Function to get token api centravet, and log connexion.
        """
        # TODO: Config system parameter: api.centravet.auth.token, api.centravet.stock, api.centravet.login.password
        URL = self.env['ir.config_parameter'].sudo().get_param('api.centravet.auth.token')
        headers = {'Content-Type': 'application/json'}
        mail = self.env['ir.config_parameter'].sudo().get_param('api.centravet.login.mail')
        password = self.env['ir.config_parameter'].sudo().get_param('api.centravet.login.password')
        payload = {'email': mail, 'password': password}

        response = requests.post(url=URL, headers=headers, data=json.dumps(payload))

        reason = self._response_status_check(response.status_code)

        self.env['soap.wsdl.log'].sudo().create({
            'name': 'API stock centravet AUTH',
            'res_id': log_res_id,
            'model_id': self.env['ir.model'].sudo().search([('model', '=', log_model_name)], limit=1).id,
            'msg': "Ask API authorization token",
            'date': fields.Datetime.today(),
            'state': 'successful' if response.status_code == 200 else 'error',
            'reason': reason,
        })

        return response.json() if response.status_code == 200 else False

    def get_compute_api_information(self):
        """
        Code call by button to get information about sale.order in Centravet API
        """
        token = self.get_auth_token(self, 'sale.order')
        headers = {'Content-Type': 'application/json', 'Authorization': 'bearer ' + token}
        endpoint = self.env['ir.config_parameter'].sudo().get_param('api.centravet.sale')
        for rec in self:
            #TODO use centravet code et shop + idCommande
            centravet_code = rec.operating_unit_id.code #codeClinique
            centravet_web_shop = rec.operating_unit_id.web_shop_id #codeBoutique

            url = '{endpoint}/{idCommande}/timeline'
            final_url = url.format(
                endpoint=endpoint,
                idCommande=rec.name,
            )
            payload = {
                'codeClinique': centravet_code,
                'codeBoutique': centravet_web_shop,
            }
            response = requests.get(url=final_url, headers=headers, params=payload)
            if response.status_code == 200:
                return response.text
            else:
                return False

    def convert_date_is8601(self, is8601_datetime):
        """
        Convert date str to datetime pythonic format
        """
        if is8601_datetime:
            return (datetime.strptime(is8601_datetime[-1], "%Y-%m-%dT%H:%M:%S") + timedelta(hours=-2))
        else:
            return False

    def compute_api_information(self):
        """
        call api centravet to get information dates about sale.order
        display in tree view
        """
        res = self.get_compute_api_information()
        if res:
            api_datas = json.loads(res)
            vals = {
                'description': "Sale: " + self.name,
                'date_sent': self.convert_date_is8601(api_datas["dateSent"]),
                'date_integrated': self.convert_date_is8601(api_datas["dateIntegrated"]),
                'date_prepared': self.convert_date_is8601(api_datas["datePrepared"]),
                'date_delivered': self.convert_date_is8601(api_datas["dateDelivered"]),
                'date_billed': self.convert_date_is8601(api_datas["dateBilled"]),
            }
        else:
            vals = {'description': 'Can not access to API, please check connexion parameters and idCommande'}

        api_information_id = self.env['api.information.wizard'].create(vals)
        form = self.env.ref('argos_sale.sale_api_information_wizard', False)
        return {
            'name': _('Api Informations'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [form.id],
            'res_model': 'api.information.wizard',
            'res_id': api_information_id.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
    @api.depends('order_line', 'order_line.product_id', 'order_line.product_id.act_type')
    def _compute_is_incineris(self):
        for rec in self:
            rec.is_incineris = any(line.product_id.act_type == 'incineration' for line in rec.order_line)

    @api.depends('refer_order_ids')
    def _count_refers(self):
        for consultation in self:
            consultation.refer_count = len(consultation.refer_order_ids)

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

    def set_conv_key(self):
        self.ensure_one()
        soft_id = self.env['ir.config_parameter'].get_param('incineris.soft_id')
        editor_id = soft_id or ''
        vet_id = str(self.employee_id.id)
        owner_id = str(self.partner_id.id)
        patient_id = str(self.patient_id.id)
        timestamp = str(fields.Datetime.now())
        self.conv_key = '-'.join([editor_id, vet_id, owner_id, patient_id, timestamp])
        return True

    def button_edit_incineris(self):
        self.ensure_one()
        if not self.is_consultation:
            raise UserError(_('Only consultation can generate incineris convention.'))
        url = self.env['ir.config_parameter'].get_param("incineris_url") or ''
        soft_id = self.env['ir.config_parameter'].get_param("incineris.soft_id")
        species = self.patient_id.species_id and self.patient_id.species_id.is_incineris_species and self.patient_id.species_id.name or \
                  'nac'
        self.set_conv_key()
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

    def button_referrals_view(self):
        self.ensure_one()
        action = self.env.ref('argos_sale.action_consultations').read()[0]
        action.update({
            'name': _('Referrals'),
            'target': 'current',
            'domain': [('id', 'in', self.refer_order_ids.ids)],
        })
        return action

    def button_confirm_edition_sale_completed(self):
        self.ensure_one()
        self.action_cancel()
        self.action_draft()
        return True

    def button_end_consultation(self):
        self.ensure_one
        self.write({
            'pickup_time': fields.Datetime.now(),
            'argos_state': 'consultation_done'
        })
