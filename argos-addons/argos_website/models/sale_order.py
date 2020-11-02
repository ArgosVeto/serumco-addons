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
        orders = self.filtered(lambda so: so.website_id)
        new_orders = orders.filtered(lambda so: not so.partner_id.has_activity)
        new_orders.send_first_mail()
        new_orders.mapped('partner_id').write({'has_activity': True})
        orders.send_review_email()
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
                                     order.operating_unit_id.code,
                                     baseurl or '',
                                     order.operating_unit_id.email,
                                     '',
                                     order.operating_unit_id.password,
                                     'WVTCDK',
                                     code_version or '',
                                     line.product_id.default_code,
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
            filename = '%s%sV%s.WBV' % (server.filename, order.operating_unit_id.code, sequence)
            server.store_data(filename, csv_data)
        return True

    def send_first_mail(self):
        for rec in self:
            try:
                email_template = self.env.ref('argos_website.website_welcome_mail_template')
                email_template.send_mail(rec.id, force_send=True, raise_exception=True)
            except Exception as e:
                _logger.error(repr(e))
        return True

    def send_review_email(self):
        for rec in self:
            try:
                email_template = self.env.ref('argos_website.review_mail_template')
                email_template.send_mail(rec.id, force_send=True, raise_exception=True)
            except Exception as e:
                _logger.error(repr(e))
        return True
