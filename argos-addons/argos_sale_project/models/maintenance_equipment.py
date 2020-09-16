# -*- coding: utf-8 -*-

from odoo import fields, models

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    is_bidirectional = fields.Boolean('Is Bidirectional')