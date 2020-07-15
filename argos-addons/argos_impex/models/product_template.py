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
                        template.server_ftp_id.with_context(template=template.id, logger=logger, general_import=True).retrieve_data()
                    elif template.import_file:
                        scsv = base64.decodebytes(template.import_file).decode('utf-8-sig')
                        self.with_context(general_import=True).processing_import_data(scsv, template)
                except Exception as e:
                    logger.error(repr(e))
                    self._cr.rollback()

    def schedule_import_rate(self, **kwargs):
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
                        template.server_ftp_id.with_context(template=template.id, logger=logger, rate_import=True).retrieve_data()
                    elif template.import_file:
                        scsv = base64.decodebytes(template.import_file).decode('utf-8-sig')
                        self.with_context(rate_import=True).processing_import_data(scsv, template)
                except Exception as e:
                    logger.error(repr(e))
                    self._cr.rollback()

    def schedule_import_association(self, **kwargs):
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
                        template.server_ftp_id.with_context(template=template.id, logger=logger, association_import=True).retrieve_data()
                    elif template.import_file:
                        scsv = base64.decodebytes(template.import_file).decode('utf-8-sig')
                        self.with_context(association_import=True).processing_import_data(scsv, template)
                except Exception as e:
                    logger.error(repr(e))
                    self._cr.rollback()

    def schedule_import_documentation(self, **kwargs):
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
                        template.server_ftp_id.with_context(template=template.id, logger=logger, documentation_import=True).retrieve_data()
                    elif template.import_file:
                        scsv = base64.decodebytes(template.import_file).decode('utf-8-sig')
                        self.with_context(documentation_import=True).processing_import_data(scsv, template)
                except Exception as e:
                    logger.error(repr(e))
                    self._cr.rollback()

    def schedule_import_grouping(self, **kwargs):
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
                        template.server_ftp_id.with_context(template=template.id, logger=logger, grouping_import=True).retrieve_data()
                    elif template.import_file:
                        scsv = base64.decodebytes(template.import_file).decode('utf-8-sig')
                        self.with_context(grouping_import=True).processing_import_data(scsv, template)
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
        for row in reader:
            try:
                if self._context.get('grouping_import'):
                    if not row.get('code'):
                        logger.error(_('The code is needed to continue processing this article. Line %s' % reader.line_num))
                        errors.append((row, _('The code column is missed!')))
                        continue
                    vals = {
                        'default_code': row.get('code'),
                        'group': row.get('regroupement'),
                        'order': row.get('ordre'),
                    }

                if self._context.get('documentation_import'):
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

                if self._context.get('association_import'):
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

                if self._context.get('rate_import'):
                    if not row.get('code'):
                        logger.error(_('The code is needed to continue processing this article. Line %s' % reader.line_num))
                        errors.append((row, _('The code column is missed!')))
                        continue
                    if not row.get('tarif'):
                        logger.error(
                            _('The tarif is needed to continue processing this article. Line %s' % reader.line_num))
                        errors.append((row, _('The tarif column is missed!')))
                        continue
                    vals = {
                        'default_code': row.get('code'),
                        'list_price': row.get('tarif'),
                    }

                if self._context.get('general_import'):
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
                    if self._context.get('rate_import') \
                            or self._context.get('association_import') \
                            or self._context.get('documentation_import') \
                            or self._context.get('grouping_import'):
                        if not product:
                            continue
                        product.write(vals)
                    if self._context.get('general_import'):
                        if product:
                            product.write(vals)
                        else:
                            product = self.create(vals)
                    if reader.line_num % 10 == 0:
                        logger.info(_('Import in progress ... %s lines treated.' % reader.line_num))
                    product.manage_supinfo(row)
                    logger.info(str(row))
                    self._cr.commit()
                except Exception as e:
                    logger.error(repr(e))
                    errors.append((row, repr(e)))
                    self._cr.rollback()
            except Exception as e:
                logger.error(repr(e))
                errors.append((row, repr(e)))
                self._cr.rollback()
        if errors and template.export_xls:
            if self._context.get('grouping_import'):
                self.with_context(grouping_import=True).generate_errors_file(template, errors)
            if self._context.get('documentation_import'):
                self.with_context(documentation_import=True).generate_errors_file(template, errors)
            if self._context.get('association_import'):
                self.with_context(association_import=True).generate_errors_file(template, errors)
            if self._context.get('rate_import'):
                self.with_context(rate_import=True).generate_errors_file(template, errors)
            if self._context.get('general_import'):
                self.with_context(general_import=True).generate_errors_file(template, errors)
        logger.info(_('Import done successfully.'))

    @api.model
    def generate_errors_file(self, template=False, data=[]):
        """
        Generate the file with all error lines
        :param template:
        :param data:
        :return:
        """
        if not data or not template:
            return
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data, delimiter=';')
        if self._context.get('general_import'):
            csv_header = ['code', 'libelle', 'presentation', 'fournisseur', 'poids', 'classe', 'ssClasse', 'sClasse', 'categorie', 'sCategorie',
                          'ssCategorie', 'gtin', 'ean', 'cip', 'error detail']
            csv_writer.writerow(csv_header)
            for row, error in data:
                csv_writer.writerow([row.get('code'), row.get('libelle'), row.get('presentation'), row.get('fournisseur'), row.get('poids'),
                                     row.get('classe'), row.get('ssClasse'), row.get('sClasse'), row.get('categorie'), row.get('sCategorie'),
                                     row.get('ssCategorie'), row.get('gtin'), row.get('ean'), row.get('cip'), error])

        if self._context.get('rate_import'):
            csv_header = ['code', 'tarif', 'error detail']
            csv_writer.writerow(csv_header)
            for row, error in data:
                csv_writer.writerow([row.get('code'), row.get('tarif'), error])

        if self._context.get('association_import'):
            csv_header = ['code', 'codeA', 'error detail']
            csv_writer.writerow(csv_header)
            for row, error in data:
                csv_writer.writerow([row.get('code'), row.get('codeA'), error])

        if self._context.get('documentation_import'):
            csv_header = ['code', 'type', 'doc', 'error detail']
            csv_writer.writerow(csv_header)
            for row, error in data:
                csv_writer.writerow([row.get('code'), row.get('type'), row.get('doc'), error])

        if self._context.get('grouping_import'):
            csv_header = ['code', 'regroupement', 'ordre', 'error detail']
            csv_writer.writerow(csv_header)
            for row, error in data:
                csv_writer.writerow([row.get('code'), row.get('regroupement'), row.get('ordre'), error])

        content = base64.b64encode(csv_data.getvalue().encode('utf-8'))
        date = str(fields.Datetime.now()).replace(':', '').replace('-', '').replace(' ', '')
        filename = 'PRODUCT_ERREURS_%s.csv' % date
        self.create_attachment(template, content, filename)

    @api.model
    def create_attachment(self, template=False, content=None, filename=False):
        """
        Create error file in attachment
        :param template:
        :param content:
        :param filename:
        :return:
        """
        if not template or not content:
            return False
        model = 'ir.model.import.template'
        template.attachment_ids = [(0, 0, {'type': 'binary', 'res_model': model,
                                           'res_id': template.id, 'datas': content, 'name': filename})]
        return True
