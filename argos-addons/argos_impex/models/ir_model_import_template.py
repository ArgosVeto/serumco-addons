# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID


class IrModelImportTemplate(models.AbstractModel):
    _inherit = 'ir.model.import.template'

    is_remote_import = fields.Boolean(string='Import from FTP')
    remote_url = fields.Char(string="URL")
    remote_login = fields.Char(string="Login")
    remote_pwd = fields.Char(string="Password")
    remote_directory = fields.Char(string="Directory", default="/ARGOS/IMPORT", required=True,
                                   help="This field must be completed as follows: "
                                        "/path/to/folder/which/contain/the files. "
                                        "Don't forget to put '/' at the beginning of the paths.")
