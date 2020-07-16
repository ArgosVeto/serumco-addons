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
        model_import_obj = self.env['ir.model.import.template']
        template = model_import_obj.browse(self._context.get('template'))
        logger = self._context.get('logger')
        if self._context.get('source') == 'produit-general':
            product_tmpl_obj.processing_import_data(datas.decode('utf-8'), template, logger)
        elif self._context.get('source') == 'tarif':
            product_tmpl_obj.processing_import_list_price_data(datas.decode('utf-8'), template, logger)
        return True
