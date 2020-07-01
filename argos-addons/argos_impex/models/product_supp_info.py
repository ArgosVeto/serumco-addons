# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, registry, http, api, tools, _
from datetime import datetime
import csv
import io
import base64

import logging

_logger = logging.getLogger(__name__)

def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    is_copy = fields.Boolean(string="is copy?", default=False)

    @api.model
    def convert_to_float(self, value):
        if not value:
            return 0.0
        return value.replace(',', '.').replace(' ', '')

    @api.model
    def convert_to_date(self, date):
        if not date:
            return False
        return datetime.strptime(date, '%d-%m-%y').date()

    @api.model
    def get_t_p(self, tp):
        return tp in ('P', 'p') and 'partial' or 'total'

    def schedule_import_suppl_finition(self, **kwargs):
        with api.Environment.manage():
            with registry(self._cr.dbname).cursor() as new_cr:
                logger = self._context['logger']
                self = self.with_env(self.env(cr=new_cr))
                template_obj = self.env['ir.model.import.template']
                product_template_obj = self.env['product.template']
                attribute_obj = self.env['product.attribute.value']
                res_partner_obj = self.env['res.partner']
                seller_obj = self.env['product.supplierinfo']
                template = template_obj.browse(kwargs.get('import_id'))
                is_error = False
                try:
                    if not template:
                        logger.error(_('There is nothing to import.'))
                        return

                    # scsv = base64.decodebytes(template.import_file).decode('utf-8')
                    scsv = base64.decodebytes(
                        template.import_file).decode('ISO-8859-1')
                    csvfile = io.StringIO(scsv)

                    reader = csv.DictReader(csvfile, delimiter=';')
                    logger.info(_("Start Import Of %s" % template.file_name))
                    csv_data = io.StringIO()
                    csv_writer = csv.writer(csv_data, delimiter=';', quoting=csv.QUOTE_ALL )

                    csv_headers = [_('Id Externe du fournisseur'),
                                   _('Nom du fournisseur'),
                                   _(u'Libellé simple de l\'article'),
                                   _(u'Référence fournisseur'),
                                   _('Finition'),
                                   _('Code finition'),
                                   _(u'Quantité minimale'),
                                   _('Prix d\'Achat'),
                                   _('T|P'),
                                   _(u'Date de début'),
                                   _('Date de fin'),
                                   _('Nom de l\'article chez le fournisseur'),
                                   _(u'Référence Fournisseur de la finition'),
                                   _('Erreur constatée')
                                   ]
                    csv_writer.writerow(csv_headers)

                    for row in reader:
                        try:
                            finition_id = attribute_obj.with_context(For_price=True).get_finition_by_name(row)
                            product_tmpl_id = product_template_obj.with_context(For_price=True).get_product_template_by_name(row)
                            if not finition_id:
                                error_line = [
                                    row.get('Id Externe du fournisseur'),
                                    row.get('Nom du fournisseur'),
                                    row.get('Libellé simple de l\'article'),
                                    row.get('Référence fournisseur'),
                                    row.get('Finition'),
                                    row.get('Code finition'),
                                    row.get('Quantité minimale'),
                                    row.get('Prix d\'Achat'),
                                    row.get('T|P'),
                                    row.get('Date de début'),
                                    row.get('Date de fin'),
                                    row.get(
                                        'Nom de l\'article chez le fournisseur'),
                                    row.get('Référence Fournisseur de la finition'),
                                    "{} {}".format( 'Has no supplier , ' if not res_partner_obj.get_partner_by_name(row.get('Nom du fournisseur')) else '', 'No items, ' if not product_tmpl_id else '')
                                ]
                                csv_writer.writerow(error_line)

                                if not is_error:
                                    is_error = True
                                new_cr.rollback()

                            else:
                                # if row.get('Code finition') == 'B2' and row.get('Référence fournisseur') == 'CID.PRV.A042':
                                #     product = self.env['product.product'].browse(finition_id)
                                #     print(product.product_tmpl_id)
                                #     print(product_tmpl_id)
                                #     print(row)
                                vals = {
                                    'name': res_partner_obj.get_partner_by_name(row.get('Nom du fournisseur')),
                                    'product_tmpl_id': product_tmpl_id,
                                    'product_code': row.get('Référence fournisseur'),
                                    'product_id': finition_id,
                                    'finish_code': row.get('Code finition'),
                                    'min_qty': row.get('Quantité minimale'),
                                    'price': row.get('Prix d\'Achat').replace(',', '.'),
                                    'tp': self.get_t_p(row.get('T|P')),
                                    'date_start': self.convert_to_date(row.get('Date de début')),
                                    'date_end': self.convert_to_date(row.get('Date de fin')),
                                    'product_name': row.get('Nom de l\'article chez le fournisseur'),
                                    # 'product_code': row.get('Référence Fournisseur de la finition'),
                                }
                                # seller = seller_obj.search(
                                #     [('product_id', '=', finition_id),
                                #      ('min_qty', '=', row.get(
                                #          'Quantité minimale').replace(',', '.')),
                                #      ('finish_code', 'in',( row.get('Code finition'), 'NO')),
                                #      ('product_tmpl_id', '=', product_tmpl_id)
                                #      ], limit=1)
                                product_tmpl = self.env['product.template'].browse(product_tmpl_id)
                                qty_min = row.get('Quantité minimale').replace(',', '.')
                                qty_min = float(qty_min) if isfloat(qty_min) else 0
                                seller = product_tmpl.seller_ids.filtered(lambda s: s.product_id.id == finition_id and s.min_qty == qty_min)
                                if seller:
                                    seller[0].write(vals)
                                else:
                                    seller_obj.create(vals)
                                if reader.line_num % 150 == 0:
                                    logger.info(
                                        _("Import in progress ... %s lines treated." % reader.line_num))
                                self._cr.commit()

                        except Exception as error:
                            error_line = [
                                row.get('Id Externe du fournisseur'),
                                row.get('Nom du fournisseur'),
                                row.get('Libellé simple de l\'article'),
                                row.get('Référence fournisseur'),
                                row.get('Finition'),
                                row.get('Code finition'),
                                row.get('Quantité minimale'),
                                row.get('Prix d\'Achat'),
                                row.get('T|P'),
                                row.get('Date de début'),
                                row.get('Date de fin'),
                                row.get('Nom de l\'article chez le fournisseur'),
                                row.get('Référence Fournisseur de la finition'),
                                repr(error)
                            ]
                            csv_writer.writerow(error_line)

                            if not is_error:
                                is_error = True
                            new_cr.rollback()
                    logger.info(_("End Import Of %s Successfully." %
                                  template.file_name))
                except Exception as error:
                    logger.error(repr(error))
                    new_cr.rollback()

                if is_error and template.export_xls:
                    binary_file = base64.b64encode(
                        csv_data.getvalue().encode('utf-8-sig'))
                    # binary_file = base64.b64encode(bytes(csv_data.getvalue(), 'utf-8'))
                    file_name = 'PRODUCT_SUPPLIER_INFO_%s.csv' % fields.Datetime.now().replace(':', '').replace(
                        '-', '').replace(' ', '')
                    self.add_attachment(template.id, binary_file, file_name)
        return  True

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
