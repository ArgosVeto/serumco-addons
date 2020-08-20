# -*- coding: utf-8 -*-

import csv
import io
import base64
from odoo import models, fields, registry, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import UserError
from odoo.addons.argos_base.models import tools

FILE_DATETIME_FORMATS = ['%d/%m/%Y  %H:%M:%S', '%d/%m/%Y  %H:%M']


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
                    content = base64.decodebytes(template.import_file).decode('utf-8-sig')
                    if kwargs.get('source', False) == 'contacts':
                        return self.processing_import_contact(content, template, logger)
                    if kwargs.get('source', False) == 'patients':
                        return self.processing_import_patient(content, template, logger)
                    if kwargs.get('source', False) == 'owners':
                        return self.processing_import_patient_relationnal(content, template, logger)
                except Exception as e:
                    logger.error(repr(e))
                    new_cr.rollback()
        return True

    @api.model
    def processing_import_contact(self, content, template, logger=False):
        csvfile = io.StringIO(content)
        reader = csv.DictReader(csvfile, delimiter=';')
        logger = logger or self._context['logger']
        errors = []
        lines = []
        partner_title_obj = self.env['res.partner.title']
        for row in reader:
            try:
                number = row.get('numero')
                if not number:
                    logger.error(_('The numero is needed to continue processing this contact. Line %s' % reader.line_num))
                    errors.append((row, _('The numero column is missed!')))
                    continue
                phone, mobile = tools.split_consolidated_phones(row.get('consolidatedPhones'))
                vals = {
                    'ref': row.get('numero'),
                    'gmvet_id': row.get('id'),
                    'name': row.get('consolidatedData'),
                    'firstname': row.get('firstname'),
                    'lastname': row.get('lastname'),
                    'phone': phone,
                    'mobile': mobile,
                    'comment': row.get('memo'),
                    'email': row.get('email'),
                    'siret': row.get('siret'),
                    'send_letter': tools.str2bool(row.get('mailingByPostMail')),
                    'send_sms': tools.str2bool(row.get('mailingBySMS')),
                    'send_email': tools.str2bool(row.get('mailingByEmail')),
                    'title': partner_title_obj.get_title_by_shortcut(row.get('title')),
                    'active': not tools.str2bool(row.get('deleted'))
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
                self._cr.commit()
            except Exception as e:
                logger.error(repr(e))
                errors.append((row, repr(e)))
                self._cr.rollback()
        self.env['product.template'].manage_import_report('contacts', lines, template, errors, logger)
        return True

    @api.model
    def processing_import_patient(self, content, template, logger=False):
        csvfile = io.StringIO(content)
        reader = csv.DictReader(csvfile, delimiter=';')
        logger = logger or self._context['logger']
        errors = []
        lines = []
        parameter_obj = self.env['res.partner.parameter']
        partner_category_obj = self.env['res.partner.category']
        for row in reader:
            try:
                name = row.get('name')
                if not name:
                    logger.error(_('The name is needed to continue processing this contact. Line %s' % reader.line_num))
                    errors.append((row, _('The name column is missing!')))
                    continue
                birth_date = tools.date_from_params(int(row.get('birthYear')), int(row.get('birthMonth')), int(row.get('birthDay')))
                death_date = tools.format_date(row.get('dateOfDeath'))
                tattoo_date = tools.format_date(row.get('tatoo_date'))
                chip_date = tools.format_date(row.get('identificationDate'))
                issue_date = tools.format_date(row.get('passportDate'))
                race = parameter_obj._get_parameter_by_name(row.get('breed'), 'race')
                robe = parameter_obj._get_parameter_by_name(row.get('coat'), 'robe')
                species = self.retrieve_gmvet_data(partner_category_obj, False, row.get('species_id'))
                gender = self.retrieve_gmvet_data(parameter_obj, 'gender', row.get('gender_id'))
                insurance = self.retrieve_gmvet_data(parameter_obj, 'insurance', row.get('insurance_id'))
                chip_location = self.retrieve_gmvet_data(parameter_obj, 'chip', row.get('lieuTranspondeur_id'))
                tattoo_location = self.retrieve_gmvet_data(parameter_obj, 'tattoo', row.get('lieuTatouage_id'))

                vals = {
                    'contact_type': 'patient',
                    'name': row.get('name'),
                    'comment': row.get('note'),
                    'gmvet_id': row.get('id'),
                    'birthdate_date': birth_date,
                    'death_date': death_date,
                    'tattoo_date': tattoo_date,
                    'chip_date': chip_date,
                    'issue_date': issue_date,
                    'is_reproductive': tools.str2bool(row.get('breeding')),
                    'is_dangerous': tools.str2bool(row.get('dangerousDog')),
                    'is_dead': tools.str2bool(row.get('deceased')),
                    'is_missing': tools.str2bool(row.get('missing')),
                    'active': not tools.str2bool(row.get('deleted')),
                    'race_id': race and race.id or False,
                    'robe_id': robe and robe.id or False,
                    'species_id': species and species.id or False,
                    'gender_id': gender and gender.id or False,
                    'insurance_id': insurance and insurance.id or False,
                    'chip_location_id': chip_location and chip_location.id or False,
                    'tattoo_location_id': tattoo_location and tattoo_location.id or False,

                }
                patient = self.search([('gmvet_id', '=', row.get('id'))], limit=1)
                if patient:
                    patient.write(vals)
                else:
                    patient = self.create(vals)
                patient.manage_patient_diets(parameter_obj, row.get('feed'))
                patient.manage_patient_environment(parameter_obj, row.get('middleLife_id'))
                if reader.line_num % 500 == 0:
                    logger.info(_('Import in progress ... %s lines treated.') % reader.line_num)
                lines.append(reader.line_num)
                self._cr.commit()
            except Exception as e:
                logger.error(repr(e))
                errors.append((row, repr(e)))
                self._cr.rollback()
        self.env['product.template'].manage_import_report('patients', lines, template, errors, logger)
        return True

    @api.model
    def retrieve_gmvet_data(self, obj=False, type=False, gmvet_id=False):
        if not gmvet_id:
            return None
        elif obj._name == 'res.partner.parameter':
            parameter = obj.get_partner_parameter_by_gmvet_id(type, gmvet_id)
            if not parameter:
                raise UserError(_('The ''%s'' parameter with Gmvet ID %s is missing.') % (type, gmvet_id))
            return parameter
        elif obj._name == 'res.partner.category':
            category = obj.get_partner_category_by_gmvet_id(gmvet_id)
            if not category:
                raise UserError(_('The species with Gmvet ID %s is missing.') % (gmvet_id))
            return category
        return None

    @api.model
    def manage_patient_diets(self, parameter_obj, feeds):
        diet_ids = []
        if not feeds:
            return False
        for diet in feeds.split(','):
            diet_ids.append((4, parameter_obj._get_parameter_by_name(diet, 'diet').id))
        self.write({'diet_ids': diet_ids})
        return True

    @api.model
    def manage_patient_environment(self, parameter_obj, environment):
        environment_ids = []
        data = self.retrieve_gmvet_data(parameter_obj, 'living', environment)
        if not environment or not data:
            return False
        environment_ids.append((4, data.id))
        self.write({'environment_ids': environment_ids})
        return True

    @api.model
    def processing_import_patient_relationnal(self, content, template, logger=False):
        csvfile = io.StringIO(content)
        reader = csv.DictReader(csvfile, delimiter=';')
        logger = logger or self._context['logger']
        errors = []
        lines = []
        for row in reader:
            try:
                contact = self.with_context(active_test=False).search([('contact_type', '=', 'contact'), ('gmvet_id', '=',
                                                                                                     row.get('client_id'))],
                                                                      limit=1)
                patient = self.with_context(active_test=False).search([('contact_type', '=', 'patient'), ('gmvet_id', '=',
                                                                                                  row.get('patient_id'))], limit=1)
                if contact and patient:
                    patient.owner_ids = [(4, contact.id)]
                    contact.patient_ids = [(4, patient.id)]
                    self._cr.commit()
                else:
                    logger.error(_('Missing contact with gmvet id %s or patient with gmvet id %s') % (row.get('client_id'),
                                                                                                      row.get('patient_id')))
                    errors.append((row, _('Missing contact with gmvet id %s or patient with gmvet id %s') % (row.get('client_id'),
                                                                                                      row.get('patient_id'))))
                    continue
                if reader.line_num % 500 == 0:
                    logger.info(_('Import in progress ... %s lines treated.') % reader.line_num)
                lines.append(reader.line_num)
            except Exception as e:
                logger.error(repr(e))
                errors.append((row, repr(e)))
                self._cr.rollback()
        self.env['product.template'].manage_import_report('owners', lines, template, errors, logger)
        return True
