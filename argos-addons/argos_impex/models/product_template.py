# -*- coding: utf-8 -*-


import csv
import io
import base64

from odoo import models, fields, registry, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def manage_supinfo(self, row={}):
        self.ensure_one()
        res_partner = self.env['res.partner']
        if not row:
            return False
        supplier = res_partner.search([('name', '=', row.get('fournisseur'))], limit=1)
        if not supplier:
            supplier = res_partner.create({'name': row.get('fournisseur'), 'company_type': 'company'})

        sellers = self.seller_ids.filtered_from_domain([('name', '=', supplier.id)])
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
                logger = self._context['logger']
                self = self.with_env(self.env(cr=new_cr))
                category_obj = self.env['product.category']
                model_import_obj = self.env['ir.model.import.template']
                line_errors = False
                try:
                    template = model_import_obj.browse(kwargs.get('import_id'))
                    if not template:
                        logger.error(_('There is nothing to import.'))
                        return True
                    if not template.has_file_changed:
                        logger.info(_('Nothing to import. The file is the same as the last execution.'))
                        return True
                    scsv = base64.decodebytes(template.import_file).decode('utf-8-sig')
                    csvfile = io.StringIO(scsv)
                    reader = csv.DictReader(csvfile, delimiter=',')
                    for row in reader:
                        try:
                            if not row.get('code'):
                                logger.error(
                                    _(
                                        "The code is needed to continue processing this article. Line %s" % reader.line_num))
                                line_errors = True
                                continue

                            if not row.get('libelle'):
                                logger.error(
                                    _(
                                        "The code is needed to continue processing this article. Line %s" % reader.line_num))
                                line_errors = True
                                continue

                            vals = {
                                'default_code': row.get('code'),
                                'name': row.get('libelle'),
                                'description': row.get('presentation'),
                                'weight': self.convert_to_float(row.get('poids')),
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
                            product = self.search(
                                [('default_code', '!=', False), ('default_code', '=', row.get('code'))], limit=1)
                            try:
                                if product:
                                    product.write(vals)
                                else:
                                    vals.update({'default_code': row.get('code')})
                                    product = self.create(vals)
                                if reader.line_num % 150 == 0:
                                    logger.info(_("Import in progress ... %s lines treated." % reader.line_num))

                                product.manage_supinfo(row)
                                self._cr.commit()
                            except Exception as e:
                                logger.error(repr(e))
                                line_errors = True
                                new_cr.rollback()
                        except Exception as error:
                            logger.error(repr(error))
                            line_errors = True
                            new_cr.rollback()
                    logger.info(_("End Import Of %s Successfully." % template.file_name))
                    template.write({'has_file_changed': False})
                except Exception as error:
                    logger.error(repr(error))
                    line_errors = True
                    new_cr.rollback()
                if line_errors and template.export_xls:
                    self.generate_error_files()
