# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def calendar_verify_availability(self, date_start, date_end):
        """ verify availability of the partner(s) between 2 datetimes on their calendar
        """
        if bool(self.env['calendar.event'].search_count([
            ('partner_ids', 'in', self.ids),
            '|', '&', ('start_datetime', '<', fields.Datetime.to_string(date_end)),
            ('appointment_stop', '>', fields.Datetime.to_string(date_start)),
            '&', ('allday', '=', True),
            '|', ('start_date', '=', fields.Date.to_string(date_end)),
            ('start_date', '=', fields.Date.to_string(date_start))])):
            return False
        return True
