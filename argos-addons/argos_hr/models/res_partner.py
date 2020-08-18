# -*- coding: utf-8 -*-

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    employee_id = fields.Many2one('hr.employee', 'Attending Veterinarian')
