# -*- coding: utf-8 -*-

import base64
import io
import csv
from odoo import models, fields, registry, api, _


class ResPartnerPathology(models.Model):
    _inherit = 'res.partner.pathology'

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
                    pathology_obj = self.env['res.partner.pathology']
                    pathology_category_obj = self.env['pathology.category']
                    content = base64.decodebytes(template.import_file).decode('utf-8-sig')
                    csvfile = io.StringIO(content)
                    reader = csv.DictReader(csvfile, delimiter=';')
                    logger = logger or self._context['logger']
                    errors = []
                    lines = []
                    for row in reader:
                        try:
                            pathology_category = pathology_category_obj.search([('gmvet_id', '=', row.get('categorie_id'))], limit=1)
                            vals = {
                                'name': row.get('name'),
                                'quartier': row.get('quartiers'),
                                'category_id': pathology_category and pathology_category.id or False,
                                'gmvet_id': row.get('id')
                            }
                            pathology = pathology_obj.search([('gmvet_id', '=', row.get('id'))], limit=1)
                            if pathology:
                                pathology.write(vals)
                            else:
                                pathology_obj.create(vals)
                            lines.append(reader.line_num)
                            self._cr.commit()
                        except Exception as e:
                            logger.error(repr(e))
                            errors.append((row, repr(e)))
                            new_cr.rollback()
                except Exception as e:
                    logger.error(repr(e))
                    new_cr.rollback()
                self.env['product.template'].manage_import_report('pathology', lines, template, errors, logger)
        return True