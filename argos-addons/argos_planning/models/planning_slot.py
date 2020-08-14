# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class PlanningSlot(models.Model):
    _inherit = 'planning.slot'

    mrdv_event_id = fields.Integer('Mrdv Id')
    mrdv_job_id = fields.Integer('Mrdv Job Id')
    source = fields.Selection([('ounit', 'Operating Unit'), ('phone', 'Phone'), ('web', 'Web')], 'Source',
                              default='ounit')
    patient_id = fields.Many2one('res.partner', 'Patient', domain="[('contact_type', '=', 'patient')]")
    partner_id = fields.Many2one('res.partner', 'Customer', domain="[('contact_type', '=', 'contact')]")
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')
    consultation_type_id = fields.Many2one('consultation.type', 'Consultation Type')
    active = fields.Boolean('Active', default=True)
    state = fields.Selection([('draft', 'Draft'), ('validated', 'Validated'), ('cancel', 'Cancelled')], 'State',
                             default='draft')
    more_info = fields.Text('More Information')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    total_due = fields.Monetary(related='partner_id.total_due')

    @api.model
    def _cron_recover_planning(self):
        self._recover_away()
        self._recover_presence()
        self.env['planning.assignment']._recover_assignment()

    @api.model
    def _recover_away(self):
        print('Away')

    @api.model
    def _recover_presence(self):
        print('Presence')

    @api.model
    def _prepare_slot_data(self, post={}):
        if not post:
            return {}
        role_obj = self.env['planning.role']
        type_obj = self.env['consultation.type']
        unit_obj = self.env['operating.unit']
        partner_obj = self.env['res.partner']
        return {
            'mrdv_event_id': post.get('mrdvEventId'),
            'mrdv_job_id': post.get('mrdvJobId'),
            'source': 'web',
            'role_id': role_obj._get_role_by_type(post.get('type')).id,
            'name': post.get('title'),
            'state': post.get('status'),
            'more_info': post.get('CustomerMoreInfo'),
            'start_datetime': post.get('startDate'),
            'end_datetime': post.get('endDate'),
            'consultation_type_id': type_obj._get_consultation_type(post.get('consultationName')).id,
            'operating_unit_id': unit_obj._get_operating_unit_by_location(post.get('location')).id,
            'partner_id': partner_obj._get_partner_by_name(post.get('customerName'), post.get('customerPhone')).id,
            'patient_id': partner_obj._get_patient_by_name(post.get('petName'), post.get('animalName'),
                                                           post.get('customerName'),
                                                           post.get('customerPhone')).id,
        }

    def button_validate(self):
        self.ensure_one()
        self.write({'state': 'validated'})
        return True

    def button_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancel'})
        return True

    def button_set_to_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})
        return True

    def open_action_followup(self):
        self.ensure_one()
        action = self.env.ref('account_followup.customer_statements_form_view').read()[0]
        action['res_id'] = self.partner_id.id
        return action

    def send_notification_mail(self):
        self.ensure_one()
        try:
            email_template = self.env.ref('argos_planning.notification_mail_template')
            email_template.send_mail(self.id, force_send=True, raise_exception=True)
        except Exception as e:
            _logger.error(repr(e))

    @api.model
    def create(self, vals):
        res = super(PlanningSlot, self).create(vals)
        if res.partner_id and res.partner_id.tutor_curator_id:
            res.send_notification_mail()
        return res
