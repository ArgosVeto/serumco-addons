# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    many2one_limit_param = fields.Integer(string='Many2one item limit', config_parameter='many2one.limit')