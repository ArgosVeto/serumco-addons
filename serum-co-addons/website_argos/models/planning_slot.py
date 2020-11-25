# -*- coding: utf-8 -*-
# Developed by Auguria.
# See LICENSE file for full copyright and licensing details

from odoo import api, fields, models, _
import pytz
import logging
_logger = logging.getLogger(__name__)

try:
    import vobject
except ImportError:
    _logger.warning("`vobject` Python module not found, iCal file generation disabled. Consider installing this module if you want to generate iCal files")
    vobject = None

class PlanningSlot(models.Model):
    _inherit = 'planning.slot'

    def _get_ics_file(self):
        """ Returns iCalendar file for the event invitation.
            :returns a dict of .ics file content for each event
        """

        def ics_datetime(idate, allday=False):
            if idate:
                if allday:
                    return fields.Date.from_string(idate)
                else:
                    return fields.Datetime.from_string(idate).replace(tzinfo=pytz.timezone('UTC'))
            return False

        result = {}
        if not vobject:
            return result

        for slot in self:
            cal = vobject.iCalendar()
            cal_planning = cal.add('vevent')

            cal_planning.add('created').value = ics_datetime(fields.Datetime.now())
            cal_planning.add('dtstart').value = ics_datetime(slot.start_datetime)
            cal_planning.add('dtend').value = ics_datetime(slot.end_datetime)
            cal_planning.add('summary').value = slot.name or slot.operating_unit_id and slot.operating_unit_id.name
            if slot.sudo().operating_unit_id and slot.sudo().operating_unit_id.partner_id:
                cal_planning.add('location').value = slot.sudo().operating_unit_id.partner_id._display_address() or ''
            result[slot.id] = cal.serialize().encode('utf-8')
        return result
