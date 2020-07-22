# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, tools


class PlanningRole(models.Model):
    _inherit = 'planning.role'

    role_type = fields.Selection([('rdv', 'Rdv'), ('away', 'Away'), ('presence', 'Presence')], 'Role Type')

    @api.model
    def _get_role_by_type(self, type=False):
        return self.search([('role_type', '=', type)], limit=1)