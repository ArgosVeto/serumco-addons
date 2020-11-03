import re

from odoo import http
from odoo.http import request


class JitsiController(http.Controller):

    @http.route('/jitsi/<model("calendar.event"):event>', auth='user', website=True)
    def jitsi(self, event, **kw):
        if not event.use_jitsi:
            return request.render('jitsi_meet_integration.jitsi_not_enabled', {})

        server = request.env['ir.config_parameter'].sudo().get_param('jitsi.server', 'meet.jit.si')
        return request.render('jitsi_meet_integration.jitsi_room', {
            'event': event,
            'autostart': True,
            'jitsi_server': server,
        })

    @http.route('/jitsi/join/<int:attendee>', auth='public', website=True)
    def jitsi_join(self, attendee, **kw):
        attendee = request.env['calendar.attendee'].sudo().browse(attendee)
        event = attendee.event_id
        if not event.use_jitsi:
            return request.render('jitsi_meet_integration.jitsi_not_enabled', {})

        if not event.jitsi_open:
            return request.render('jitsi_meet_integration.jitsi_not_open', {})

        server = request.env['ir.config_parameter'].sudo().get_param('jitsi.server', 'meet.jit.si')
        return request.render('jitsi_meet_integration.jitsi_room', {
            'event': event,
            'attendee': attendee,
            'autostart': True,
            'jitsi_server': server,
        })

    @http.route('/jitsi/rpc/open', auth='user', type='json')
    def jitsi_open(self, **kw):
        event_id = int(request.params.get('event_id', False))
        if not event_id:
            return False
        event = request.env['calendar.event'].browse(event_id)
        if not event.use_jitsi:
            return False
        event.jitsi_open = True
        return True

    @http.route('/jitsi/close/<model("calendar.event"):event>', auth='user', website=True)
    def jitsi_close(self, event, **kw):
        event.jitsi_open = False

        return request.render('jitsi_meet_integration.jitsi_room', {
            'event': event,
            'autostart': False,
        })
