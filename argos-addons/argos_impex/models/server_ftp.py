# -*- coding: utf-8 -*-

import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class ServerFTP(models.Model):
    _inherit = 'server.ftp'

    def callback(self, data=None):
        """
        To be overrided to process retrieved data
        :param data:
        :return:
        """
        super(ServerFTP, self).callback(data)
        if not self._context.get('template'):
            return
        product_tmpl_obj = self.env['product.template']
        model_import_obj = self.env['ir.model.import.template']
        template = model_import_obj.browse(self._context.get('template'))
        logger = self._context.get('logger')
        product_tmpl_obj.processing_import_data(data.decode('utf-8'), template, logger)
        return True
