# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    appointment_constraint = fields.Boolean(string='Appointment constraint')
