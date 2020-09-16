# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
import ast

_logger = logging.getLogger(__name__)


class PlanningSlot(models.Model):
    _name = 'planning.slot'
    _inherit = ['planning.slot', 'mail.thread', 'mail.activity.mixin']

    mrdv_event_id = fields.Integer('Mrdv Id')
    mrdv_job_id = fields.Integer('Mrdv Job Id')
    source = fields.Selection([('ounit', 'Operating Unit'), ('phone', 'Phone'), ('web', 'Web')], 'Source',
                              default='ounit')
    patient_id = fields.Many2one('res.partner', 'Patient', domain="[('contact_type', '=', 'patient')]")
    partner_id = fields.Many2one('res.partner', 'Customer', domain="[('contact_type', '=', 'contact')]")
    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit')
    consultation_type_id = fields.Many2one('consultation.type', 'Consultation Type', domain=[('is_canvas', '=', False)])
    active = fields.Boolean('Active', default=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('validated', 'Validated'), ('waiting', 'Waiting'), ('in_progress', 'In Progress'),
         ('done', 'Done'), ('cancel', 'Cancelled'), ('not_honored', 'Not Honored')], 'State',
        default='draft', track_visibility='onchange')
    more_info = fields.Text('More Information')
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    total_due = fields.Monetary(related='partner_id.total_due')
    arrival_time = fields.Datetime('Arrival Time', track_visibility='onchange')
    pickup_time = fields.Datetime('Pick-up Time', track_visibility='onchange')
    departure_time = fields.Datetime('Departure Time', track_visibility='onchange')

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

    def button_set_to_waiting(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        url = '%s/web#id=%s&model=%s' % (base_url, self.id, self._name)
        channel_obj = self.env['mail.channel']
        if self.user_id:
            result = channel_obj.channel_get([self.user_id.partner_id.id])
            vals = {
                'body': _('Your appointment has arrived: <a href=# data-oe-model=planning.slot data-oe-id=%d>%s</a>' %
                          (self.id, url)),
                'subtype': 'mail.mt_comment',
                'message_type': 'comment',
            }
            if result:
                channel = channel_obj.browse(result.get('id'))
                channel.message_post(**vals)
        self.write({
            'arrival_time': fields.Datetime.now(),
            'state': 'waiting'
        })
        return True

    def button_progress(self):
        self.ensure_one()
        self.write({
            'pickup_time': fields.Datetime.now(),
            'state': 'in_progress'
        })
        action = self.env.ref('argos_sale.action_consultations').read()[0]
        action['views'] = [(self.env.ref('argos_sale.consultation_view_order_form').id, 'form')]
        action['context'] = ast.literal_eval(action['context'])
        action['context'].update({
            'default_slot_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_patient_id': self.patient_id.id,
            'default_employee_id': self.employee_id.id,
            'default_is_consultation': True,
            'default_consultation_type_id': self.consultation_type_id.id,
            'default_customer_observation': self.more_info,
        })
        return action

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
        return self.partner_id.open_action_followup()

    def send_notification_mail(self):
        self.ensure_one()
        try:
            email_template = self.env.ref('argos_planning.planning_notification_mail_template')
            email_template.send_mail(self.id, force_send=True, raise_exception=True)
        except Exception as e:
            _logger.error(repr(e))

    @api.model
    def create(self, vals):
        res = super(PlanningSlot, self).create(vals)
        if res.partner_id and res.partner_id.has_tutor_curator:
            res.send_notification_mail()
        return res
