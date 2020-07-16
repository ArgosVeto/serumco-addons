import logging
import re

from odoo.addons.calendar.models.calendar import calendar_id2real_id
from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    use_jitsi = fields.Boolean(
            string='Remote Meeting',
    )

    jitsi_password = fields.Char(
            string='Password',
    )

    jitsi_url = fields.Char(
            string='Jitsi Url',
            compute='_compute_jitsi_url',
    )

    jitsi_open = fields.Boolean(
            string='Jitsi Open',
            help='The Remote Meeting allows to join',
    )

    jitsi_room = fields.Char(
            string='Jitsi Room',
            compute='_compute_jitsi_url',
    )

    def _compute_jitsi_url(self):
        for record in self.filtered(lambda f: f.use_jitsi):
            real_id = calendar_id2real_id(record.id)
            record.jitsi_url = '/jitsi/{0}'.format(real_id)
            room_name = '{0} vc {1}'.format(record.user_id.company_id.name, real_id).lower()
            room_name = re.sub('[^\w ]+', '', room_name)
            room_name = re.sub(' +', '-', room_name)
            record.jitsi_room = room_name

    def action_open_jitsi(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': self.jitsi_url,
        }


class Attendee(models.Model):
    _inherit = 'calendar.attendee'

    jitsi_url = fields.Char(
            string='Jitsi Url',
            compute='_compute_jitsi_url'
    )

    def _compute_jitsi_url(self):
        for record in self.filtered(lambda f: f.event_id.use_jitsi):
            record.jitsi_url = '/jitsi/join/{0}'.format(record.id)

    def _send_mail_to_attendees(self, template_xmlid, force_send=False):
        jitsi_template_xmlid = 'jitsi_meet_integration.{0}_jitsi'.format(template_xmlid.split('.', 1)[1])
        jitsi_attendees = self.filtered(lambda f: f.event_id.use_jitsi)
        normal_attendees = self.filtered(lambda f: not f.event_id.use_jitsi)

        result1 = super(Attendee, normal_attendees)._send_mail_to_attendees(template_xmlid, force_send)
        result2 = super(Attendee, jitsi_attendees)._send_mail_to_attendees(jitsi_template_xmlid, force_send)
        return result1 and result2
