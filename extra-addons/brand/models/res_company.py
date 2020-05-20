# # Copyright (C) 2020 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    brand_use_level = fields.Selection([('no', 'Do not use brands on business document'), ('optional', 'Optional'),
                                        ('required', 'Required')], 'Brand Use Level', default='no')
