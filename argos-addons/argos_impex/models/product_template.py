# -*- coding: utf-8 -*-


import csv
import io
import base64

from odoo import models, fields, registry, api, _
from odoo.addons.argos_base.models import tools


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def manage_supinfo(self, row={}):
        self.ensure_one()
        if not row.get('fournisseur'):
            return
        partner_obj = self.env['res.partner']
        if not row:
            return False
        supplier = partner_obj.search([('name', '=', row.get('fournisseur'))], limit=1)
        if not supplier:
            supplier = partner_obj.create({'name': row.get('fournisseur')})
        sellers = self.seller_ids.filtered(lambda s: s.name == supplier)
        if not sellers:
            vals = [(0, 0, {
                'name': supplier.id,
                'product_tmpl_id': self.id,
                'sequence': 0})]
            self.seller_ids = vals
            return True
        return True

    def schedule_import_process(self, **kwargs):
        with api.Environment.manage():
            with registry(self._cr.dbname).cursor() as new_cr:
                self = self.with_env(self.env(cr=new_cr))
                logger = self._context['logger']
                model_import_obj = self.env['ir.model.import.template']
                try:
                    template = model_import_obj.browse(kwargs.get('template_id'))
                    if not template:
                        logger.error(_('There is nothing to import.'))
                        return True
                    if template.is_remote_import:
                        if not template.server_ftp_id:
                            return
                        template.server_ftp_id.with_context(template=template.id, logger=logger, source='produit-general').retrieve_data()
                    elif template.import_file:
                        scsv = base64.decodebytes(template.import_file).decode('utf-8-sig')
                        self.processing_import_data(scsv, template)
                except Exception as e:
                    logger.error(repr(e))
                    self._cr.rollback()

    @api.model
    def processing_import_data(self, content=None, template=False, logger=False):
        """
        :param content:
        :param template:
        :return:
        """
        if not content or not template:
            return
        category_obj = self.env['product.category']
        csvfile = io.StringIO(content)
        reader = csv.DictReader(csvfile, delimiter=';')
        logger = logger or self._context['logger']
        errors = []
        lines = []
        for row in reader:
            try:
                if not row.get('code'):
                    logger.error(_('The code is needed to continue processing this article. Line %s' % reader.line_num))
                    errors.append((row, _('The code column is missed!')))
                    continue
                if not row.get('libelle'):
                    logger.error(_('The libelle is needed to continue processing this article. Line %s' % reader.line_num))
                    errors.append((row, _('The libelle column is missed!')))
                    continue
                vals = {
                    'default_code': row.get('code'),
                    'name': row.get('libelle'),
                    'description': row.get('presentation'),
                    'weight': row.get('poids'),
                    'mother_class': row.get('classe'),
                    'sub_child_class': row.get('ssClasse'),
                    'child_class': row.get('sClasse'),
                    'categ_id': category_obj._get_category_by_name(row.get('categorie')),
                    'gtin': row.get('gtin'),
                    'ean': row.get('ean'),
                    'cip': row.get('cip'),
                    'sale_ok': True,
                    'purchase_ok': True,
                    'type': 'product',
                }
                product = self.search([('default_code', '=', row.get('code'))], limit=1)
                try:
                    if product:
                        product.write(vals)
                    else:
                        product = self.create(vals)
                    if reader.line_num % 150 == 0:
                        logger.info(_('Import in progress ... %s lines treated.' % reader.line_num))
                    product.manage_supinfo(row)
                    lines.append(reader.line_num)
                    self._cr.commit()
                except Exception as e:
                    logger.error(repr(e))
                    errors.append((row, repr(e)))
                    self._cr.rollback()
            except Exception as e:
                logger.error(repr(e))
                errors.append((row, repr(e)))
                self._cr.rollback()
        self.manage_import_report('produit-general', lines, template, errors, logger)
        return True

    @api.model
    def generate_errors_file(self, source=False, template=False, data=[]):
        """
        Generate the file with all error lines
        :param template:
        :param data:
        :return:
        """
        if not data or not template or not source:
            return
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data, delimiter =';')
        if source == 'produit-general':
            csv_writer.writerow(['code', 'libelle', 'presentation', 'fournisseur', 'poids', 'classe', 'ssClasse', 'sClasse', 'categorie',
                                 'sCategorie', 'ssCategorie', 'gtin', 'ean', 'cip', 'error detail'])
            for row, error in data:
                csv_writer.writerow([row.get('code'), row.get('libelle'), row.get('presentation'), row.get('fournisseur'), row.get('poids'),
                                     row.get('classe'), row.get('ssClasse'), row.get('sClasse'), row.get('categorie'), row.get('sCategorie'),
                                     row.get('ssCategorie'), row.get('gtin'), row.get('ean'), row.get('cip'), error])
        elif source == 'tarif':
            csv_writer.writerow(['code', 'tarif'])
            for row, error in data:
                csv_writer.writerow([row.get('code'), row.get('tarif'), error])

        elif source == 'association':
            csv_header = ['code', 'codeA', 'error detail']
            csv_writer.writerow(csv_header)
            for row, error in data:
                csv_writer.writerow([row.get('code'), row.get('codeA'), error])

        elif source == 'documentation':
            csv_header = ['code', 'type', 'doc', 'error detail']
            csv_writer.writerow(csv_header)
            for row, error in data:
                csv_writer.writerow([row.get('code'), row.get('type'), row.get('doc'), error])

        elif source == 'regroupement':
            csv_header = ['code', 'regroupement', 'ordre', 'error detail']
            csv_writer.writerow(csv_header)
            for row, error in data:
                csv_writer.writerow([row.get('code'), row.get('regroupement'), row.get('ordre'), error])

        content = base64.b64encode(csv_data.getvalue().encode('utf-8'))
        date = str(fields.Datetime.now()).replace(':', '').replace('-', '').replace(' ', '')
        filename = '%s_%s.csv' % (source, date)
        self.create_attachment(template, content, filename)

    @api.model
    def create_attachment(self, template=False, content=None, filename=False):
        """
        Create error file in attachment
        :param template:
        :param content:
        :param filename:
        :return:²
        """
        if not template or not content:
            return False
        model = 'ir.model.import.template'
        template.attachment_ids = [(0, 0, {'type': 'binary', 'res_model': model,
                                           'res_id': template.id, 'datas': content, 'name': filename})]
        return True

    @api.model
    def schedule_import_list_price_process(self, **kwargs):
        with api.Environment.manage():
            with registry(self._cr.dbname).cursor() as new_cr:
                self = self.with_env(self.env(cr=new_cr))
                logger = self._context['logger']
                model_import_obj = self.env['ir.model.import.template']
                try:
                    template = model_import_obj.browse(kwargs.get('template_id'))
                    if not template:
                        logger.error(_('There is nothing to import.'))
                        return
                    if template.is_remote_import:
                        if not template.server_ftp_id:
                            return
                        template.server_ftp_id.with_context(template=template.id, logger=logger, source='tarif').retrieve_data()
                    elif template.import_file:
                        scsv = base64.decodebytes(template.import_file).decode('utf-8-sig')
                        self.processing_import_list_price_data(scsv, template)
                except Exception as e:
                    logger.error(repr(e))
                    self._cr.rollback()

    @api.model
    def processing_import_list_price_data(self, content=None, template=False, logger=False):
        """
        Import price list of products
        :param content:
        :param template:
        :param logger:
        :return:
        """
        if not content or not template:
            return False
        csvfile = io.StringIO(content)
        reader = csv.DictReader(csvfile, delimiter=';')
        logger = logger or self._context['logger']
        errors = []
        lines = []
        for row in reader:
            try:
                if not row.get('code'):
                    logger.error(_('The code is needed to continue processing this article. Line %s' % reader.line_num))
                    errors.append((row, _('The code column is missed!')))
                    continue
                vals = {
                    'default_code': row.get('code'),
                    'list_price': row.get('tarif')
                }
                product = self.search([('default_code', '=', row.get('code'))], limit=1)
                try:
                    if product:
                        product.write(vals)
                    else:
                        logger.info(_('No product with code %s found.') % row.get('code'))
                        errors.append((row, _('No product with code %s found.') % row.get('code')))
                    if reader.line_num % 150 == 0:
                        logger.info(_('Import in progress ... %s lines treated.' % reader.line_num))
                    lines.append(reader.line_num)
                    self._cr.commit()
                except Exception as e:
                    logger.error(repr(e))
                    errors.append((row, repr(e)))
                    self._cr.rollback()
            except Exception as e:
                logger.error(repr(e))
                errors.append((row, repr(e)))
                self._cr.rollback()
        self.manage_import_report('tarif', lines, template, errors, logger)
        return True

    @api.model
    def schedule_import_association_process(self, **kwargs):
        with api.Environment.manage():
            with registry(self._cr.dbname).cursor() as new_cr:
                self = self.with_env(self.env(cr=new_cr))
                logger = self._context['logger']
                model_import_obj = self.env['ir.model.import.template']
                try:
                    template = model_import_obj.browse(kwargs.get('template_id'))
                    if not template:
                        logger.error(_('There is nothing to import.'))
                        return
                    if template.is_remote_import:
                        if not template.server_ftp_id:
                            return
                        template.server_ftp_id.with_context(template=template.id, logger=logger,
                                                            source='association').retrieve_data()
                    elif template.import_file:
                        scsv = base64.decodebytes(template.import_file).decode('utf-8-sig')
                        self.processing_import_association_data(scsv, template)
                except Exception as e:
                    logger.error(repr(e))
                    self._cr.rollback()

    @api.model
    def processing_import_association_data(self, content=None, template=False, logger=False):
        """
        Import association of products
        :param content:
        :param template:
        :param logger:
        :return:
        """
        if not content or not template:
            return False
        csvfile = io.StringIO(content)
        reader = csv.DictReader(csvfile, delimiter=';')
        logger = logger or self._context['logger']
        errors = []
        lines = []
        for row in reader:
            try:
                if not row.get('code'):
                    logger.error(_('The code is needed to continue processing this article. Line %s' % reader.line_num))
                    errors.append((row, _('The code column is missed!')))
                    continue
                if not row.get('codeA'):
                    logger.error(
                        _('The codeA is needed to continue processing this article. Line %s' % reader.line_num))
                    errors.append((row, _('The codeA column is missed!')))
                    continue
                vals = {
                    'default_code': row.get('code'),
                    'association_code': row.get('codeA'),
                }
                product = self.search([('default_code', '=', row.get('code'))], limit=1)
                try:
                    if product:
                        product.write(vals)
                    else:
                        logger.info(_('No product with code %s found.') % row.get('code'))
                        errors.append((row, _('No product with code %s found.') % row.get('code')))
                    if reader.line_num % 150 == 0:
                        logger.info(_('Import in progress ... %s lines treated.' % reader.line_num))
                    lines.append(reader.line_num)
                    self._cr.commit()
                except Exception as e:
                    logger.error(repr(e))
                    errors.append((row, repr(e)))
                    self._cr.rollback()
            except Exception as e:
                logger.error(repr(e))
                errors.append((row, repr(e)))
                self._cr.rollback()
        self.manage_import_report('association', lines, template, errors, logger)
        return True

    @api.model
    def schedule_import_documentation_process(self, **kwargs):
        with api.Environment.manage():
            with registry(self._cr.dbname).cursor() as new_cr:
                self = self.with_env(self.env(cr=new_cr))
                logger = self._context['logger']
                model_import_obj = self.env['ir.model.import.template']
                try:
                    template = model_import_obj.browse(kwargs.get('template_id'))
                    if not template:
                        logger.error(_('There is nothing to import.'))
                        return
                    if template.is_remote_import:
                        if not template.server_ftp_id:
                            return
                        template.server_ftp_id.with_context(template=template.id, logger=logger, source='documentation').retrieve_data()
                    elif template.import_file:
                        scsv = base64.decodebytes(template.import_file).decode('utf-8-sig')
                        self.processing_import_documentation_data(scsv, template)
                except Exception as e:
                    logger.error(repr(e))
                    self._cr.rollback()

    @api.model
    def processing_import_documentation_data(self, content=None, template=False, logger=False):
        """
        Import documention of products
        :param content:
        :param template:
        :param logger:
        :return:
        """
        if not content or not template:
            return False
        csvfile = io.StringIO(content)
        reader = csv.DictReader(csvfile, delimiter=';')
        logger = logger or self._context['logger']
        errors = []
        lines = []
        for row in reader:
            try:
                if not row.get('code'):
                    logger.error(_('The code is needed to continue processing this article. Line %s' % reader.line_num))
                    errors.append((row, _('The code column is missed!')))
                    continue
                if not row.get('type'):
                    logger.error(
                        _('The type is needed to continue processing this article. Line %s' % reader.line_num))
                    errors.append((row, _('The type column is missed!')))
                    continue
                vals = {
                    'default_code': row.get('code'),
                    'type': row.get('type'),
                    'description': row.get('doc'),
                }
                product = self.search([('default_code', '=', row.get('code'))], limit=1)
                try:
                    if product:
                        product.write(vals)
                    else:
                        logger.info(_('No product with code %s found.') % row.get('code'))
                        errors.append((row, _('No product with code %s found.') % row.get('code')))
                    if reader.line_num % 150 == 0:
                        logger.info(_('Import in progress ... %s lines treated.' % reader.line_num))
                    lines.append(reader.line_num)
                    self._cr.commit()
                except Exception as e:
                    logger.error(repr(e))
                    errors.append((row, repr(e)))
                    self._cr.rollback()
            except Exception as e:
                logger.error(repr(e))
                errors.append((row, repr(e)))
                self._cr.rollback()
        self.manage_import_report('documentation', lines, template, errors, logger)
        return True

    @api.model
    def schedule_import_regroupment_process(self, **kwargs):
        with api.Environment.manage():
            with registry(self._cr.dbname).cursor() as new_cr:
                self = self.with_env(self.env(cr=new_cr))
                logger = self._context['logger']
                model_import_obj = self.env['ir.model.import.template']
                try:
                    template = model_import_obj.browse(kwargs.get('template_id'))
                    if not template:
                        logger.error(_('There is nothing to import.'))
                        return
                    if template.is_remote_import:
                        if not template.server_ftp_id:
                            return
                        template.server_ftp_id.with_context(template=template.id, logger=logger, source='regroupement').retrieve_data()
                    elif template.import_file:
                        scsv = base64.decodebytes(template.import_file).decode('utf-8-sig')
                        self.processing_import_regroupment_data(scsv, template)
                except Exception as e:
                    logger.error(repr(e))
                    self._cr.rollback()

    @api.model
    def processing_import_regroupment_data(self, content=None, template=False, logger=False):
        """
        Import regroupment of products
        :param content:
        :param template:
        :param logger:
        :return:
        """
        if not content or not template:
            return False
        csvfile = io.StringIO(content)
        reader = csv.DictReader(csvfile, delimiter=';')
        logger = logger or self._context['logger']
        errors = []
        lines = []
        for row in reader:
            try:
                if not row.get('code'):
                    logger.error(_('The code is needed to continue processing this article. Line %s' % reader.line_num))
                    errors.append((row, _('The code column is missed!')))
                    continue
                vals = {
                    'default_code': row.get('code'),
                    'group': row.get('regroupement'),
                    'order': row.get('ordre'),
                }
                product = self.search([('default_code', '=', row.get('code'))], limit=1)
                try:
                    if product:
                        product.write(vals)
                    else:
                        logger.info(_('No product with code %s found.') % row.get('code'))
                        errors.append((row, _('No product with code %s found.') % row.get('code')))
                    if reader.line_num % 150 == 0:
                        logger.info(_('Import in progress ... %s lines treated.' % reader.line_num))
                    lines.append(reader.line_num)
                    self._cr.commit()
                except Exception as e:
                    logger.error(repr(e))
                    errors.append((row, repr(e)))
                    self._cr.rollback()
            except Exception as e:
                logger.error(repr(e))
                errors.append((row, repr(e)))
                self._cr.rollback()
        self.manage_import_report('regroupement', lines, template, errors, logger)
        return True

    @api.model
    def manage_import_report(self, source=False, lines=[], template=False, errors=[], logger=None):
        """
        :param lines:
        :param template:
        :param errors:
        :param logger:
        :return:
        """
        if lines:
            logger.info(_('Liste of lines imported successfully: %s') % str(lines))
        if errors and template.export_xls:
            self.generate_errors_file(source, template, errors)
            logger.info(_('Import finish with errors.\nGo to History Error Files tab to show the list of stranded lines.'))
            return False
        if not errors:
            logger.info(_('Import done successfully.'))
        return True
