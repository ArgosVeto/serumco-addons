# -*- coding: utf-8 -*-

import base64
import io
import csv
from odoo import models, fields, registry, api, _


class PathologyCategory(models.Model):
    _inherit = 'pathology.category'

    @api.model
    def schedule_import_process(self, **kwargs):
        with api.Environment.manage():
            with registry(self._cr.dbname).cursor() as new_cr:
                self = self.with_env(self.env(cr=new_cr))
                logger = self._context['logger']
                try:
                    template = self.env['ir.model.import.template'].browse(kwargs['template_id'])
                    if not template.import_file:
                        logger.error(_('There is nothing to import.'))
                        return True
                    pathology_category_obj = self.env['pathology.category']
                    content = base64.decodebytes(template.import_file).decode('utf-8-sig')
                    csvfile = io.StringIO(content)
                    reader = csv.DictReader(csvfile, delimiter=';')
                    logger = logger or self._context['logger']
                    errors = []
                    lines = []
                    for row in reader:
                        try:
                            vals = {
                                'name': row.get('name'),
                                'type': row.get('type'),
                                'typical_workshop': row.get('atelierType'),
                                'gmvet_id': row.get('id'),
                            }
                            pathology_category = pathology_category_obj.search([('gmvet_id', '=', row.get('id'))], limit=1)
                            if pathology_category:
                                pathology_category.write(vals)
                            else:
                                pathology_category_obj.create(vals)
                            lines.append(reader.line_num)
                            self._cr.commit()
                        except Exception as e:
                            logger.error(repr(e))
                            errors.append((row, repr(e)))
                            self._cr.rollback()
                except Exception as e:
                    logger.error(repr(e))
                    self._cr.rollback()
                self.env['product.template'].manage_import_report('pathology-category', lines, template, errors, logger)
        return True