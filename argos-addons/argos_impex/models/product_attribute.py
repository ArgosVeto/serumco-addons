# -*- coding: utf-8 -*-

import csv
import io
import base64

from odoo import models, fields, registry, api, _


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    centravet_id = fields.Char('Centravet Id', required=False)

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
            try:
                vals = {
                    'centravet_id': row.get('filtre'),
                    'name': row.get('libelle'),
                    'create_variant': 'dynamic',
                }
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
