# -*- coding: utf-8 -*-

import ast
import datetime
import logging
from datetime import datetime as dt, timedelta
from odoo.exceptions import ValidationError

import pytz

from odoo import models, fields, api, _

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
    allday = fields.Boolean('All Day', default=False)
    background_event = fields.Boolean('Background', default=False)
    partner_phone = fields.Char(related='partner_id.phone', string='Customer phone')
    patient_ids = fields.Many2many('res.partner', related='partner_id.patient_ids')
    role_type = fields.Selection(related='role_id.role_type')
    website_planning = fields.Boolean(string='Website planning', default=False, copy=False)
    unexpected_rdv = fields.Boolean(string='Unexpected appointment', default=False, copy=False)

    @api.model
    def get_work_interval(self, start_date, employee=False):
        tz = self._context.get('tz') or self.env.user.partner_id.tz or 'UTC'
        timezone = pytz.timezone(tz)
        self_tz = self.with_context(tz=tz)

        start_date = fields.Datetime.context_timestamp(self_tz, start_date).replace(tzinfo=None).astimezone(timezone)
        start_datetime = dt.combine(start_date, datetime.time(8, 0, 0)).astimezone(pytz.utc)
        end_datetime = dt.combine(start_date, datetime.time(20, 0, 0)).astimezone(pytz.utc)
        if employee:
            work_interval = employee.resource_id._get_work_interval(start_datetime, end_datetime)
            if work_interval.get(employee.resource_id.id, False):
                start_dt, end_dt = work_interval[employee.resource_id.id]
                if start_dt:
                    start_datetime = start_dt.astimezone(pytz.utc).replace(tzinfo=None).astimezone(timezone)
                if end_dt:
                    end_datetime = end_dt.astimezone(pytz.utc).replace(tzinfo=None).astimezone(timezone)
        return [start_datetime.replace(tzinfo=None), end_datetime.replace(tzinfo=None)]

    def write(self, vals):
        if vals.get('rendering', False):
            del vals['rendering']
        if vals.get('allday', False) or self[0].allday:
            start_datetime = fields.Datetime.from_string(vals.get('start_datetime', False)) or self[0].start_datetime
            employee_id = self.env['hr.employee'].browse(vals['employee_id']) if 'employee_id' in vals else self[
                0].employee_id
            interval = self.get_work_interval(start_datetime, employee_id)
            vals['start_datetime'] = interval[0]
            vals['end_datetime'] = interval[1]
        res = super(PlanningSlot, self).write(vals)
        if not self.filtered(lambda l: l.website_planning):
            self.check_veterinary_presence()
        return res

    @api.onchange('allday')
    def _on_allday_change(self):
        if self.allday:
            interval = self.get_work_interval(self.start_datetime, self.employee_id)
            self.start_datetime = interval[0]
            self.end_datetime = interval[1]

    @api.onchange('role_id')
    def _on_role_change(self):
        if self.role_id and self.role_id.allday:
            self.allday = True

    @api.model
    def _cron_recover_planning(self):
        self._recover_away()
        self._recover_presence()
        self.env['planning.assignment']._recover_assignment()

    @api.model
    def _recover_away(self):
        # TODO : implement this method
        pass

    @api.model
    def _recover_presence(self):
        # TODO : implement this method
        pass

    @api.model
    def _prepare_slot_data(self, post={}):
        if not post:
            return {}
        role_obj = self.env['planning.role']
        type_obj = self.env['consultation.type']
        unit_obj = self.env['operating.unit']
        partner_obj = self.env['res.partner']
        employee_obj = self.env['hr.employee']
        return {
            'mrdv_event_id': post.get('mrdvEventId'),
            'mrdv_job_id': post.get('mrdvJobId'),
            'source': 'web',
            'role_id': role_obj._get_role_by_type(post.get('type')).id,
            'name': post.get('title'),
            'state': post.get('status'),
            'more_info': post.get('customerMoreInfo'),
            'start_datetime': post.get('startDate'),
            'end_datetime': post.get('endDate'),
            'consultation_type_id': type_obj._get_consultation_type(post.get('consultationName')).id,
            'operating_unit_id': unit_obj._get_operating_unit_by_location(post.get('location')).id,
            'partner_id': partner_obj._get_partner_by_name(post.get('customerName'), post.get('customerPhone')).id,
            'patient_id': partner_obj._get_patient_by_name(post.get('petName'), post.get('animalName'),
                                                           post.get('customerName'),
                                                           post.get('customerPhone')).id,
            'employee_id': employee_obj.search([('name', '=', post.get('employeeName'))]).id,
        }

    def send_confirmation_mail(self):
        self.ensure_one()
        try:
            email_template = self.env.ref('argos_planning.planning_validation_mail_template')
            employee = self.env['hr.employee.public'].browse(self.mapped('employee_id').id)
            template_context = {
                'employee': employee,
            }
            email_template.with_context(**template_context).send_mail(self.id, force_send=True, raise_exception=True)
        except Exception as e:
            _logger.error(repr(e))

    def button_validate(self):
        self.ensure_one()
        self.write({'state': 'validated'})
        if self.partner_id and not self.partner_id.has_activity:
            self.send_first_mail()
            self.partner_id.write({'has_activity': True})
        self.send_confirmation_mail()
        self.send_review_email()
        return True

    def button_not_honored(self):
        self.ensure_one()
        self.write({'state': 'not_honored'})
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
            'default_operating_unit_id': self.operating_unit_id.id,
        })
        return action

    def button_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancel'})
        self.send_cancellation_mail()
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
        if not res.website_planning:
            res.check_veterinary_presence()
        return res

    def check_veterinary_presence(self):
        cur_operating_unit = self.env.user.default_operating_unit_id
        role_obj = self.env['planning.role']
        presence_role_ids = role_obj.search([('role_type', '=', 'presence')]).ids
        absence_role_ids = role_obj.search([('role_type', '=', 'away')]).ids
        for rec in self.filtered(lambda
                                         l: l.employee_id and l.role_id and l.role_id.id not in absence_role_ids and l.role_id not in presence_role_ids):
            domain = [('operating_unit_id', '=', cur_operating_unit.id), ('employee_id', '=', rec.employee_id.id),
                      ('role_id', 'in', presence_role_ids), '|', '|', '&', ('start_datetime', '>=', rec.start_datetime),
                      ('start_datetime', '<', rec.end_datetime), '&', ('end_datetime', '>', rec.start_datetime),
                      ('end_datetime', '<', rec.end_datetime), '&', ('start_datetime', '<=', rec.start_datetime),
                      ('end_datetime', '>=', rec.end_datetime)]
            if not self.search(domain):
                raise ValidationError(_('Unauthorized appointment assignment for an absent or unassigned veterinarian'))

    def send_cancellation_mail(self):
        self.ensure_one()
        try:
            email_template = self.env.ref('argos_planning.planning_cancel_mail_template')
            email_template.send_mail(self.id, force_send=True, raise_exception=True)
        except Exception as e:
            _logger.error(repr(e))

    def send_first_mail(self):
        self.ensure_one()
        try:
            email_template = self.env.ref('argos_planning.planning_welcome_mail_template')
            email_template.send_mail(self.id, force_send=True, raise_exception=True)
        except Exception as e:
            _logger.error(repr(e))

    def send_review_email(self):
        for rec in self:
            try:
                email_template = self.env.ref('argos_planning.review_mail_template')
                email_template.send_mail(rec.id, force_send=True, raise_exception=True)
            except Exception as e:
                _logger.error(repr(e))
        return True
