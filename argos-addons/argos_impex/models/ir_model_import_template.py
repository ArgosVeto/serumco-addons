# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import fields, models


class IrModelImportTemplate(models.Model):
    _inherit = 'ir.model.import.template'

    sequence = fields.Integer('Sequence')
    is_remote_import = fields.Boolean('Import from FTP')
    server_ftp_id = fields.Many2one('server.ftp', 'Server FTP', ondelete='restrict', index=True)

    def create_cron(self, **kwargs):
        for record in self:
            date = (fields.Datetime.now() + relativedelta(day=31)).strftime('%Y-%m-%d 00:00:00')
            kwargs.update({'priority': record.sequence, 'nextcall': fields.Datetime.from_string(date)})
            super(IrModelImportTemplate, record).create_cron(**kwargs)
        return True
