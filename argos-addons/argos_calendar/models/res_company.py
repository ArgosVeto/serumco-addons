# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    hospital_icon = fields.Binary(string='Hospital')
    hour_icon = fields.Binary(string='Hour')
    invoice_icon = fields.Binary(string='Invoice')
    medical_icon = fields.Binary(string='Medical')
