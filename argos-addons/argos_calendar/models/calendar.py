# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'
    _inherits = {"planning.slot": "planning_slot_id"}

    planning_slot_id = fields.Many2one('planning.slot', string='Planning', required=True, ondelete='cascade')
    appointment_stop = fields.Datetime('Appointment Stop')
    name = fields.Text(related='planning_slot_id.name', readonly=False)
    start = fields.Datetime(related='planning_slot_id.start_datetime')
    stop = fields.Datetime(related='planning_slot_id.end_datetime')
    start_datetime = fields.Datetime(related='planning_slot_id.start_datetime')
    stop_datetime = fields.Datetime(related='planning_slot_id.end_datetime')
    end_datetime = fields.Datetime(related='planning_slot_id.end_datetime')

    @api.model
    def create(self, vals):
        res = super(CalendarEvent, self).create(vals)
        if not res.appointment_stop:
            res.write({'appointment_stop': res.end_datetime})
        return res

    def unlink(self):
        for planning in self.mapped('planning_slot_id'):
            planning.button_cancel()
        return super(CalendarEvent, self).unlink()
