# -*- coding: utf-8 -*-


import csv
import io
import base64

import xml.etree.ElementTree as ET

from odoo import models, fields, registry, api, _
from odoo.addons.argos_base.models import tools


def transform_tuple_to_dict(data_tuple=(), source=False):
    """
    Transform data tuple to dict
    :param data_tuple:
    :return:
    """
    if not data_tuple or not source:
        return {}
    if source == 'produit-regroupement':
        return {'code': data_tuple[1], 'regroupement': data_tuple[3], 'ordre': data_tuple[2]}
    return {'code': data_tuple[1], 'filtre': data_tuple[2], 'valeur': data_tuple[3]}


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    doc_type = fields.Char('Documentation Type', required=False)
    doc_url = fields.Char('Documentation URL', required=False)
    aliment_type = fields.Char('Aliment Type', required=False)
    utilization = fields.Char('Utilization', required=False)
    composition = fields.Char('Composition', required=False)
    analytic_constitution = fields.Char('Analytic Constitution', required=False)
    additives = fields.Char('Additives', required=False)
    energetic_value = fields.Char('Energetic Value', required=False)
    daily_ratio_recommended = fields.Char('Daily Ratio Recommended', required=False)
    indications = fields.Char('Indications', required=False)
    waters_content = fields.Char('Waters Content', required=False)

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

    @api.model
    def schedule_import_process(self, **kwargs):
        with api.Environment.manage():
            with registry(self._cr.dbname).cursor() as new_cr:
                self = self.with_env(self.env(cr=new_cr))
                logger = self._context['logger']
                model_import_obj = self.env['ir.model.import.template']
                try:
                    template = model_import_obj.browse(kwargs.get('template_id'))
                    source = kwargs.get('source')
                    if not template:
                        logger.error(_('There is nothing to import.'))
                        return True
                    if template.is_remote_import:
                        if not template.server_ftp_id:
                            return
                        template.server_ftp_id.with_context(template=template.id, logger=logger, source=source).retrieve_data()
                    elif template.import_file:
                        content = base64.decodebytes(template.import_file).decode('utf-8-sig')
                        if source == 'produit-general':
                            return self.processing_import_data(content, template, source)
                        if source == 'tarif':
                            return self.processing_import_list_price_data(content, template, source)
                        if source == 'produit-association':
                            return self.processing_import_product_association_data(content, template, source)
                        if source == 'produit-documentation':
                            return self.processing_import_product_documentation_data(content, template, source)
                        if source == 'produit-regroupement':
                            return self.processing_import_product_regroupment_data(content, template, source)
                        if source == 'produit-reglementation':
                            return self.processing_import_product_reglementation_data(content, template, source)
                        if source == 'produit-enrichi':
                            return self.processing_import_product_enrichi_data(content, template, source)
                        if source == 'produit-filtre':
                            return self.processing_import_produit_filtre_data(content, template, source)
                        if source == 'stock':
                            return self.processing_import_stock_data(content, template, source)
                except Exception as e:
                    logger.error(repr(e))
                    self._cr.rollback()

    @api.model
    def processing_import_data(self, content=None, template=False, source=False, logger=False):
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
                    logger.error(_('The code is needed to continue processing this article. Line %s') % reader.line_num)
                    errors.append((row, _('The code column is missed!')))
                    continue
                if not row.get('libelle'):
                    logger.error(_('The libelle is needed to continue processing this article. Line %s') % reader.line_num)
                    errors.append((row, _('The libelle column is missed!')))
                    continue
                vals = {
                    'default_code': row.get('code'),
                    'name': row.get('libelle'),
                    'description': row.get('presentation'),
                    'weight': row.get('poids'),
                    'categ_id': category_obj._get_category_by_name(row.get('categorie')),
                    'gtin': row.get('gtin'),
                    'ean': row.get('ean'),
                    'cip': row.get('cip'),
                    'sale_ok': True,
                    'purchase_ok': True,
                    'type': 'product',
                    'is_published': True,
                }
                product = self.search([('default_code', '=', row.get('code'))], limit=1)
                try:
                    if product:
                        product.write(vals)
                    else:
                        product = self.create(vals)
                    if reader.line_num % 150 == 0:
                        logger.info(_('Import in progress ... %s lines treated.') % reader.line_num)
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
        self.manage_import_report(source, lines, template, errors, logger)
        return True

    @api.model
    def generate_errors_file(self, source=False, template=False, data=[]):
        """
        Generate the file with all error lines
        :param template:
        :param data:
        :return:
        """
        if not data or not template or not source or not isinstance(data, list):
            return
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data, delimiter=';')
        if source == 'produit-general':
            csv_writer.writerow(['code', 'libelle', 'presentation', 'fournisseur', 'poids', 'classe', 'ssClasse', 'sClasse', 'categorie',
                                 'sCategorie', 'ssCategorie', 'gtin', 'ean', 'cip', 'error detail'])
            for row, error in data:
                csv_writer.writerow([row.get('code'), row.get('libelle'), row.get('presentation'), row.get('fournisseur'), row.get('poids'),
                                     row.get('classe'), row.get('ssClasse'), row.get('sClasse'), row.get('categorie'),
                                     row.get('sCategorie'),
                                     row.get('ssCategorie'), row.get('gtin'), row.get('ean'), row.get('cip'), error])
        elif source == 'tarif':
            csv_writer.writerow(['code', 'tarif', 'error detail'])
            for row, error in data:
                csv_writer.writerow([row.get('code'), row.get('tarif'), error])
        elif source == 'produit-association':
            csv_header = ['code', 'codeA', 'error detail']
            csv_writer.writerow(csv_header)
            for row, error in data:
                csv_writer.writerow([row.get('code'), row.get('codeA'), error])
        elif source == 'produit-documentation':
            csv_header = ['code', 'type', 'doc', 'error detail']
            csv_writer.writerow(csv_header)
            for row, error in data:
                csv_writer.writerow([row.get('code'), row.get('type'), row.get('doc'), error])
        elif source == 'produit-regroupement':
            csv_header = ['code', 'regroupement', 'ordre', 'error detail']
            csv_writer.writerow(csv_header)
            for row, error in data:
                csv_writer.writerow([row.get('code'), row.get('regroupement'), row.get('ordre'), error])
        elif source == 'produit-filtre':
            csv_header = ['code', 'filtre', 'valeur', 'error detail']
            csv_writer.writerow(csv_header)
            for row, error in data:
                csv_writer.writerow([row.get('code'), row.get('filtre'), row.get('valeur'), error])
        elif source == 'produit-reglementation':
            return self.generate_xml_error_file(source, template, data)
        elif source == 'produit-enrichi':
            return self.generate_xml_error_file(source, template, data)
        elif source in ('contacts', 'patients', 'owners', 'gender', 'race', 'robe', 'insurance', 'insurance', 'living', 'species',
                        'tattoo', 'chip', 'passport', 'pathology-category', 'pathology', 'weight'):
            header = list(data[0][0].keys())
            csv_writer.writerow(header + ['error detail'])
            for row, error in data:
                csv_writer.writerow([row.get(key) for key in header] + [error])
        elif source == 'stock':
            csv_writer.writerow(['Client', 'Article', 'Stock', 'Erreur'])
            for row, error in data:
                csv_writer.writerow([row.get('Client'), row.get('Article'), row.get('Stock'), error])
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
    def processing_import_list_price_data(self, content=None, template=False, source=False, logger=False):
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
                    logger.error(_('The code is needed to continue processing this article. Line %s') % reader.line_num)
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
                        errors.append((row, _('No product with code %s found.') % row.get('code')))
                    if reader.line_num % 150 == 0:
                        logger.info(_('Import in progress ... %s lines treated.') % reader.line_num)
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
        self.manage_import_report(source, lines, template, errors, logger)
        return True

    @api.model
    def processing_import_product_association_data(self, content=None, template=False, source=False, logger=False):
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
                    logger.error(_('The code is needed to continue processing this article. Line %s') % reader.line_num)
                    errors.append((row, _('The code column is missed!')))
                    continue
                product = self.search([('default_code', '=', row.get('code'))], limit=1)
                try:
                    if product:
                        accessory = self.search([('default_code', '=', row.get('codeA')), ('default_code', '!=', False)], limit=1)
                        if accessory:
                            product.write({'accessory_product_ids': [(4, accessory.id)]})
                            lines.append(reader.line_num)
                        else:
                            errors.append((row, _('No associated product with code %s found.') % row.get('codeA')))
                    else:
                        errors.append((row, _('No product with code %s found.') % row.get('code')))
                    if reader.line_num % 150 == 0:
                        logger.info(_('Import in progress ... %s lines treated.') % reader.line_num)
                    self._cr.commit()
                except Exception as e:
                    logger.error(repr(e))
                    errors.append((row, repr(e)))
                    self._cr.rollback()
            except Exception as e:
                logger.error(repr(e))
                errors.append((row, repr(e)))
                self._cr.rollback()
        self.manage_import_report(source, lines, template, errors, logger)
        return True

    @api.model
    def processing_import_product_documentation_data(self, content=None, template=False, source=False, logger=False):
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
                    logger.error(_('The code is needed to continue processing this article. Line %s') % reader.line_num)
                    errors.append((row, _('The code column is missed!')))
                    continue
                if not row.get('type'):
                    logger.error(
                        _('The type is needed to continue processing this article. Line %s') % reader.line_num)
                    errors.append((row, _('The type column is missed!')))
                    continue
                vals = {
                    'default_code': row.get('code'),
                    'doc_type': row.get('type'),
                    'doc_url': row.get('doc'),
                }
                product = self.search([('default_code', '=', row.get('code'))], limit=1)
                try:
                    if product:
                        product.write(vals)
                    else:
                        errors.append((row, _('No product with code %s found.') % row.get('code')))
                    if reader.line_num % 150 == 0:
                        logger.info(_('Import in progress ... %s lines treated.') % reader.line_num)
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
        self.manage_import_report(source, lines, template, errors, logger)
        return True

    @api.model
    def processing_import_product_regroupment_data(self, content=None, template=False, source=False, logger=False):
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
        product_summary = {}
        for row in reader:
            product_summary.setdefault(row.get('regroupement'), []). \
                append((reader.line_num, row.get('code'), row.get('ordre'), row.get('regroupement')))
        for key, values in product_summary.items():
            try:
                products = self
                for item in values:
                    if len(values) == 1:
                        logger.error(_('The is no regroupement to treat. Line %s') % item[0])
                        errors.append((transform_tuple_to_dict(item, source), _('The is no regroupement to treat!')))
                        continue
                    if not item[1]:
                        logger.error(_('The code is needed to continue processing this article. Line %s') % item[0])
                        errors.append((transform_tuple_to_dict(item, source), _('Pleas fill the code column!')))
                        continue
                    product = self.search([('default_code', '=', item[1])], limit=1)
                    if not product:
                        errors.append((transform_tuple_to_dict(item, source), _('No product with code %s found.') % item[1]))
                        continue
                    products |= product
                    product.write({'website_sequence': int(item[2])})
                    lines.append(item[0])
                for product in products:
                    product.write({'alternative_product_ids': [(4, idx) for idx in (products - product).ids]})
                self._cr.commit()
            except Exception as e:
                logger.error(repr(e))
                errors.append((transform_tuple_to_dict(item, source), repr(e)))
                self._cr.rollback()
        self.manage_import_report(source, lines, template, errors, logger)
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
            logger.info(_('List of lines imported successfully: %s') % str(lines))
        if errors and template.export_xls:
            self.generate_errors_file(source, template, errors)
            logger.info(_('Import finish with errors. Go to History Error Files tab to show the list of stranded lines.'))
            return False
        if errors:
            logger.info(_("List of stranded lines: ['%s']") % "', '".join(str(row[0].get('code', row[0].get('default_code')))
                                                                          for row in errors if row and isinstance(row[0], dict)))
            return False
        if not errors:
            logger.info(_('Import done successfully.'))
        return True

    @api.model
    def processing_import_product_reglementation_data(self, content=None, template=False, source=False, logger=False):
        """
        Import regulations of products
        :param content:
        :param template:
        :param logger:
        :return:
        """
        if not content or not template:
            return False
        products = ET.fromstring(content)
        index = 1
        lines = []
        errors = []
        logger = logger or self._context['logger']
        for child in products:
            default_code = child[0].text.strip()
            vals = {
                'default_code': default_code,
                'aliment_type': child[1].text,
                'utilization': child[2].text,
                'composition': child[3].text,
                'analytic_constitution': child[5].text,
                'additives': child[5].text,
                'energetic_value': child[6].text,
                'daily_ratio_recommended': child[7].text,
                'indications': child[8].text,
                'waters_content': child[9].text,
            }
            if not default_code:
                logger.error(_('The code is needed to continue processing this article. Line %s') % index)
                errors.append((vals, _('The code is needed to continue processing this article!')))
                index += 1
                continue
            product = self.search([('default_code', '=', default_code)], limit=1)
            try:
                if product:
                    product.write(vals)
                    lines.append(default_code)
                else:
                    errors.append((vals, _('No product with code %s found.') % default_code))
                if index % 150 == 0:
                    logger.info(_('Import in progress ... %s lines treated.') % index)
                self._cr.commit()
            except Exception as e:
                logger.error(repr(e))
                errors.append((vals, repr(e)))
                self._cr.rollback()
            finally:
                index += 1
        self.manage_import_report(source, lines, template, errors, logger)

    @api.model
    def generate_xml_error_file(self, source=False, template=False, data=False):
        """
        :param data:
        :param template:
        :param source:
        :return:
        """
        if not data or not template or not source:
            return False
        root = self.get_xml_structure(source, data)
        xml_data = ET.tostring(root)
        content = base64.b64encode(xml_data)
        date = str(fields.Datetime.now()).replace(':', '').replace('-', '').replace(' ', '')
        filename = '%s_%s.xml' % (source, date)
        self.create_attachment(template, content, filename)
        return True

    @api.model
    def get_xml_structure(self, source=False, data=False):
        """
        :param source:
        :param data:
        :return:
        """
        if not source or not data:
            return False
        if source == 'produit-reglementation':
            root = ET.Element('Produits')
            for tag, error_msg in data:
                product = ET.SubElement(root, 'produit')
                code = ET.SubElement(product, 'code')
                typeAliment = ET.SubElement(product, 'typeAliment')
                utilisation = ET.SubElement(product, 'utilization')
                composition = ET.SubElement(product, 'composition')
                constitutantsAnalytiques = ET.SubElement(product, 'constitutantsAnalytiques')
                additifs = ET.SubElement(product, 'additifs')
                valeurEnergetique = ET.SubElement(product, 'valeurEnergetique')
                rationJournaliereRecommandee = ET.SubElement(product, 'rationJournaliereRecommandee')
                indications = ET.SubElement(product, 'indications')
                teneurEnEau = ET.SubElement(product, 'teneurEnEau')
                error = ET.SubElement(product, 'errorDetails')
                # add text to tags
                code.text = tag.get('default_code')
                typeAliment.text = tag.get('aliment_type')
                utilisation.text = tag.get('utilisation')
                composition.text = tag.get('composition')
                constitutantsAnalytiques.text = tag.get('analytic_constitution')
                additifs.text = tag.get('additives')
                valeurEnergetique.text = tag.get('energetic_value')
                rationJournaliereRecommandee.text = tag.get('daily_ratio_recommended')
                indications.text = tag.get('indications')
                teneurEnEau.text = tag.get('waters_content')
                error.text = error_msg
            return root
        if source == 'produit-enrichi':
            root = ET.Element('Produits')
            for tag, error_msg in data:
                product = ET.SubElement(root, 'produit')
                code = ET.SubElement(product, 'code')
                description = ET.SubElement(product, 'description')
                vignette = ET.SubElement(product, 'vignette')
                photo = ET.SubElement(product, 'photo')
                error = ET.SubElement(product, 'error_detail')
                # add text to tags
                code.text = tag.get('default_code')
                description.text = tag.get('description')
                vignette.text = tag.get('vignette')
                photo.text = tag.get('photo')
                error.text = error_msg
            return root
        return False

    @api.model
    def processing_import_product_enrichi_data(self, content=None, template=False, source=False, logger=False):
        """
        Import enriched_products of products
        :param content:
        :param template:
        :param logger:
        :return:
        """
        if not content or not template:
            return False
        products = ET.fromstring(content)
        index = 1
        lines = []
        errors = []
        logger = logger or self._context['logger']
        for child in products:
            default_code = child[0].text.strip()
            vals = {
                'default_code': default_code,
                'description_sale': child[1].text,
                'image_1024': tools.get_image_url_as_base64(child[2].text),
                'image_1920': tools.get_image_url_as_base64(child[3].text)
            }
            if not default_code:
                logger.error(_('The code is needed to continue processing this article. Line %s') % index)
                errors.append((vals, _('The code is needed to continue processing this article!')))
                index += 1
                continue
            product = self.search([('default_code', '=', default_code)], limit=1)
            try:
                if product:
                    product.write(vals)
                    lines.append(default_code)
                else:
                    errors.append((vals, _('No product with code %s found.') % default_code))
                if index % 150 == 0:
                    logger.info(_('Import in progress ... %s lines treated.') % index)
                self._cr.commit()
            except Exception as e:
                logger.error(repr(e))
                errors.append((vals, repr(e)))
                self._cr.rollback()
            finally:
                index += 1
        return self.manage_import_report(source, lines, template, errors, logger)

    @api.model
    def processing_import_produit_filtre_data(self, content=None, template=False, source=False, logger=False):
        """
        Import variant attributes/value
        :param content:
        :param template:
        :param source:
        :param logger:
        :return:
        """
        if not content or not template:
            return False
        csvfile = io.StringIO(content)
        reader = csv.DictReader(csvfile, delimiter=';')
        logger = logger or self._context['logger']
        product_attribute_summary = {}
        errors = []
        lines = []
        product_attr_obj = self.env['product.attribute']
        product_attr_value_obj = self.env['product.attribute.value']
        for row in reader:
            if not row.get('code'):
                logger.error(_('The code column is needed to continue processing this article. Line %s') % reader.line_num)
                errors.append((row, _('The code column is needed to continue processing this article!')))
                continue
            if not row.get('filtre'):
                logger.error(_('The filtre column is needed to continue processing this article. Line %s') % reader.line_num)
                errors.append((row, _('The filtre column is needed to continue processing this article!')))
                continue
            if not row.get('valeur'):
                logger.error(_('The value column is needed to continue processing this article. Line %s') % reader.line_num)
                errors.append((row, _('The value column is needed to continue processing this article!')))
                continue
            code = row.get('code')
            product = self.search([('default_code', '=', code)], limit=1)
            if not product:
                logger.error(_('No product with code %s found. Line %s') % (code, reader.line_num))
                errors.append((row, _('No product with code %s found.') % code))
                continue
            filter = row.get('filtre')
            attribute = product_attr_obj.get_attribute_by_name(filter)
            if not attribute:
                logger.error(_('No attribute %s found. Line %s') % (filter, reader.line_num))
                errors.append((row, _('No attribute %s found.') % filter))
                continue
            product_attribute_summary.setdefault((product, attribute), []).append((reader.line_num, code, filter, row.get('valeur')))
        index = 0
        for key, values in product_attribute_summary.items():
            try:
                product = key[0]
                attribute = key[1]
                index += 1
                if index % 500 == 0:
                    progression = round(index * 100 / len(product_attribute_summary))
                    logger.info(_('Import in progress ... %s %%%%') % str(progression))
                attribute_lines = product.attribute_line_ids.filtered(lambda attr: attr.attribute_id == attribute)
                attribute_values = product_attr_value_obj.manage_attribute_values(values, attribute, logger)
                if attribute_lines:
                    attribute_lines.write({'value_ids': [(4, idx) for idx in attribute_values.ids]})
                    # TODO: manage attribute value deletion
                else:
                    product.write({'attribute_line_ids': [(0, 0, {'attribute_id': attribute.id,
                                                                  'value_ids': [(6, 0, attribute_values.ids)]})]})
                for item in values:
                    lines.append(item[0])
                self._cr.commit()
            except Exception as e:
                logger.error(repr(e))
                errors.append((transform_tuple_to_dict(values, source), _('No attribute %s found.') % filter))
                self._cr.rollback()
        self.manage_import_report(source, lines, template, errors, logger)
        return True

    @api.model
    def processing_import_stock_data(self, content=None, template=False, source=False, logger=False):
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
        operating_unit_obj = self.env['operating.unit']
        quant_obj = self.env['stock.quant']
        stock_location_obj = self.env['stock.location']
        for row in reader:
            try:
                line_num = reader.line_num
                clinical = row.get('Client')
                if not clinical:
                    logger.error(_('The clinical code is missed. Line %s') % line_num)
                    errors.append((row, _('The clinical code is missed!')))
                    continue
                operating_unit = operating_unit_obj.search([('code', '=', clinical)], limit=1)
                if not operating_unit:
                    logger.error(_('No clinical with code %s found. Line %s') % (clinical, line_num))
                    errors.append((row, _('No clinical found!')))
                    continue
                code = row.get('Article')
                if not code:
                    logger.error(_('The product code is missed. Line %s') % line_num)
                    errors.append((row, _('The product code is missed!')))
                    continue
                product = self.search([('default_code', '=', code)], limit=1)
                if not product:
                    logger.error(_('No product with code %s found. Line %s') % (code, line_num))
                    errors.append((row, _('No product found.')))
                    continue
                try:
                    quant = quant_obj.search([('location_id.operating_unit_id', '=', operating_unit.id),
                                              ('location_id.usage', 'in', ('internal', 'transit')),
                                              ('product_id', 'in', product.product_variant_ids.ids)], limit=1)
                    if quant:
                        if row.get('Stock') == 'O':
                            inventory_quantity = 1
                        else:
                            inventory_quantity = 0
                        quant.with_context(inventory_mode=True).write({'inventory_quantity': inventory_quantity})
                    elif row.get('Stock') == 'O':
                        quant_obj.with_context(inventory_mode=True).create({
                            'location_id': stock_location_obj.search([('usage', 'in', ('internal', 'transit')),
                                                                      ('operating_unit_id', '=', operating_unit.id)]).id,
                            'product_id': product.product_variant_ids.ids[0],
                            'inventory_quantity': 1,
                        })
                    lines.append(line_num)
                    self._cr.commit()
                except Exception as e:
                    logger.error(repr(e))
                    errors.append((row, repr(e)))
                    self._cr.rollback()
            except Exception as e:
                logger.error(repr(e))
                errors.append((row, repr(e)))
                self._cr.rollback()
        self.manage_import_report(source, lines, template, errors, logger)
        return True


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def create(self, vals):
        record = super(StockQuant, self).create(vals)
        return record
