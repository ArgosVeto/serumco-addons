# -*- coding: utf-8 -*-

from odoo import models, fields, registry, http, api, _
import csv
import io
from . import tools
import base64


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def convert_to_float(self, value):
        if not value:
            return False
        return value.replace(',', '.')

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

    def schedule_import_product(self, **kwargs):

        with api.Environment.manage():
            with registry(self._cr.dbname).cursor() as new_cr:
                logger = self._context['logger']
                self = self.with_env(self.env(cr=new_cr))
                template_obj = self.env['ir.model.import.template']
                product_category_obj = self.env['product.category']
                product_template_obj = self.env['product.template']
                # product_gamme_obj = self.env['product.gamme']
                res_partner_obj = self.env['res.partner']
                is_error = False
                template = template_obj.browse(kwargs.get('import_id'))
                csv_data = io.StringIO()
                csv_writer = csv.writer(csv_data, delimiter=';')

                csv_headers = [_('code'),
                               _('libelle'),
                               _('presentation'),
                               # _('fournisseur'),
                               _('poids'),
                               # _('ecoParticipation'),
                               # _('nouveau'),
                               # _('classe'),
                               # _('ssClasse'),
                               # _('sClasse'),
                               # _('codeCategorie'),
                               _('categorie'),
                               # _('sCategorie'),
                               # _('ssCategorie'),
                               # _('poids_net'),
                               # _('gtin'),
                               # _('ean'),
                               # _('cip'),
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
                            if row.get('code') and row.get('libelle'):
                                vals = {
                                    'default_code': row.get('code'),
                                    'name': row.get('libelle'),
                                    'description': row.get('presentation'),
                                    # 'fournisseur': ,
                                    'weight': self.convert_to_float(row.get('poids')),
                                    # 'ecoParticipation': ,
                                    # 'nouveau': tools.str2bool(row.get('nouveau')),
                                    # 'classe': row.get('classe'),
                                    # 'ssClasse': row.get('ssClasse'),
                                    # 'sClasse': row.get('sClasse'),
                                    # 'codeCategorie': row.get('codeCategorie'),
                                    # 'categ_id': product_category_obj.get_category_by_name(row.get('categorie')),
                                    # 'sCategory': row.get('sCategory'),
                                    # 'ssCategory': row.get('ssCategory'),
                                    # 'poids_net': row.get('poids_net'),
                                    # 'gtin': row.get('gtin'),
                                    # 'ean': row.get('ean'),
                                    # 'cip': row.get('cip'),



                                    # 'subfamily_id': product_category_obj.get_category_by_name(row.get('subfamily_id')),
                                    # 'valdelia_family_id': product_category_obj.get_category_by_name(
                                    #     row.get('valdelia_family_id'), is_valdelia=True),
                                    # 'valdelia_subfamily_id': product_category_obj.get_category_by_name(
                                    #     row.get('valdelia_subfamily_id'), is_valdelia=True),
                                    # 'gamme_id': product_gamme_obj.get_gamme_by_name(row.get('gamme_ID')),
                                    # 'designer_id': res_partner_obj.get_partner_by_name(row.get('designer_id')),
                                    # 'supplier_id': res_partner_obj.get_partner_by_name(row.get('Supplier_ID')),
                                    # 'drawing_number': row.get('drawing_number'),
                                    # 'purchase_ok': tools.str2bool(row.get('purchase_ok')),
                                    # 'sale_ok': tools.str2bool(row.get('sale_ok')),
                                    # 'weight_net': row.get('weight'),
                                    # 'type': row.get('type'),
                                    # 'version': row.get('version'),
                                    # 'code_pfc': row.get('code_pfc'),
                                    # 'ref_supplier': row.get('Ref_Fournisseur '),
                                    # 'list_price': row.get('list_price'),
                                }
                                template_id = product_template_obj.search(
                                    [('default_code', '=', row.get('code'))], limit=1)
                                if template_id:
                                    template_id.write(vals)
                                else:
                                    product_template_obj.create(vals)
                                if reader.line_num % 150 == 0:
                                    logger.info(_("Import in progress ... %s lines treated." % reader.line_num))
                                self._cr.commit()
                            else:
                                pass

                        except Exception as error:
                            error_line = [
                                        row.get('code'),
                                        row.get('libelle'),
                                        row.get('presentation'),
                                        # row.get('fournisseur'),
                                        row.get('poids'),
                                        # row.get('ecoParticipation'),
                                        # row.get('nouveau'),
                                        # row.get('classe'),
                                        # row.get('ssClasse'),
                                        # row.get('sClasse'),
                                        # row.get('codeCategorie'),
                                        row.get('categorie'),
                                        # row.get('sCategorie'),
                                        # row.get('ssCategorie'),
                                        # row.get('poids_net'),
                                        # row.get('gtin'),
                                        # row.get('ean'),
                                        # row.get('cip'),
                                        repr(error)
                            ]
                            csv_writer.writerow(error_line)

                            if not is_error:
                                is_error = True
                            new_cr.rollback()
                    logger.info(_("End Import Of %s Successfully." % template.file_name))
                except Exception as error:
                    logger.error(repr(error))
                    new_cr.rollback()

                if is_error and template.export_xls:
                    binary_file = base64.b64encode(csv_data.getvalue().encode('utf-8-sig'))
                    file_name = 'PRODUCT_TEMPLATE_ERREURS_%s.csv' % fields.Datetime.now().replace(':', '').replace('-', '').replace(' ', '')
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
