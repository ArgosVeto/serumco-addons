# -*- coding: utf-8 -*-

from odoo import fields, models


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    employee_ids = fields.Many2many('hr.employee', 'operating_unit_employee_rel', 'operating_unit_id', 'employee_id',
                                    'Employees')
    skill_ids = fields.One2many('hr.employee.skill', related='employee_ids.employee_skill_ids')
