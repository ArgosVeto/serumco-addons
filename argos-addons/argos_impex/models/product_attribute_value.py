# -*- coding: utf-8 -*-
from odoo import models, api, fields, _

import logging
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)



class ProductAttributeValue(models.Model):
    _inherit = "product.attribute.value"

    _sql_constraints = [
        ('value_company_uniq', 'CHECK(1=1)',
         'This attribute value already exists !')
    ]

    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        store=True,
        related="attribute_id.partner_id")

    @api.model
    def get_new_finition(self, variant, tmpl_id):
        products = self.env['product.roduct'].search(
            [('product_tmpl_id', '=', tmpl_id.id), ('attribute_value_ids', 'in', variant.ids)])
        return products

    def archive_duplicate(self, vals):
        suppl_id = self.env['product.supplierinfo.finition'].browse([vals])
        suppl_id.write({'active': False})
        try:
            suppl_id.unlink()
        except UserError as e:
            _logger.error(e)
        return True

    @api.model
    def remove_duplicate(self):
        partner_ids = self.env['res.partner'].search([('supplier', '=', True)])
        suppinfo_finition_obj = self.env['product.supplierinfo.finition']
        for partner_id in partner_ids:
            self.env.cr.execute(
                """
                SELECT DISTINCT name,finish_code,supplier_id
                from product_supplierinfo_finition
                where supplier_id in (%s);
                
                """,(partner_id.id,)
            )

            supp_info_ids = self.env.cr.fetchall()
            ids_lst = []
            for fintion in supp_info_ids:
                ids_lst.append(suppinfo_finition_obj.search([('name', '=', fintion[0]),
                                                         ('finish_code', '=', fintion[1]),
                                                         ('supplier_id', '=', fintion[2])],
                                                        order='id', limit=1).id)
            info_ids = suppinfo_finition_obj.search([('id', 'not in', ids_lst), ('supplier_id', '=', partner_id.id)])
            if info_ids:
                for data in info_ids:
                    data.write({'name': 'To drop', 'finish_code' : 'To drop'})
                    self.archive_duplicate(data.id)

        return True

    @api.model
    def get_finition_by_name(self, row):
        if not row.get('Nom du fournisseur'):
            return False
        partner_id = self.env['res.partner'].get_partner_by_name(row.get('Nom du fournisseur'))
        if not partner_id:
            return False
        product_obj = self.env['product.product']
        product_tpl_obj = self.env['product.template']
        suppinfo_finition_obj = self.env['product.supplierinfo.finition']
        variant_obj = self.env['product.attribute.value']
        if self._context.get('For_price'):
            product_tmpl_id_active = product_tpl_obj.search(
                [('ref_supplier', '=', row.get('Référence fournisseur')), ('supplier_id', '=', partner_id)], limit=1)
            if not product_tmpl_id_active:
                product_tmpl_id = product_tpl_obj.search([('ref_supplier', '=', row.get('Référence fournisseur')), ('supplier_id', '=', partner_id),
                                               ('active', '!=', True)], limit=1)
            else:
                product_tmpl_id = product_tmpl_id_active
        else:
            product_tmpl_id = product_tpl_obj.search(
                [('name', '=', row.get('Libellé simple de l\'article')), ('supplier_id', '=', partner_id)])
        if product_tmpl_id:
            if row.get('Finition') in ('Toutes', '', False, 'non'):
                # get list of finition id in seller_ids
                finition=product_tmpl_id.seller_ids.mapped('product_id')
                for f_id in finition:
                    # for each seller_ids with this finition: find if qty exist
                    seller_ids = product_tmpl_id.seller_ids.filtered(lambda r: r.product_id and r.product_id.id == f_id.id)
                    qty_min_import = row.get('Quantité minimale')
                    # get line with the qty imported
                    line=seller_ids.filtered(lambda r: r.min_qty == float(qty_min_import))
                    if line:
                        line.write({'price': row.get('Prix d\'Achat').replace(',', '.')})
                    else:
                        if seller_ids:
                            seller_ids[0].copy({
                                'is_copy': True,
                                'price': row.get('Prix d\'Achat').replace(',', '.'),
                                'min_qty': qty_min_import,
                            })
                    # for line in seller_ids:
                    #
                    #     qty_min_import = row.get('Quantité minimale')
                    #     # get line with the qty imported
                    #     if line.min_qty == qty_min_import:
                    #         line.write({'price': row.get('Prix d\'Achat').replace(',', '.')})
                    #     else:
                    #         # if qty doent existe: create ne line
                    #         line.copy({
                    #             'is_copy': True,
                    #             'price': row.get('Prix d\'Achat').replace(',', '.'),
                    #             'min_qty': qty_min_import,
                    #         })
                return line.product_id.id
            else:
                product_variant_ids = product_tmpl_id.product_variant_ids
                attribute_values = product_variant_ids.mapped('attribute_value_ids')

                characteristic = attribute_values.filtered_from_domain([('name', '=', row.get('Finition')),
                                                                        ('partner_id', '=', partner_id),
                                                                        ('finish_code', 'in', (row.get('Code finition'), 'NO'))
                                                                        ])

                if characteristic and characteristic.product_ids:
                    return characteristic.product_ids.filtered(lambda p: p.product_tmpl_id.id == product_tmpl_id.id)[0].id
                elif characteristic and not characteristic.product_ids:
                    product_id = product_obj.create({
                        'name': product_tmpl_id.name,
                        'product_tmpl_id': product_tmpl_id.id,
                        'attribute_value_ids': [(4, characteristic.id)],
                        'finish_code': row.get('Code finition'),
                        'tp': self.env['product.supplierinfo'].get_t_p(row.get('T|P')),
                    })
                    return product_id.id
                else:

                    variant_id = variant_obj.search([('name', '=', row.get('Finition')),('finish_code', 'in', (row.get('Code finition'), 'No', '', False) ),
                                                     ('partner_id', '=', partner_id)])
                    if not variant_id:
                        variant_id = self.env['product.attribute.value'].with_context(product=True, supplier=partner_id).create(
                            {'attribute_id': self.env['res.partner'].browse([partner_id]).attribute_id.id,
                             'name': row.get('Finition'),
                             'finish_code': row.get('Code finition'),
                             'partner_id': partner_id,
                             'tp': self.env['product.supplierinfo'].get_t_p(row.get('T|P'))
                             }
                        )

                    for attribute_line in product_tmpl_id.attribute_line_ids:
                        for attribute in attribute_line.attribute_id:
                            attribute.write({
                                'value_ids': [(4, variant_id.id)]
                            })
                            attribute_line.write({
                                'value_ids': [(4, variant_id.id)]
                            })

                    new_product = product_obj.create({
                        'name': product_tmpl_id.name,
                        'product_tmpl_id': product_tmpl_id.id,
                        'attribute_value_ids': [(4, variant_id.id)],
                        'finish_code': row.get('Code finition'),
                        'tp': self.env['product.supplierinfo'].get_t_p(row.get('T|P')),
                    })
                    return new_product.id
        return False
