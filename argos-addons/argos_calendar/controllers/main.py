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
    def calendar_appointment_submit(self, appointment_type, datetime_str, employee_id, name, phone, email,
                                    country_id=False, available_slot_alert=False, **kwargs):
        timezone = request.session['timezone']
        tz_session = pytz.timezone(timezone)
        if available_slot_alert:
            available_slot_alert = True
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
            'website_planning': True
        })
        event.attendee_ids.write({'state': 'accepted'})
        rdv_planning_role = request.env.ref('argos_planning.planning_role_appoint', False)
        event.planning_slot_id.write({
            'partner_id': Partner.id,
            'name': _('%s with %s') % (appointment_type.name, name),
            'start_datetime': date_start.strftime(dtf),
            'end_datetime': date_end.strftime(dtf),
            'available_slot_alert': available_slot_alert,
            'role_id': rdv_planning_role and rdv_planning_role.id or False
        })
        event.planning_slot_id.button_validate()
        return request.redirect('/website/calendar/view/' + event.access_token + '?message=new')

    @http.route('/website/replanning/<int:planning>/<int:partner_planning>', type='http', auth="public", website=True)
    def portal_website_replanning(self, planning, partner_planning, **kw):
        partner_data = {}
        if not request.session.uid or request.env.uid == 4:
            return http.local_redirect('/web/login?redirect=/website/replanning/%s/%s' % (planning, partner_planning))
        if request.env.user.partner_id != request.env.ref('base.public_partner'):
            partner_data = request.env.user.partner_id.read(fields=['name', 'mobile', 'country_id', 'email'])[0]
        planning = request.env['planning.slot'].sudo().browse(planning)
        partner_planning = request.env['planning.slot'].sudo().browse(partner_planning)
        timezone = request.session.get('timezone')
        if not timezone:
            timezone = request.env.context.get('tz') or planning.partner_id and planning.partner_id.tz
            request.session['timezone'] = timezone
        tz_session = pytz.timezone(timezone)

        if not planning or planning.state != 'cancel' \
                or not planning.with_context(active_test=False).calendar_event_ids \
                or not partner_planning or not partner_planning.available_slot_alert \
                or not partner_planning.calendar_event_ids or planning.employee_id.id != partner_planning.employee_id.id \
                or planning.operating_unit_id.id != partner_planning.operating_unit_id.id \
                or planning.start_datetime >= partner_planning.start_datetime:
            return request.render("argos_calendar.replanning")

        appointment_type = partner_planning.calendar_event_ids[0].appointment_type_id
        day_name = format_datetime(planning.start_datetime, 'EEE', locale=get_lang(request.env).code)
        date_formated = format_datetime(planning.start_datetime.replace(tzinfo=pytz.utc).astimezone(tz_session),
                                        locale=get_lang(request.env).code)
        values = {
            'partner_data': partner_data,
            'appointment': planning,
            'partner_appointment': partner_planning,
            'appointment_type': appointment_type,
            'datetime': planning.start_datetime,
            'datetime_locale': day_name + ' ' + date_formated,
            'datetime_str': planning.start_datetime,
            'countries': request.env['res.country'].search([])
        }
        return request.render("argos_calendar.replanning_form", values)

    @http.route('/website/replanning/<int:planning>/<int:partner_planning>/submit', type='http', auth="public",
                website=True)
    def portal_submit_website_replanning(self, planning, partner_planning, name, phone, email, country_id=False,
                                         available_slot_alert=False, **kw):
        planning = request.env['planning.slot'].sudo().browse(planning)
        partner_planning = request.env['planning.slot'].sudo().browse(partner_planning)
        if available_slot_alert:
            available_slot_alert = True

        if not planning or planning.state != 'cancel' \
                or not planning.with_context(active_test=False).calendar_event_ids \
                or not partner_planning or not partner_planning.available_slot_alert \
                or not partner_planning.calendar_event_ids or planning.employee_id.id != partner_planning.employee_id.id \
                or planning.operating_unit_id.id != partner_planning.operating_unit_id.id \
                or planning.start_datetime >= partner_planning.start_datetime:
            return request.render("argos_calendar.replanning")

        country_name = country_id and request.env['res.country'].browse(int(country_id)).name or ''
        Employee = planning.employee_id
        Partner = request.env['res.partner'].sudo().search([('email', '=like', email)], limit=1)
        if Partner:
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

        description = ('Country: %s\n'
                       'Mobile: %s\n'
                       'Email: %s\n' % (country_name, phone, email))

        partner_ids = list(set([Employee.user_id.partner_id.id] + [Partner.id]))
        event = planning.with_context(active_test=False).calendar_event_ids[0]
        event.sudo().write({
            'partner_ids': [(4, pid, False) for pid in partner_ids],
            'description': description
        })
        planning.write({
            'partner_id': Partner.id,
            'patient_id': False,
            'available_slot_alert': available_slot_alert
        })
        partner_planning.button_cancel()
        planning.button_validate()
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
