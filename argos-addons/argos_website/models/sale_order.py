# -*- coding: utf-8 -*-

import csv
import io
import base64

from odoo import api, models
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        self.filtered(lambda so: so.website_id).generate_centravet_orders()
        new_orders = self.filtered(lambda so: not so.partner_id.has_activity)
        new_orders.send_first_mail()
        new_orders.mapped('partner_id').write({'has_activity': True})
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
                operating_unit = order.operating_unit_id
                if operating_unit.click_and_collect:
                    code = operating_unit.web_shop_id
                    password = operating_unit.web_shop_password
                else:
                    code = operating_unit.code
                    password = operating_unit.password
                csv_writer.writerow([order.name,
                                     partner.email or '',
                                     partner.name,
                                     partner_shipping.street or '',
                                     partner_shipping.street2 or '',
                                     partner_shipping.zip or '',
                                     partner_shipping.city or '',
                                     partner.phone or partner.mobile or '',
                                     code or '',
                                     baseurl or '',
                                     operating_unit.email or '',
                                     '',
                                     password or '',
                                     'WVTCDK',
                                     code_version or '',
                                     line.product_id.default_code or '',
                                     int(line.product_uom_qty),
                                     '',
                                     'N',
                                     0,
                                     subscriber_code or '',
                                     watermark or '',
                                     '',
                                     '',
                                     ''])
            sequence = self.env['ir.sequence'].next_by_code('centravet.sale.order.seq')
            filename = '%sV%s.WBV' % (code, sequence)
            file_path = '%s%s' % (server.filename, filename)
            order.save_centravet_attachment(filename, csv_data)
            try:
                server.store_data(file_path, csv_data)
            except Exception as e:
                _logger.error(repr(e))
        return True

    def send_first_mail(self):
        for rec in self:
            try:
                email_template = self.env.ref('argos_website.website_welcome_mail_template')
                email_template.send_mail(rec.id, force_send=True, raise_exception=True)
            except Exception as e:
                _logger.error(repr(e))
        return True

    def save_centravet_attachment(self, filename, content):
        self.ensure_one()
        if not filename or not content:
            return
        self.env['ir.attachment'].create({
            'type': 'binary',
            'res_model': self._name,
            'res_id': self.id,
            'datas': base64.b64encode(content.getvalue().encode('utf-8')),
            'name': filename
        })
