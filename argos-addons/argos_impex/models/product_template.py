# -*- coding: utf-8 -*-

from odoo import models, fields, registry, http, api, _
import csv
import io
from . import tools
import pathlib
from datetime import datetime
from ftplib import FTP
import base64
import os

PRODUCT_FILE = ['.csv']

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def convert_to_float(self, value):
        if not value:
            return False
        return value.replace(',', '.')

    def get_import_directory(self):
        logger = self._context['logger']
        try:
            return str(os.path.dirname(os.path.abspath(__file__))).replace('models', 'import_data/').strip(' ')
        except Exception as error:
            logger.error(_("Error when accessing remote direcory:  " + str(error)))

    def get_all_files_to_import(self):
        logger = self._context['logger']
        try:
            return os.listdir(self.get_import_directory())
        except Exception as error:
            logger.error(_("Error when accessing files in local directory:  " + str(error)))

    @api.model
    def get_all_files_from_ftp(self, template):
        """ Get all files from ftp"""

        logger = self._context['logger']
        try:
            logger.info(_("Starting ftp connexion..."))
            ftp = FTP(template.remote_url)
            ftp.set_pasv(False)
            ftp.login(template.remote_login, template.remote_pwd)
            ftp.cwd(template.remote_directory)
            logger.info(_("Connected..."))

            start = datetime.now()
            down_path = self.get_import_directory()
            files = ftp.nlst()

            for file in files:
                logger.info(_("Downloading..." + file))
                ftp.retrbinary("RETR " + file, open(down_path + file, 'wb').write)

            ftp.close()
            end = datetime.now()
            diff = end - start
            logger.info(_('All files downloaded for ' + str(diff.seconds) + 's'))

        except Exception as error:
            logger.error(_("Error when downloading files from remote directory:  " + str(error)))

    def get_supplier_by_name(self, supplier_name):
        res_partner = self.env['res.partner']
        partner = res_partner.search([('name', '=', supplier_name)], limit=1)
        if partner:
            return [(0, 0, {'name': partner.id})]
        else:
            new_partner = res_partner.create({'name': supplier_name, 'company_type': 'company'})
            return [(0, 0, {'name': new_partner.id})]

    def get_categ_by_name(self, mother_categ_name, sub_categ_name, child_categ_name):
        product_category = self.env['product.category']
        mother_category = product_category.search([('name', '=', mother_categ_name)], limit=1)
        if mother_category:
            mother_categ = mother_category
        else:
            mother_categ = product_category.create({
                'name': mother_categ_name
            })

        sub_category = product_category.search([('name', '=', sub_categ_name)], limit=1)
        if sub_category:
            sub_category.write({'parent_id': mother_categ.id})
        else:
            sub_category = product_category.create({
                'name': sub_categ_name,
                'parent_id': mother_categ.id
            })

        child_categ = product_category.search([('name', '=', child_categ_name)], limit=1)
        if child_categ:
            child_categ.write({'parent_id': sub_category.id})
            return child_categ.id
        else:
            child_categ = product_category.create({
                'name': child_categ_name,
                'parent_id': sub_category.id
            })
            return child_categ.id

    @api.model
    def get_product_template_by_name(self, row):
        partner_obj = self.env['res.partner']
        product_tmp_obj = self.env['product.template']
        partner_id = partner_obj.get_partner_by_name(row.get('Nom du fournisseur'))
        if not partner_id:
            return self.search([('name', '=', row.get('Libellé simple de l\'article'))], limit=1).id
        elif self._context.get('For_price'):
            product_tmpl_id_active = self.search(
                [('ref_supplier', '=', row.get('Référence fournisseur')), ('supplier_id', '=', partner_id)], limit=1)
            if not product_tmpl_id_active:
                product_tmpl_id = self.search([('ref_supplier', '=', row.get('Référence fournisseur')), ('supplier_id', '=', partner_id),
                                               ('active', '!=', True)], limit=1)
            else:
                product_tmpl_id = product_tmpl_id_active
            return product_tmpl_id.id
        else:
            return product_tmp_obj.search([('supplier_id', '=', partner_id), ('name', '=', row.get('Libellé simple de l\'article'))], limit=1).id

    def running_import(self, logger, csv_writer, new_cr, file_name, reader, template, csv_data):
        product_template_obj = self.env['product.template']
        is_error = False
        logger.info(_("Start Import Of %s" % file_name))

        csv_headers = [_('code'),
                       _('libelle'),
                       _('presentation'),
                       _('fournisseur'),
                       _('poids'),
                       # _('ecoParticipation'),
                       # _('nouveau'),
                       _('classe'),
                       _('ssClasse'),
                       _('sClasse'),
                       # _('codeCategorie'),
                       _('categorie'),
                       _('sCategorie'),
                       _('ssCategorie'),
                       # _('poids_net'),
                       _('gtin'),
                       _('ean'),
                       _('cip'),
                       ]
        csv_writer.writerow(csv_headers)

        try:
            if not template:
                logger.error(_('There is nothing to import.'))
                return

            for row in reader:
                try:
                    vals = {
                        'default_code': row.get('code'),
                        'name': row.get('libelle'),
                        'description': row.get('presentation'),
                        'seller_ids': self.get_supplier_by_name(row.get('fournisseur')),
                        'weight': self.convert_to_float(row.get('poids')),
                        # 'ecoParticipation': ,
                        # 'nouveau': tools.str2bool(row.get('nouveau')),
                        'mother_class': row.get('classe'),
                        'sub_child_class': row.get('ssClasse'),
                        'child_class': row.get('sClasse'),
                        # 'codeCategorie': row.get('codeCategorie'),
                        # 'poids_net': row.get('poids_net'),
                        'gtin': row.get('gtin'),
                        'ean': row.get('ean'),
                        'cip': row.get('cip'),
                    }
                    if row.get('categorie'):
                        vals.update({'categ_id': self.get_categ_by_name(row.get('categorie'), row.get('sCategorie'),
                                                                        row.get('ssCategorie'))})

                    template_id = product_template_obj.search(
                        [('default_code', '=', row.get('code'))], limit=1)
                    if template_id:
                        template_id.write(vals)
                    else:
                        product_template_obj.create(vals)
                    if reader.line_num % 150 == 0:
                        logger.info(_("Import in progress ... %s lines treated." % reader.line_num))
                    self._cr.commit()

                except Exception as error:
                    error_line = [
                        row.get('code'),
                        row.get('libelle'),
                        row.get('presentation'),
                        row.get('fournisseur'),
                        row.get('poids'),
                        # row.get('ecoParticipation'),
                        # row.get('nouveau'),
                        row.get('classe'),
                        row.get('ssClasse'),
                        row.get('sClasse'),
                        # row.get('codeCategorie'),
                        row.get('categorie'),
                        row.get('sCategorie'),
                        row.get('ssCategorie'),
                        # row.get('poids_net'),
                        row.get('gtin'),
                        row.get('ean'),
                        row.get('cip'),
                        repr(error)
                    ]
                    csv_writer.writerow(error_line)
                    logger.error(repr(error))

                    if not is_error:
                        is_error = True
                    new_cr.rollback()
            logger.info(_("End Import Of %s Successfully." % file_name))

        except Exception as error:
            logger.error(repr(error))
            new_cr.rollback()

        if is_error and template.export_xls:
            binary_file = base64.b64encode(csv_data.getvalue().encode('utf-8-sig'))
            name_of_file = file_name + '_%s.csv' % fields.Datetime.now()
            self.add_attachment(template.id, binary_file, name_of_file)

    def schedule_import_product(self, **kwargs):

        with api.Environment.manage():
            with registry(self._cr.dbname).cursor() as new_cr:
                logger = self._context['logger']
                self = self.with_env(self.env(cr=new_cr))
                template_obj = self.env['ir.model.import.template']
                template = template_obj.browse(kwargs.get('import_id'))

                if template.is_remote_import:
                    self.get_all_files_from_ftp(template)
                    for file in self.get_all_files_to_import():
                        csv_data = io.StringIO()
                        csv_writer = csv.writer(csv_data, delimiter=';')

                        csv_file = str(self.get_import_directory() + file)
                        if pathlib.Path(csv_file).suffix in PRODUCT_FILE:
                            with open(csv_file, 'r', encoding='utf-8') as FILE:
                                reader = csv.DictReader(FILE, delimiter=';', quotechar='|')
                                self.running_import(logger, csv_writer, new_cr, file, reader, template, csv_data)
                            os.remove(str(self.get_import_directory() + file))
                else:
                    csv_data = io.StringIO()
                    csv_writer = csv.writer(csv_data, delimiter=';')

                    # scsv = base64.decodebytes(template.import_file).decode('ISO-8859-1')
                    scsv = base64.decodebytes(template.import_file).decode('utf-8')
                    csvfile = io.StringIO(scsv)
                    reader = csv.DictReader(csvfile, delimiter=';', quotechar='|')
                    self.running_import(logger, csv_writer, new_cr, template.file_name, reader, template, csv_data)

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
        })
        self._cr.commit()
        return True
