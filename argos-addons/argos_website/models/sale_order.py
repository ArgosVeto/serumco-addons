# -*- coding: utf-8 -*-

import csv
import io

from odoo import api, models
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        try:
            self.filtered(lambda so: so.website_id).generate_centravet_orders()
        except Exception as e:
            _logger.error(repr(e))
        return res

    def generate_centravet_orders(self):
        """
        Generate csv order and send it to the centravet FTP
        :return:
        """
        baseurl = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        watermark = self.env['ir.config_parameter'].sudo().get_param('centravet.watermark')
        subscriber_code = self.env['ir.config_parameter'].sudo().get_param('centravet.subscriber_code')
        code_version = self.env['ir.config_parameter'].sudo().get_param('code.version')
        server = self.env.ref('argos_sale.server_ftp_argos_sale_order_data', raise_if_not_found=False)
        for order in self:
            csv_data = io.StringIO()
            csv_writer = csv.writer(csv_data, delimiter=',')
            partner = order.partner_id
            partner_shipping = order.partner_shipping_id
            for line in order.order_line:
                csv_writer.writerow([order.name,
                                     partner.email or '',
                                     partner.name,
                                     partner_shipping.street or '',
                                     partner_shipping.street2 or '',
                                     partner_shipping.zip or '',
                                     partner_shipping.city or '',
                                     partner.phone or partner.mobile or '',
                                     order.operating_unit_id.centravet_code,
                                     baseurl or '',
                                     order.operating_unit_id.email,
                                     '',
                                     order.operating_unit_id.password,
                                     'CDK',
                                     code_version or '',
                                     line.product_id.default_code,
                                     line.product_uom_qty,
                                     '',
                                     'N',
                                     '',
                                     subscriber_code or '',
                                     watermark or '',
                                     '',
                                     '',
                                     ''])
            sequence = self.env['ir.sequence'].next_by_code('centravet.sale.order.seq')
            filename = '%s%sV%s.WBV.csv' % (server.filename, order.operating_unit_id.code, sequence)
            server.store_data(filename, csv_data)
        return True
