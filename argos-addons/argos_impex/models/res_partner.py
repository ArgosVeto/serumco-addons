# -*- coding: utf-8 -*-


import csv
import io
import base64

from odoo import models, fields, registry, api, _
from odoo.addons.argos_base.models import tools


class ResPartnerTitle(models.Model):
    _inherit = 'res.partner.title'

    def get_title_by_shortcut(self, shortcut=False):
        """

        :param shortcut:
        :return:
        """
        if not shortcut:
            return False
        title = self.search([('shortcut', '=', shortcut.strip())], limit=1)
        if title:
            return title.id
        return self.create({'name': shortcut, 'shortcut': shortcut}).id


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def process_import(self, **kwargs):
        with api.Environment.manage():
            with registry(self._cr.dbname).cursor() as new_cr:
                self = self.with_env(self.env(cr=new_cr))
                logger = self._context['logger']
                try:
                    import_template = self.env['ir.model.import.template'].browse(kwargs['template_id'])
                    if not import_template or not import_template.import_file:
                        logger.error(_('There is nothing to import.'))
                        return True
                    if import_template.import_file:
                        partner_title_obj = self.env['res.partner.title']
                        content = base64.decodebytes(import_template.import_file).decode('utf-8-sig')
                        csvfile = io.StringIO(content)
                        reader = csv.DictReader(csvfile, delimiter=';')
                        errors = []
                        lines = []
                        header = []
                        for row in reader:
                            try:
                                if not header:
                                    header = list(row.keys())
                                if not row.get('numero'):
                                    logger.error(_(
                                        'The numero is needed to continue processing this contact. Line %s' % reader.line_num))
                                    errors.append((row, _('The numero column is missed!')))
                                    continue
                                vals = {
                                    'gmvet_id': row.get('numero'),
                                    'name': row.get('consolidatedData'),
                                    'first_name': row.get('firstname'),
                                    'last_name': row.get('lastname'),
                                    'phone': self.split_consolidated_phones(row.get('consolidatedPhones'))[0],
                                    'mobile': self.split_consolidated_phones(row.get('consolidatedPhones'))[1],
                                    'comment': tools.str2none(row.get('memo')) or '' + '\n' + row.get('notificationMsg'),
                                    'email': row.get('email'),
                                    'siret': row.get('siret'),
                                    'send_letter': tools.str2bool(row.get('mailingByPostMail')),
                                    'send_sms': tools.str2bool(row.get('mailingBySMS')),
                                    'send_email': tools.str2bool(row.get('mailingByEmail')),
                                    'title': partner_title_obj.get_title_by_shortcut(row.get('title')),
                                }
                                partner = self.search([('gmvet_id', '=', row.get('numero'))])
                                vals = tools.str2none_dict(vals)
                                if not partner:
                                    partner = self.create(vals)
                                else:
                                    partner.write(vals)
                                new_cr.commit()
                                lines.append(reader.line_num)

                            except Exception as ex:
                                logger.error(repr(ex))
                                errors.append((row, repr(ex)))
                                self._cr.rollback()
                        tools.manage_import_report(header, lines, import_template, errors, logger)

                except Exception as e:
                    logger.error(repr(e))
                    errors.append((row, repr(e)))
                    new_cr.rollback()
        return True

    @api.model
    def split_consolidated_phones(self, value):
        if not '##' in value:
            return value, None
        return value.split('##')[0], value.split('##')[1]
