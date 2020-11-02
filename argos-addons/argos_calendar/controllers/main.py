# -*- coding: utf-8 -*-

import base64
import functools
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytz
from io import BytesIO
from babel.dates import format_datetime

from odoo import fields, http, _
from odoo.addons.web.controllers.main import Binary as _Binary
from odoo.addons.website_calendar.controllers.main import WebsiteCalendar
from odoo.http import request
from odoo.modules import get_resource_path
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from odoo.tools.misc import get_lang

IMAGE_FORMATS = ['png', 'svg']


class WebsitePlanning(WebsiteCalendar):
    @http.route(['/website/calendar/<model("calendar.appointment.type"):appointment_type>/info'], type='http',
                auth="public", website=True)
    def calendar_appointment_form(self, appointment_type, employee_id, date_time, **kwargs):
        partner_data = {}
        if request.env.user.partner_id != request.env.ref('base.public_partner'):
            partner_data = request.env.user.partner_id.read(fields=['name', 'mobile', 'country_id', 'email'])[0]
        day_name = format_datetime(datetime.strptime(date_time, dtf), 'EEE', locale=get_lang(request.env).code)
        date_formated = format_datetime(datetime.strptime(date_time, dtf), locale=get_lang(request.env).code)
        return request.render("argos_calendar.appointment_form_inherit", {
            'partner_data': partner_data,
            'appointment_type': appointment_type,
            'datetime': date_time,
            'datetime_locale': day_name + ' ' + date_formated,
            'datetime_str': date_time,
            'employee_id': employee_id,
            'countries': request.env['res.country'].search([]),
        })

    @http.route(['/website/calendar/<model("calendar.appointment.type"):appointment_type>/submit'], type='http',
                auth="public", website=True, method=["POST"])
    def calendar_appointment_submit(self, appointment_type, datetime_str, employee_id, name, phone, email, new_duration,
                                    country_id=False, **kwargs):
        timezone = request.session['timezone']
        tz_session = pytz.timezone(timezone)
        duration = appointment_type.appointment_duration
        date_start = tz_session.localize(fields.Datetime.from_string(datetime_str)).astimezone(pytz.utc)
        date_end = date_start + relativedelta(hours=duration)
        planning_date_end = date_start + relativedelta(hours=appointment_type.appointment_duration)

        # check availability of the employee again (in case someone else booked while the client was entering the form)
        Employee = request.env['hr.employee'].sudo().browse(int(employee_id))
        if Employee.user_id and Employee.user_id.partner_id:
            if not Employee.user_id.partner_id.calendar_verify_availability(date_start, date_end):
                return request.redirect('/website/calendar/%s/appointment?failed=employee' % appointment_type.id)

        country_name = country_id and request.env['res.country'].browse(int(country_id)).name or ''
        Partner = request.env['res.partner'].sudo().search([('email', '=like', email)], limit=1)
        if Partner:
            if not Partner.calendar_verify_availability(date_start, date_end):
                return request.redirect('/website/calendar/%s/appointment?failed=partner' % appointment_type.id)
            if not Partner.mobile or len(Partner.mobile) <= 5 and len(phone) > 5:
                Partner.write({'mobile': phone})
            if not Partner.country_id:
                Partner.country_id = country_id
        else:
            Partner = Partner.create({
                'name': name,
                'country_id': country_id,
                'mobile': phone,
                'email': email,
            })
        Clinic = Partner.operating_unit_id or request.env.user.default_operating_unit_id

        description = ('Country: %s\n'
                       'Mobile: %s\n'
                       'Email: %s\n' % (country_name, phone, email))
        for question in appointment_type.question_ids:
            key = 'question_' + str(question.id)
            if question.question_type == 'checkbox':
                answers = question.answer_ids.filtered(lambda x: (key + '_answer_' + str(x.id)) in kwargs)
                description += question.name + ': ' + ', '.join(answers.mapped('name')) + '\n'
            elif kwargs.get(key):
                if question.question_type == 'text':
                    description += '\n* ' + question.name + ' *\n' + kwargs.get(key, False) + '\n\n'
                else:
                    description += question.name + ': ' + kwargs.get(key) + '\n'

        categ_id = request.env.ref('website_calendar.calendar_event_type_data_online_appointment')
        alarm_ids = appointment_type.reminder_ids and [(6, 0, appointment_type.reminder_ids.ids)] or []
        partner_ids = list(set([Employee.user_id.partner_id.id] + [Partner.id]))
        event = request.env['calendar.event'].sudo().create({
            'state': 'open',
            'name': _('%s with %s') % (appointment_type.name, name),
            'start_date': date_start.strftime(dtf),
            'appointment_stop': planning_date_end.strftime(dtf),
            'allday': False,
            'duration': appointment_type.appointment_duration,
            'description': description,
            'alarm_ids': alarm_ids,
            'location': appointment_type.location,
            'partner_ids': [(4, pid, False) for pid in partner_ids],
            'categ_ids': [(4, categ_id.id, False)],
            'appointment_type_id': appointment_type.id,
            'employee_id': Employee.id,
            'user_id': Employee.user_id.id,
            'operating_unit_id': Clinic.id if Clinic else False,
            'website_planning': True,
        })
        event.attendee_ids.write({'state': 'accepted'})
        event.planning_slot_id.write({
            'partner_id': Partner.id,
            'name': _('%s with %s') % (appointment_type.name, name),
            'start_datetime': date_start.strftime(dtf),
            'end_datetime': date_end.strftime(dtf),
        })
        event.planning_slot_id.button_validate()
        return request.redirect('/website/calendar/view/' + event.access_token + '?message=new')


class WebsitePlanning(WebsiteCalendar):
    @http.route(['/website/calendar/<model("calendar.appointment.type"):appointment_type>/info'], type='http',
                auth="public", website=True)
    def calendar_appointment_form(self, appointment_type, employee_id, date_time, **kwargs):
        partner_data = {}
        if request.env.user.partner_id != request.env.ref('base.public_partner'):
            partner_data = \
                request.env.user.partner_id.read(fields=['name', 'mobile', 'country_id', 'email'])[0]
        day_name = format_datetime(datetime.strptime(date_time, dtf), 'EEE', locale=get_lang(request.env).code)
        date_formated = format_datetime(datetime.strptime(date_time, dtf), locale=get_lang(request.env).code)
        return request.render("argos_calendar.appointment_form_inherit", {
            'partner_data': partner_data,
            'appointment_type': appointment_type,
            'datetime': date_time,
            'datetime_locale': day_name + ' ' + date_formated,
            'datetime_str': date_time,
            'employee_id': employee_id,
            'countries': request.env['res.country'].search([]),
        })

    @http.route(['/website/calendar/<model("calendar.appointment.type"):appointment_type>/submit'], type='http',
                auth="public", website=True, method=["POST"])
    def calendar_appointment_submit(self, appointment_type, datetime_str, employee_id, name, phone, email,
                                    country_id=False, **kwargs):
        timezone = request.session['timezone']
        tz_session = pytz.timezone(timezone)
        duration = appointment_type.appointment_duration
        date_start = tz_session.localize(fields.Datetime.from_string(datetime_str)).astimezone(pytz.utc)
        date_end = date_start + relativedelta(hours=duration)
        planning_date_end = date_start + relativedelta(hours=appointment_type.appointment_duration)

        # check availability of the employee again (in case someone else booked while the client was entering the form)
        Employee = request.env['hr.employee'].sudo().browse(int(employee_id))
        if Employee.user_id and Employee.user_id.partner_id:
            if not Employee.user_id.partner_id.calendar_verify_availability(date_start, date_end):
                return request.redirect('/website/calendar/%s/appointment?failed=employee' % appointment_type.id)

        country_name = country_id and request.env['res.country'].browse(int(country_id)).name or ''
        Partner = request.env['res.partner'].sudo().search([('email', '=like', email)], limit=1)
        if Partner:
            if not Partner.calendar_verify_availability(date_start, date_end):
                return request.redirect('/website/calendar/%s/appointment?failed=partner' % appointment_type.id)
            if not Partner.mobile or len(Partner.mobile) <= 5 and len(phone) > 5:
                Partner.write({'mobile': phone})
            if not Partner.country_id:
                Partner.country_id = country_id
        else:
            Partner = Partner.create({
                'name': name,
                'country_id': country_id,
                'mobile': phone,
                'email': email,
            })
        Clinic = Partner.operating_unit_id or request.env.user.default_operating_unit_id

        description = ('Country: %s\n'
                       'Mobile: %s\n'
                       'Email: %s\n' % (country_name, phone, email))
        for question in appointment_type.question_ids:
            key = 'question_' + str(question.id)
            if question.question_type == 'checkbox':
                answers = question.answer_ids.filtered(lambda x: (key + '_answer_' + str(x.id)) in kwargs)
                description += question.name + ': ' + ', '.join(answers.mapped('name')) + '\n'
            elif kwargs.get(key):
                if question.question_type == 'text':
                    description += '\n* ' + question.name + ' *\n' + kwargs.get(key, False) + '\n\n'
                else:
                    description += question.name + ': ' + kwargs.get(key) + '\n'

        categ_id = request.env.ref('website_calendar.calendar_event_type_data_online_appointment')
        alarm_ids = appointment_type.reminder_ids and [(6, 0, appointment_type.reminder_ids.ids)] or []
        partner_ids = list(set([Employee.user_id.partner_id.id] + [Partner.id]))
        event = request.env['calendar.event'].sudo().create({
            'state': 'open',
            'name': _('%s with %s') % (appointment_type.name, name),
            'start_date': date_start.strftime(dtf),
            'appointment_stop': planning_date_end.strftime(dtf),
            'allday': False,
            'duration': appointment_type.appointment_duration,
            'description': description,
            'alarm_ids': alarm_ids,
            'location': appointment_type.location,
            'partner_ids': [(4, pid, False) for pid in partner_ids],
            'categ_ids': [(4, categ_id.id, False)],
            'appointment_type_id': appointment_type.id,
            'employee_id': Employee.id,
            'user_id': Employee.user_id.id,
            'operating_unit_id': Clinic.id if Clinic else False,
            'website_planning': True,
        })
        event.attendee_ids.write({'state': 'accepted'})
        event.planning_slot_id.write({
            'partner_id': Partner.id,
            'name': _('%s with %s') % (appointment_type.name, name),
            'start_datetime': date_start.strftime(dtf),
            'end_datetime': date_end.strftime(dtf),
        })
        event.planning_slot_id.button_validate()
        return request.redirect('/website/calendar/view/' + event.access_token + '?message=new')


class Binary(_Binary):
    def _logo(self, img='logo', fmt=None, **kwargs):
        if fmt and fmt not in IMAGE_FORMATS:
            raise ValueError(fmt)

        placeholder = functools.partial(get_resource_path, 'argos_calendar', 'static', 'src', 'img')
        company = request.env['res.company'].sudo().search([], limit=1)
        for try_fmt in [fmt] if fmt else IMAGE_FORMATS:
            field = '%s_icon' % img
            values = company.read([field, 'write_date'])[0]
            if values[field]:
                image = BytesIO(base64.b64decode(values[field]))
                return http.send_file(image, filename='%s.%s' % (img, try_fmt), mtime=values['write_date'])

        return http.send_file(placeholder('%s.%s' % (img, fmt or IMAGE_FORMATS[0])))

    @http.route(['/web/binary/invoice_icon'], type='http', auth='none', cors='*')
    def invoice_icon(self, **kwargs):
        return self._logo(img='invoice', **kwargs)

    @http.route(['/web/binary/hospital_icon'], type='http', auth='none', cors='*')
    def hospital_icon(self, **kwargs):
        return self._logo(img='hospital', **kwargs)

    @http.route(['/web/binary/medical_icon'], type='http', auth='none', cors='*')
    def medical_icon(self, **kwargs):
        return self._logo(img='medical', **kwargs)

    @http.route(['/web/binary/hour_icon'], type='http', auth='none', cors='*')
    def hour_icon(self, **kwargs):
        return self._logo(img='hour', **kwargs)
