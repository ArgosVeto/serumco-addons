# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    result_line_ids = fields.One2many('project.task.line', 'patient_id', 'Analysis Result Lines')
    imagery_task_ids = fields.One2many('project.task', 'patient_id', 'Imagery', domain=[('task_type', '=', 'imagery')])