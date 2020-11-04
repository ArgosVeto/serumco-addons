# -*- coding: utf-8 -*-

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    billed = fields.Boolean('billed', default=False)
