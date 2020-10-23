# -*- coding: utf-8 -*-

from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    type = fields.Selection([('internal', 'Internal'), ('external', 'External'), ('outsourcing', 'Outsourcing')],
                            'Analysis Type', default='internal')
    task_type = fields.Selection([('analysis', 'Analysis'), ('imagery', 'Imagery')], 'Exam Type')
    order_id = fields.Many2one('sale.order', 'Order')
    patient_id = fields.Many2one(related='order_id.patient_id')
    species_id = fields.Many2one(related='patient_id.species_id')
    equipment_id = fields.Many2one('maintenance.equipment', 'Equipment')
    note = fields.Char('Note')
    state = fields.Selection([('draft', 'Draft'), ('waiting', 'Waiting'), ('done', 'Done')],
                             default='draft', string='Exam State')
    task_id = fields.Many2one('project.task', 'Analysis Request')
    result_ids = fields.One2many('project.task', 'task_id', 'Result')
    result_line_ids = fields.One2many('project.task.line', 'task_id', 'Result Lines')
    result_date = fields.Datetime('Result Date', default=lambda self: fields.Datetime.now())
    comments = fields.Char('Comments')
    imagery = fields.Binary('Imagery')

    def action_open_result(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_id': self.result_ids.id,
            'res_model': 'project.task',
            'views': [[self.env.ref('argos_sale_project.project_task_result_view_form').id, 'form']],
            'context': {'create': False},
        }

    def action_launch_analysis(self):
        self.ensure_one()
        if self.task_type == 'analysis':
            self.create({
                'name': self.name,
                'task_id': self.id,
                'task_type': self.task_type,
                'order_id': self.order_id.id,
                'equipment_id': self.equipment_id.id
            })
        if self.equipment_id:
            self.write({'state': 'waiting'})
        else:
            self.write({'state': 'done'})
        if self.type in ['outsourcing', 'external']:
            action = self.env.ref('purchase.purchase_rfq').read()[0]
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            return action
        return True
