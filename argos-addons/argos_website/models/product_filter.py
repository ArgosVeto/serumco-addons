# -*- coding: utf-8 -*-
import csv
import io
import base64
from odoo import models, fields, api, registry, _

class ProductFilter(models.Model):
    _name = 'product.filter'

    name = fields.Char('Name')
    is_filter_visible = fields.Boolean('Filter visible in web')
    product_filter_line_ids = fields.One2many('product.filter.line', 'product_filter_id', 'Product filter lines')

    filters_line_ids = fields.One2many('product.template.filter.line', 'filter_id', 'Lines')
    product_tmpl_ids = fields.Many2many('product.template', string="Related Products", compute='_compute_products', store=True)

    centravet_id = fields.Char('Centravet Id', required=False)

    @api.model
    def processing_import_referentiel_filtre_data(self, content=None, template=False, source=False, logger=False):
        """
        Import variant attributes
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
        for row in reader:
            print(row)
            try:
                vals = {
                    'centravet_id': row.get('filtre'),
                    'name': row.get('libelle'),
                    # 'create_variant': 'dynamic',
                }
                print('vals=', vals)
                if not self.search([('centravet_id', '=', row.get('filtre'))], limit=1):
                    self.create(vals)
            except Exception as e:
                logger.error(repr(e))
                self._cr.rollback()
        return True

    @api.model
    def get_attribute_by_name(self, name=False):
        """
        Get attribute by centravet Id
        :param name:
        :return:
        """
        return self.search([('centravet_id', '=', name)], limit=1)

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
                    if not template or not source:
                        logger.error(_('There is nothing to import.'))
                        return False
                    if template.is_remote_import:
                        if not template.server_ftp_id:
                            return False
                        template.server_ftp_id.with_context(template=template.id, logger=logger, source=source).retrieve_data()
                    elif template.import_file:
                        content = base64.decodebytes(template.import_file).decode('utf-8-sig')
                        if source == 'referentiel-filtre':
                            return self.processing_import_referentiel_filtre_data(content, template, source)
                except Exception as e:
                    logger.error(repr(e))
                    self._cr.rollback()

    @api.depends('filters_line_ids.product_id')
    def _compute_products(self):
        for pa in self:
            pa.product_tmpl_ids = pa.filters_line_ids.product_id

class ProductFilterLine(models.Model):
    _name = 'product.filter.line'

    name = fields.Char('Name')
    product_filter_id = fields.Many2one('product.filter')

    @api.model
    def manage_attribute_values(self, values=False, attribute=False, logger=False, errors=[]):
        """
        Get attribute value
        :param name:
        :return:
        """
        if not values or not attribute:
            return False
        attribute_values = self.env['product.filter.line']
        for item in values:
            try:
                value = self.search([('name', '=', item[3]), ('product_filter_id', '=', attribute.id)], limit=1)
                if not value:
                    value = self.create({'name':  item[3], 'product_filter_id': attribute.id})
                attribute_values |= value
                self._cr.commit()
            except Exception as e:
                logger.error(repr(e))
                errors.append((item, repr(e)))
                self._cr.rollback()
        return attribute_values


class ProductTemplateFilter(models.Model):
    _inherit = 'product.template'

    product_filter_ids = fields.One2many("product.template.filter.line", 'product_id')

class ProductTemplateFilterline(models.Model):
    _name = 'product.template.filter.line'

    active = fields.Boolean(default=True)
    filter_id = fields.Many2one('product.filter')
    filter_line_ids = fields.Many2many('product.filter.line', domain="[('product_filter_id', '=', filter_id)]",)
    product_id = fields.Many2one('product.template')
