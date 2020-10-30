# -*- coding: utf-8 -*-

from odoo import fields, models, api


class TaskResultLine(models.Model):
    _name = 'project.task.line'
    _description = 'Project Task Result Line'

    task_id = fields.Many2one('project.task', 'Result')
    parameter_id = fields.Many2one('project.tags', 'Parameter')
    value = fields.Float('Value')
    unit = fields.Char('Unit')
    min = fields.Float('Minimum')
    max = fields.Float('Maximum')
    comments = fields.Text('Comments')
    patient_id = fields.Many2one(related='task_id.patient_id', store=True)
    name = fields.Char(related='task_id.name')
    result_date = fields.Datetime(related='task_id.result_date', store=True)

    @api.model
    def create_result_line(self, task_id, dict):
        return self.create({
            'task_id': task_id,
            'parameter_id': self.env['project.tags'].search([('name', '=', dict.get('name'))], limit=1).id,
            'value': dict.get('value'),
            'min': dict.get('min'),
            'max': dict.get('max'),
            'unit': dict.get('unit')
        })
