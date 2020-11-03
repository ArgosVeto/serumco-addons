# -*- coding: utf-8 -*-

import math
from datetime import datetime, timedelta, time

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError


def float_to_time(hours):
    """ Convert a number of hours into a time object. """
    if hours == 24.0:
        return time.max
    fractional, integral = math.modf(hours)
    return time(int(integral), int(float_round(60 * fractional, precision_digits=0)), 0)


class PlanningSlot(models.Model):
    _inherit = 'planning.slot'

    calendar_event_ids = fields.One2many('calendar.event', 'planning_slot_id', string='Meetings')

    def unlink(self):
        self.mapped('calendar_event_ids').write({'active': False})
        return super(PlanningSlot, self).unlink()

    def button_not_honored(self):
        self.ensure_one()
        self.write({'state': 'not_honored'})
        self.calendar_event_ids.write({'active': False})
        return True

    def button_cancel(self):
        self.ensure_one()
        self.write({'state': 'cancel'})
        self.calendar_event_ids.write({'active': False})
        return True

    def button_validate(self):
        self.ensure_one()
        self.write({'state': 'validated'})
        self.with_context(active_test=False).calendar_event_ids.write({'active': True})
        self.send_confirmation_mail()
        return True

    @api.model
    def get_resources(self, start_date, end_date):
        employee_resources = {}
        start_date = fields.Date.from_string(start_date)
        end_date = fields.Date.from_string(end_date)
        cur_operating_unit = self.env.user.default_operating_unit_id
        if cur_operating_unit:
            domain = [('operating_unit_id', '=', cur_operating_unit.id), '|', '&', ('start_datetime', '>', start_date),
                      ('start_datetime', '<=', end_date), '&', ('end_datetime', '>', start_date),
                      ('end_datetime', '<=', end_date)]
            plannings = self.search(domain)
            for employee in plannings.mapped('employee_id'):
                employee_resources[employee.id] = employee.name
            if plannings.filtered(lambda l: not l.employee_id):
                employee_resources[False] = _('To assign')
        return {'employee_id': employee_resources}

    @api.model
    def get_resources_data(self, start_date, end_date):
        event_list = []
        start_date = fields.Date.from_string(start_date)
        end_date = fields.Date.from_string(end_date)
        employee_resources = self.get_resources((start_date - timedelta(days=1)).strftime('%Y-%m-%d'),
                                                end_date.strftime('%Y-%m-%d')).get('employee_id')
        delta = end_date - start_date
        timeoff_color = 'rgba(0,0,0,.15)'
        resource_calendar_id = self.env.company.resource_calendar_id
        if self.env.user.default_operating_unit_id and self.env.user.default_operating_unit_id.calendar_id:
            resource_calendar_id = self.env.user.default_operating_unit_id.calendar_id
        for key, val in employee_resources.items():
            for i in range(delta.days + 1):
                day_date = start_date + timedelta(days=i)
                break_time = False
                day = []
                start_date_lst = []
                end_date_lst = []

                week_day = day_date.weekday()
                make_date = day_date.strftime('%Y-%m-%d')

                sdate = datetime.strftime(day_date, '%Y-%m-%d') + " 00:00:00"
                edate = datetime.strftime(day_date, '%Y-%m-%d') + " 24:00:00"

                start, end = False, False
                day_list = [int(d.dayofweek) for d in resource_calendar_id.attendance_ids if
                            week_day == int(d.dayofweek)]
                day_period = False
                for work_hour in resource_calendar_id.attendance_ids:
                    if week_day == int(work_hour.dayofweek):
                        day.append(week_day)
                        start_date_lst.append(work_hour.hour_from)
                        end_date_lst.append(work_hour.hour_to)
                        start = float_to_time(work_hour.hour_from)
                        end = float_to_time(work_hour.hour_to)
                        day_period = work_hour.day_period
                        if work_hour.day_period == 'morning' and len(day_list) > 1:
                            event_list.append({'id': 'emp1' + str(key),
                                               'resourceId': key,
                                               'color': timeoff_color,
                                               'rendering': 'background',
                                               'start': sdate,
                                               'end': make_date + 'T' + str(start)})
                            break_time = make_date + 'T' + str(end)

                        elif work_hour.day_period == 'afternoon' and len(day_list) > 1:
                            if break_time:
                                event_list.append({'id': 'emp2' + str(key),
                                                   'resourceId': key,
                                                   'color': timeoff_color,
                                                   'rendering': 'background',
                                                   'start': break_time,
                                                   'end': make_date + 'T' + str(start)})

                            event_list.append({'id': 'emp3' + str(key),
                                               'resourceId': key,
                                               'color': timeoff_color,
                                               'rendering': 'background',
                                               'start': make_date + 'T' + str(end),
                                               'end': edate})

                if len(day_list) == 1:
                    if day_period == 'morning':
                        event_list.append({'id': 'emp_am' + str(key),
                                           'resourceId': key,
                                           'color': timeoff_color,
                                           'rendering': 'background',
                                           'start': sdate,
                                           'end': make_date + 'T' + str(start)})

                        event_list.append({'id': 'emp_am_end' + str(key),
                                           'resourceId': key,
                                           'color': timeoff_color,
                                           'rendering': 'background',
                                           'start': make_date + 'T' + str(end),
                                           'end': make_date + 'T' + str('24:00:00')})

                    if day_period == 'afternoon':
                        event_list.append({'id': 'emp_pm_start' + str(key),
                                           'resourceId': key,
                                           'color': timeoff_color,
                                           'rendering': 'background',
                                           'start': make_date + 'T' + str('00:00:00'),
                                           'end': make_date + 'T' + str(start)})

                        event_list.append({'id': 'emp_pm_end' + str(key),
                                           'resourceId': key,
                                           'color': timeoff_color,
                                           'rendering': 'background',
                                           'start': make_date + 'T' + str(end),
                                           'end': make_date + 'T' + str('24:00:00')})
                if len(day) == 0:
                    event_list.append({'id': 'emp4' + str(key),
                                       'resourceId': key,
                                       'color': timeoff_color,
                                       'rendering': 'background',
                                       'start': make_date + 'T' + '00:00:00',
                                       'end': make_date + 'T' + '24:00:00'})
                day.clear()
        return event_list

    @api.model
    def get_inactive_filters(self):
        return self.env['planning.role'].search([('role_type', '=', 'presence')]).ids

    @api.model
    def get_activities(self, start_date, end_date, resources):
        activities = {}
        start_date = fields.Date.from_string(start_date)
        end_date = fields.Date.from_string(end_date)
        delta = end_date - start_date
        employees = self.env['hr.employee'].search(
            [('user_id', '!=', False), ('id', 'in', [int(res) for res in resources])])
        for employee in employees:
            employee_activities = {}
            for i in range(delta.days + 1):
                day = start_date + timedelta(days=i)
                activity_count = self.env['mail.activity'].search_count(
                    [('user_id', '=', employee.user_id.id), ('date_deadline', '=', day)])
                employee_activities[str(day)] = activity_count
            activities[employee.id] = employee_activities
        return activities

    @api.model
    def get_tasks(self, start_date, end_date, resources):
        tasks = {}
        start_date = fields.Date.from_string(start_date)
        end_date = fields.Date.from_string(end_date)
        delta = end_date - start_date
        employees = self.env['hr.employee'].search(
            [('user_id', '!=', False), ('id', 'in', [int(res) for res in resources])])
        for employee in employees:
            employee_tasks = {}
            for i in range(delta.days + 1):
                day = start_date + timedelta(days=i)
                task_count = self.env['project.task'].search_count(
                    [('user_id', '=', employee.user_id.id), ('planned_date_begin', '>=', day),
                     ('planned_date_begin', '<', day + timedelta(days=1))])
                employee_tasks[str(day)] = task_count
            tasks[employee.id] = employee_tasks
        return tasks

    @api.model
    def get_activity_action(self, employee_id, event_date):
        event_date = fields.Date.from_string(event_date)
        user = self.env['hr.employee'].browse(employee_id).user_id
        context = dict(self._context or {})
        return {
            'name': _('%s - activities of %s') % (user.name, event_date.strftime('%d/%m/%Y')),
            'domain': [('user_id', '=', user.id), ('date_deadline', '=', event_date)],
            'type': 'ir.actions.act_window',
            'res_model': 'mail.activity',
            'view_type': 'list,form',
            'views': [[False, "list"], [False, "form"]],
            'target': 'current',
            'context': context,
        }

    @api.model
    def get_task_action(self, employee_id, event_date):
        event_date = fields.Date.from_string(event_date)
        user = self.env['hr.employee'].browse(employee_id).user_id
        context = dict(self._context or {})

        return {
            'name': _('%s - tasks of %s') % (user.name, event_date.strftime('%d/%m/%Y')),
            'domain': [('user_id', '=', user.id), ('planned_date_begin', '>=', event_date),
                       ('planned_date_begin', '<', event_date + timedelta(days=1))],
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'view_type': 'list,form',
            'views': [[False, "list"], [False, "form"]],
            'target': 'current',
            'context': context,
        }

    def action_open_agenda(self):
        action = self.env.ref('argos_calendar.agenda_calendar_action').read([])[0]
        action_domain = []
        if self.env.user.default_operating_unit_id:
            action_domain = [('operating_unit_id', '=', self.env.user.default_operating_unit_id.id)]
        action['domain'] = action_domain
        action['id'] = self.env.ref('argos_calendar.agenda_calendar_action_server').read([])[0].get('id', False)
        return action
