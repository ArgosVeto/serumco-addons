# -*- coding: utf-8 -*-

import base64
import io
import csv
from odoo import models, registry, api, _
from odoo.addons.argos_base.models import tools


class PassportPassport(models.Model):
    _inherit = 'passport.passport'

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
                    passport_obj = self.env['passport.passport']
                    patient_obj = self.env['res.partner']
                    category_obj = self.env['res.partner.category']
                    content = base64.decodebytes(template.import_file).decode('utf-8-sig')
                    csvfile = io.StringIO(content)
                    reader = csv.DictReader(csvfile, delimiter=';')
                    logger = logger or self._context['logger']
                    errors = []
                    lines = []
                    for row in reader:
                        try:
                            delivery_date = tools.format_date(row.get('dateDelivery'))
                            patient = patient_obj.search([('gmvet_id', '=', row.get('patient_id')), ('contact_type', '=', 'patient')],
                                                         limit=1)
                            species = row.get('species') and category_obj._get_category_by_name(row.get('species'), 'patient').id or False
                            vals = {
                                'gmvet_id': row.get('id'),
                                'address': row.get('address'),
                                'city': row.get('city'),
                                'delivery_date': delivery_date,
                                'identification': row.get('identification'),
                                'number': row.get('number'),
                                'status': row.get('status'),
                                'zip_code': row.get('zipCode'),
                                'name': row.get('number'),
                                'patient_ids': patient and [(4, patient.id)] or False,
                                'species_id': species
                            }
                            passport = passport_obj.search([('gmvet_id', '=', row.get('id'))], limit=1)
                            if passport:
                                passport.write(vals)
                            else:
                                passport_obj.create(vals)
                            if reader.line_num % 100 == 0:
                                logger.info(_('Import in progress ... %s lines treated.') % reader.line_num)
                            lines.append(reader.line_num)
                            self._cr.commit()
                        except Exception as e:
                            logger.error(repr(e))
                            errors.append((row, repr(e)))
                            new_cr.rollback()
                except Exception as e:
                    logger.error(repr(e))
                    new_cr.rollback()
                self.env['product.template'].manage_import_report('passport', lines, template, errors, logger)
        return True
