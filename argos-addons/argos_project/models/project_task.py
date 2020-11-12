# -*- coding: utf-8 -*-

from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = 'project.task'

    sale_patient_id = fields.Many2one(related='sale_order_id.patient_id')

    def action_create_report(self):
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'type': 'ir.actions.act_window',
            'context': {'default_is_report': True},
            'target': 'new',
        }
