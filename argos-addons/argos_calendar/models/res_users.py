# -*- coding: utf-8 -*-

from datetime import timedelta
from pytz import timezone, UTC

from odoo import api, models, fields, modules, _


class Users(models.Model):
    _inherit = 'res.users'

    def _systray_get_next_planning_domain(self):
        tz = self.env.user.tz
        cur_date = fields.Datetime.now()
        if tz:
            cur_date = timezone(tz).localize(cur_date).astimezone(UTC)
        return [('start_datetime', '>=', cur_date), ('state', 'in', ['validated']),
                ('employee_id.user_id', '=', self.env.user.id), ('role_id.role_type', '=', 'rdv')]

    @api.model
    def systray_get_activities(self):
        res = super(Users, self).systray_get_activities()
        tz = self.env.user.tz
        cur_date = fields.Datetime.now()
        if tz:
            cur_date = timezone(tz).localize(cur_date).astimezone(UTC)
        planning_slot_obj = self.env['planning.slot']
        plannings_lines = []
        plannings = planning_slot_obj.search_read(
            self._systray_get_next_planning_domain(),
            ['id', 'employee_id', 'start_datetime', 'name', 'allday', 'state'],
            order='start_datetime')
        for planning in [p for p in plannings if timezone('UTC').localize(p['start_datetime']) >= cur_date >= (
                timezone('UTC').localize(p['start_datetime']) - timedelta(hours=24))]:
            last_planning = planning_slot_obj.search(
                [('employee_id', '=', planning['employee_id'][0]), ('start_datetime', '<', planning['start_datetime']),
                 ('role_id.role_type', '=', 'rdv')], order='start_datetime desc', limit=1)
            if last_planning and last_planning.state == 'not_honored':
                plannings_lines.append(planning)

        if plannings_lines:
            planning_label = _("Clients with unfulfilled appointments")
            plannings_systray = {
                'type': 'next_planning',
                'name': planning_label,
                'model': 'planning.slot',
                'domain': ['id', 'in', [p['id'] for p in plannings_lines]],
                'icon': modules.module.get_module_icon(self.env['planning.slot']._original_module),
                'plannings': plannings_lines,
            }
            res.insert(0, plannings_systray)

        return res
