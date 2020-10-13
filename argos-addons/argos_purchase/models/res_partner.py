# -*- coding: utf-8 -*-


from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    supplier_calendar_id = fields.Many2one('resource.calendar', 'Supplier Calendar', company_dependent=True)