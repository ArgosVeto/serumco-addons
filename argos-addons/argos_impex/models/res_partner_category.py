# -*- coding: utf-8 -*-

import base64
import io
import csv
from odoo import models, fields, registry, api, _


class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    @api.model
    def get_partner_category_by_gmvet_id(self, gmvet_id):
        category = self.search([('gmvet_id', '=', gmvet_id)], limit=1)
        if category:
            return category
        return False

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
                    category_obj = self.env['res.partner.category']
                    content = base64.decodebytes(template.import_file).decode('utf-8-sig')
                    csvfile = io.StringIO(content)
                    reader = csv.DictReader(csvfile, delimiter=';')
                    logger = logger or self._context['logger']
                    errors = []
                    lines = []
                    for row in reader:
                        try:
                            category = category_obj._get_category_by_name(row.get('name'), 'patient')
                            category.write({'gmvet_id': row.get('id')})
                            lines.append(reader.line_num)
                            self._cr.commit()
                        except Exception as e:
                            logger.error(repr(e))
                            errors.append((row, repr(e)))
                            new_cr.rollback()
                except Exception as e:
                    logger.error(repr(e))
                    new_cr.rollback()
                self.env['product.template'].manage_import_report('species', lines, template, errors, logger)
        return True