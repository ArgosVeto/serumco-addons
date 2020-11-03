# -*- coding: utf-8 -*-

import logging
from zipfile import ZipFile
from io import StringIO, BytesIO

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ServerFTP(models.Model):
    _inherit = 'server.ftp'

    def retrieve_data(self):
        """
        :return:
        """
        datas = super(ServerFTP, self).retrieve_data()
        if not self._context.get('template'):
            return datas
        product_tmpl_obj = self.env['product.template']
        product_attr_obj = self.env['product.attribute']
        model_import_obj = self.env['ir.model.import.template']
        partner_obj = self.env['res.partner']
        template = model_import_obj.browse(self._context.get('template'))
        logger = self._context.get('logger')
        source = self._context.get('source')
        if source == 'produit-general':
            return product_tmpl_obj.processing_import_data(datas.decode('utf-8'), template, source, logger)
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
        if source == 'produit-catalogue-global':
            zf = ZipFile(BytesIO(datas), 'r')
            for fileInfo in zf.infolist():
                return product_tmpl_obj.processing_import_catalogue_global_data(zf.read(fileInfo).decode('ISO-8859-1'),
                                                                                template, source, logger)
        if source == 'contacts':
            return partner_obj.processing_import_contact(datas.decode('utf-8'), template, logger)
        if source == 'patients':
            return partner_obj.processing_import_patient(datas.decode('utf-8'), template, logger)
        return False
