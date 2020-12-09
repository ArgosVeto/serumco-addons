# -*- coding: utf-8 -*-

from odoo import fields, models,tools,api,_

class PosConfig(models.Model):
    _inherit = 'pos.config' 
    
    logout_time = fields.Integer(string='Logout Time(Sec.)',default="60")
    allow_auto_logout = fields.Boolean(string="Allow auto logout",default=True)

