# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ServerFTP(models.Model):
    _inherit = 'server.ftp'

    def retrieve_data(self):
        """
        :return:
        """
        datas = super(ServerFTP, self).retrieve_data()
        if not self._context.get('template') or not datas:
            return False
        product_tmpl_obj = self.env['product.template']
        product_attr_obj = self.env['product.attribute']
        model_import_obj = self.env['ir.model.import.template']
        template = model_import_obj.browse(self._context.get('template'))
        logger = self._context.get('logger')
        source = self._context.get('source')
        if source == 'produit-general':
            return product_tmpl_obj.processing_import_data(datas.decode('utf-8'), template, source, logger)
        if source == 'tarif':
            return product_tmpl_obj.processing_import_list_price_data(datas.decode('utf-8'), template, source, logger)
        if source == 'stock':
            return product_tmpl_obj.processing_import_stock_data(datas.decode('utf-8'), template, source, logger)
        if source == 'produit-association':
            return product_tmpl_obj.processing_import_product_association_data(datas.decode('utf-8'), template, source, logger)
        if source == 'produit-documentation':
            return product_tmpl_obj.processing_import_product_documentation_data(datas.decode('utf-8'), template, source, logger)
        if source == 'produit-regroupement':
            return product_tmpl_obj.processing_import_product_regroupment_data(datas.decode('utf-8'), template, source, logger)
        if source == 'produit-reglementation':
            return product_tmpl_obj.processing_import_product_reglementation_data(datas.decode('utf-8'), template, source, logger)
        if source == 'produit-enrichi':
            return product_tmpl_obj.processing_import_product_enrichi_data(datas.decode('utf-8'), template, source, logger)
        if source == 'referentiel-filtre':
            return product_attr_obj.processing_import_referentiel_filtre_data(datas.decode('utf-8'), template, source, logger)
        if source == 'produit-filtre':
            return product_tmpl_obj.processing_import_produit_filtre_data(datas.decode('utf-8'), template, source, logger)
        return False
