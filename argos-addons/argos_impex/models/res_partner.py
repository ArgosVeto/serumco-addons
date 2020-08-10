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
    _inherit = 'res.partner'

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
                    partner_title_obj = self.env['res.partner.title']
                    content = base64.decodebytes(template.import_file).decode('utf-8-sig')
                    csvfile = io.StringIO(content)
                    reader = csv.DictReader(csvfile, delimiter=';')
                    errors = []
                    lines = []
                    header = []
                    for row in reader:
                        try:
                            number = row.get('numero')
                            if not number:
                                logger.error(_('The numero is needed to continue processing this contact. Line %s' % reader.line_num))
                                errors.append((row, _('The numero column is missed!')))
                                continue
                            phone, mobile = tools.split_consolidated_phones(row.get('consolidatedPhones'))
                            vals = {
                                'name': row.get('consolidatedData'),
                                'first_name': row.get('firstname'),
                                'last_name': row.get('lastname'),
                                'phone': phone,
                                'mobile': mobile,
                                'comment': row.get('memo'),
                                'email': row.get('email'),
                                'siret': row.get('siret'),
                                'send_letter': tools.str2bool(row.get('mailingByPostMail')),
                                'send_sms': tools.str2bool(row.get('mailingBySMS')),
                                'send_email': tools.str2bool(row.get('mailingByEmail')),
                                'title': partner_title_obj.get_title_by_shortcut(row.get('title')),
                                'active': tools.str2bool(row.get('deleted'))
                            }
                            partner = self.search([('ref', '=', number)], limit=1)
                            if partner:
                                partner.write(vals)
                            else:
                                vals.update({'ref': number})
                                self.create(vals)
                            if reader.line_num % 500 == 0:
                                logger.info(_('Import in progress ... %s lines treated.') % reader.line_num)
                            lines.append(reader.line_num)
                            new_cr.commit()
                        except Exception as e:
                            logger.error(repr(e))
                            errors.append((row, repr(e)))
                            self._cr.rollback()
                    self.env['product.template'].manage_import_report('contacts', lines, template, errors, logger)
                except Exception as e:
                    logger.error(repr(e))
                    errors.append((row, repr(e)))
                    new_cr.rollback()