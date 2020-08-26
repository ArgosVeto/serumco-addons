# -*- coding: utf-8 -*-

import base64
import io
import csv
from odoo import models, fields, registry, api, _
from odoo.addons.argos_base.models import tools


class ResPartnerWeight(models.Model):
    _inherit = 'res.partner.weight'

    gmvet_id = fields.Char('Gmvet ID')

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
                    weight_obj = self.env['res.partner.weight']
                    patient_obj = self.env['res.partner']
                    content = base64.decodebytes(template.import_file).decode('utf-8-sig')
                    csvfile = io.StringIO(content)
                    reader = csv.DictReader(csvfile, delimiter=';')
                    logger = logger or self._context['logger']
                    errors = []
                    lines = []
                    for row in reader:
                        try:
                            patient = patient_obj.search([('contact_type', '=', 'patient'), ('gmvet_id', '=', row.get('patient_id'))],
                                                         limit=1)
                            if not patient:
                                logger.info(_('Can''t assign weight. Missing patient (Patient Gmvet id: %s)!') % (row.get('patient_id')))
                                errors.append((row, _('Cant''t assign weight. Missing patient (Patient Gmvet id: %s)!') % (row.get(
                                    'patient_id'))))
                                continue
                            date = tools.format_date(row.get('date'))
                            vals = {
                                'gmvet_id': row.get('id'),
                                'date': date,
                                'values': float(row.get('value')),
                                'source': row.get('source'),
                                'note': row.get('commentaire'),
                                'partner_id': patient.id
                            }
                            if row.get('id') in patient.weight_ids.mapped('gmvet_id'):
                                weight = patient.weight_ids.filtered(lambda j: j.gmvet_id == row.get('id'))
                                patient.write({'weight_ids': [(1, weight.id, vals)]})
                            else:
                                patient.write({'weight_ids': [(0, 0, vals)]})
                            if reader.line_num % 500 == 0:
                                logger.info(_('Import in progress ... %s lines treated.') % reader.line_num)
                            lines.append(reader.line_num)
                            self._cr.commit()
                        except Exception as e:
                            logger.info(repr(e))
                            errors.append((row, repr(e)))
                            self._cr.rollback()
                except Exception as e:
                    logger.error(repr(e))
                    errors.append((row, repr(e)))
                    self._cr.rollback()
                self.env['product.template'].manage_import_report('weight', lines, template, errors, logger)
        return True