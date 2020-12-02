# -*- coding: utf-8 -*-

from collections import OrderedDict

import pytz
from babel.dates import format_datetime, format_date
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from werkzeug.urls import url_encode

from odoo import http, _, fields
from odoo.http import request
from odoo.tools import html2plaintext
from odoo.tools.misc import get_lang


class CustomerPortal(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        values['appointment_count'] = request.env['planning.slot'].sudo().search_count(
            [('website_planning', '=', True), ('partner_id', '=', request.env.user.partner_id.id)])
        return values

    @http.route(['/my/appointments', '/my/appointments/page/<int:page>'], type='http', auth="public", website=True)
    def portal_my_appointments(self, page=1, sortby=None, filterby=None, **kw):
        if not request.session.uid or request.env.uid == 4:
            return http.local_redirect('/web/login?redirect=/my/appointments')
        values = self._prepare_portal_layout_values()
        Planning = request.env['planning.slot'].sudo()
        domain = [('website_planning', '=', True), ('partner_id', '=', request.env.user.partner_id.id)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'start_datetime desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        searchbar_filters = {
            'all': {'label': _('All'), 'domain': [
                ('state', 'in', ['validated', 'waiting', 'in_progress', 'done', 'cancel', 'not_honored'])]},
            'validate': {'label': _('Validated'), 'domain': [('state', '=', 'validated')]},
            'done': {'label': _('Done'), 'domain': [('state', '=', 'done')]},
            'cancel': {'label': _('Cancelled'), 'domain': [('state', '=', 'cancel')]},
            'not_honored': {'label': _('Not honored'), 'domain': [('state', '=', 'not_honored')]},
        }
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # plannins count
        plannings_count = Planning.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/appointments",
            url_args={'sortby': sortby},
            total=plannings_count,
            page=page,
            step=self._items_per_page
        )

        # content according to pager and archive selected
        plannings = Planning.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'plannings': plannings,
            'page_name': 'planning',
            'default_url': '/my/appointments',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("argos_calendar.portal_my_plannings", values)

    @http.route(['/my/appointment/<string:access_token>'], type='http', auth="public", website=True)
    def portal_my_appointment(self, access_token=None, edit=False, message=False, **kw):
        event = request.env['calendar.event'].sudo().search(
            [('access_token', '=', access_token), ('planning_slot_id.partner_id', '=', request.env.user.partner_id.id)],
            limit=1)
        if not event:
            return request.not_found()
        timezone = request.session.get('timezone')
        if not timezone:
            timezone = request.env.context.get(
                'tz') or event.appointment_type_id.appointment_tz or event.partner_ids and event.partner_ids[0].tz
            request.session['timezone'] = timezone
        tz_session = pytz.timezone(timezone)

        date_start_suffix = ""
        format_func = format_datetime
        if not event.allday:
            url_date_start = fields.Datetime.from_string(event.start_datetime).strftime('%Y%m%dT%H%M%SZ')
            url_date_stop = fields.Datetime.from_string(event.stop_datetime).strftime('%Y%m%dT%H%M%SZ')
            date_start = fields.Datetime.from_string(event.start_datetime).replace(tzinfo=pytz.utc).astimezone(
                tz_session)
        else:
            url_date_start = url_date_stop = fields.Date.from_string(event.start_date).strftime('%Y%m%d')
            date_start = fields.Date.from_string(event.start_date)
            format_func = format_date
            date_start_suffix = _(', All Day')

        locale = get_lang(request.env).code
        day_name = format_func(date_start, 'EEE', locale=locale)
        date_start = day_name + ' ' + format_func(date_start, locale=locale) + date_start_suffix
        details = event.appointment_type_id and event.appointment_type_id.message_confirmation or event.description or ''
        params = url_encode({
            'action': 'TEMPLATE',
            'text': event.name,
            'dates': url_date_start + '/' + url_date_stop,
            'details': html2plaintext(details.encode('utf-8'))
        })
        google_url = 'https://www.google.com/calendar/render?' + params

        return request.render("argos_calendar.appointment_info", {
            'event': event,
            'datetime_start': date_start,
            'google_url': google_url,
            'message': message,
            'edit': edit,
        })
