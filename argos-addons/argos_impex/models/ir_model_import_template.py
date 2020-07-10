# -*- coding: utf-8 -*-

from odoo import fields, models


class IrModelImportTemplate(models.Model):
    _inherit = 'ir.model.import.template'

    is_remote_import = fields.Boolean('Import from FTP')
    server_ftp_id = fields.Many2one('server.ftp', 'Server FTP', ondelete='restrict', index=True)
