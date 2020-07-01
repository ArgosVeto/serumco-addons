# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018 ArkeUp (<http://www.arkeup.fr>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api, _
from odoo.addons.smile_impex.tools import with_impex_cursor
from odoo.exceptions import UserError


class IrModelImportTemplate(models.Model):
    _inherit = 'ir.model.import.template'

    import_file = fields.Binary('File', attachment=True)
    file_name = fields.Char('Filename')
    export_xls = fields.Boolean(string="Générer fichier d'erreurs")


class IrModelExportTemplate(models.Model):
    _inherit = 'ir.model.export.template'

    path = fields.Char(string='Path')
    filename = fields.Char(string='Filename')


    def download_export(self):
        param = self.env['ir.config_parameter'].search([('key', '=', 'web.base.url.export')], limit=1)
        if param:
            if self.path and self.filename:
                return {
                    "type": "ir.actions.act_url",
                    "url": param.value + '?id=' + str(self.id),
                    "target": "self",
                }
            else:
                raise UserError(_('No file to download'))
        else:
            raise UserError(_('Please add key web.base.url.export to parameter'))
