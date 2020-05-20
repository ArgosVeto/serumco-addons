# # Copyright (C) 2020 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    brand_use_level = fields.Selection([('no', 'Do not use brands on business document'),
                                        ('optional', 'Optional'),
                                        ('required', 'Required')], 'Brand Use Level',
                                       default='no', related='company_id.brand_use_level', readonly=False)
