# -*- encoding: utf-8 -*-

from odoo import models, fields, _


class IrModelImportTemplate(models.Model):
    _inherit = 'ir.model.import.template'

    import_file = fields.Binary('File', attachment=True)
    file_name = fields.Char('Filename')
    export_xls = fields.Boolean('Generate errors file')
    attachment_ids = fields.Many2many('ir.attachment', 'model_import_template_attachment_rel', 'template_id',
                                      'attachment_id', 'Documents', readonly=True)
