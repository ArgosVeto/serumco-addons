# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class PlanningAssignment(models.Model):
    _name = "planning.assignment"
    _description = "Planning Assignment"

    start_date = fields.Datetime('Start Date')
    end_date = fields.Datetime('End Date')
    operating_unit_id = fields.Many2one('operating.unit', 'Clinic')
    employee_id = fields.Many2one('hr.employee', 'Veterinary')

    @api.model
    def _recover_assignment(self):
        print('Assignment')