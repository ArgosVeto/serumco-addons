# -*- coding: utf-8 -*-

from odoo import models, fields, registry, api, _
from . import tools
import csv
import io
import base64

import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'



    def get_partner_by_name(self, name):
        if not name:
            return False
        return self.search([('name', '=', name)], limit=1).id

    @api.model
    def get_childs(self, row):
        country_obj = self.env['res.country']
        if not self.search([('type', '=', 'delivery' if row.get('child_ids/type') == 'Shipping address' else 'invoice'), ('street', '=', row.get('child_ids/street'))]):
            return [(0, 0, {
                # 'name': row.get('Contact / Associated business / Commercial 1'),
                'type': 'delivery' if row.get('child_ids/type') == 'Shipping address' else 'invoice',
                'street': row.get('child_ids/street'),
                'street2': row.get('child_ids/street2'),
                'city': row.get('child_ids/city'),
                'zip': row.get('child_ids/zip'),
                'country_id': country_obj.get_country_by_name(row.get('Contacts/pays')),
            })]
        else:
            return False

    def schedule_import_partner(self, **kwargs):
        with api.Environment.manage():
            with registry(self._cr.dbname).cursor() as new_cr:
                logger = self._context['logger']
                self = self.with_env(self.env(cr=new_cr))
                template_obj = self.env['ir.model.import.template']
                position_obj = self.env['account.fiscal.position']
                partner_obj = self.env['res.partner']
                res_users_obj = self.env['res.users']
                template = template_obj.browse(kwargs.get('import_id'))
                is_error = False
                if template.export_xls:
                    csv_data = io.StringIO()
                    csv_writer = csv.writer(csv_data, delimiter=';')

                    csv_headers = [_('ID externe'),
                                   _('Nom'),
                                   _('Société liée'),
                                   _('Type de société'),
                                   _('Est un fournisseur'),
                                   _('Est un client'),
                                   _('Contact / Associated business / Commercial 1'),
                                   _('Notes'),
                                   _('Position fiscale'),
                                   _('APE'),
                                   _('TVA'),
                                   _('Actif/ve'),
                                   _('Téléphone'),
                                   _('Site web'),
                                   _('Courriel'),
                                   _('child_ids/type'),
                                   _('child_ids/street'),
                                   _('child_ids/street2'),
                                   _('child_ids/city'),
                                   _('child_ids/zip'),
                                   _('Contacts/pays'),
                                   _(u'Erreur constatée'),
                                   ]
                    csv_writer.writerow(csv_headers)

                try:
                    if not template:
                        logger.error(_('There is nothing to import.'))
                        return
                    # scsv = base64.decodebytes(template.import_file).decode('utf-8')
                    scsv = base64.decodebytes(template.import_file).decode('ISO-8859-1')
                    csvfile = io.StringIO(scsv)
                    reader = csv.DictReader(csvfile, delimiter=';')
                    logger.info(_("Start Import Of %s" % template.file_name))
                    for row in reader:
                        try:
                            vals = {
                                'name': row.get('Nom'),
                                'parent_id': row.get('Société liée / ID'),
                                'company_type': row.get('Type de société', 'person').lower(),
                                'supplier': tools.str2bool(row.get('Est un fournisseur')),
                                'customer': tools.str2bool(row.get('Est un client')),
                                'active': tools.str2bool(row.get('Actif/ve')),
                                'comment': row.get('Notes'),
                                'property_account_position_id': position_obj.get_position_by_name(
                                    row.get('Position fiscale')),
                                'ape': row.get('APE'),
                                'vat': row.get('TVA'),
                                'child_ids': self.get_childs(row),
                                'phone': row.get('Téléphone'),
                                'website': row.get('Site web'),
                                'email': row.get('Courriel'),
                                'ref': row.get('ID externe'),
                                'user_id': res_users_obj.get_user_by_name(
                                    row.get('Contact / Associated business / Commercial 1')),
                            }
                            partner = partner_obj.search([('ref', '=', row.get('ID externe'))], limit=1)
                            if partner:
                                partner.write(vals)
                            else:
                                partner_obj.create(vals)
                            if reader.line_num % 150 == 0:
                                logger.info(_("Import in progress ... %s lines treated." % reader.line_num))
                            self._cr.commit()
                        except Exception as error:
                            if template.export_xls:
                                error_line = [row.get('ID externe'),
                                              row.get('Nom'),
                                              row.get('Société liée'),
                                              row.get('Type de société'),
                                              row.get('Est un fournisseur'),
                                              row.get('Est un client'),
                                              row.get('Contact / Associated business / Commercial 1'),
                                              row.get('Notes'),
                                              row.get('Position fiscale'),
                                              row.get('APE'),
                                              row.get('TVA'),
                                              row.get('Actif/ve'),
                                              row.get('Téléphone'),
                                              row.get('Site web'),
                                              row.get('Courriel'),
                                              row.get('child_ids/type'),
                                              row.get('child_ids/street'),
                                              row.get('child_ids/street2'),
                                              row.get('child_ids/city'),
                                              row.get('child_ids/zip'),
                                              row.get('Contacts/pays'),
                                              repr(error)
                                              ]
                                if not is_error:
                                    is_error = True

                                csv_writer.writerow(error_line)
                            logger.error(repr(error))
                            new_cr.rollback()
                    logger.info(_("End Import Of %s Successfully." % template.file_name))
                except Exception as error:
                    logger.error(repr(error))
                    new_cr.rollback()

                if is_error and template.export_xls:
                    binary_file = base64.b64encode(csv_data.getvalue().encode('utf-8-sig'))
                    file_name = 'RES_PARTNER_ERREURS_%s.csv' % fields.Datetime.now().replace(':', '').replace('-','').replace(
                        ' ', '')
                    self.add_attachment(template.id, binary_file, file_name)
        return True

    @api.model
    def add_attachment(self, res_id, file, filename):
        """ add attachment """
        attach_obj = self.env['ir.attachment']
        attach_obj.create({
            'type': 'binary',
            'res_model': 'ir.model.import.template',
            'res_id': res_id,
            'datas': file,
            'name': filename,
            'datas_fname': filename,
        })
        return True
