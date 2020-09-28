# -*- coding: utf-8 -*-

import csv
import io
import base64
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('approved', 'Approved'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ])

    def button_confirm(self):
        if self._context.get('standard_process', False):
            context = dict(self.env.context, wait_discount=True)
            return {
                'name': _('Confirmation'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'purchase.confirmation.wizard',
                'views': [(False, 'form')],
                'target': 'new',
                'context': context,
            }

        return super(PurchaseOrder, self).button_confirm()

    def button_release(self):
        if self._context.get('standard_process', False):
            carrier_id = self.partner_id.property_delivery_carrier_id
            if carrier_id and self.amount_untaxed < carrier_id.amount:
                context = dict(self.env.context, shipping_fees=True)
                return {
                    'name': _('Confirmation'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'purchase.confirmation.wizard',
                    'views': [(False, 'form')],
                    'target': 'new',
                    'context': context,
                }
        for rec in self:
            rec.send_order_mail()

        return super(PurchaseOrder, self).button_release()

    def send_order_mail(self):
        try:
            email_template = self.sudo().env.ref('argos_purchase.purchase_order_edi_mail_template_data')
            email_values = {}
            mail_attachments = self.generate_purchase_mail_attachment(self.partner_id.is_centravet)
            email_values.update({'attachment_ids': [(6, 0, mail_attachments.ids)]})
            email_template.sudo().send_mail(self.id, force_send=True, email_values=email_values, raise_exception=True)
        except Exception as e:
            _logger.error(repr(e))

    @api.model
    def get_centravet_subscriber_code(self):
        return self.env['ir.config_parameter'].sudo().get_param('centravet.subscriber_code')

    def generate_purchase_mail_attachment(self, centravet=False):
        if centravet:
            file_data = base64.b64encode(self.generate_purchase_edi_file().getvalue().encode('utf-8'))
            sequence = self.env['ir.sequence'].next_by_code('centravet.purchase.order.seq')
            file_name = self.get_centravet_subscriber_code() + 'C' + sequence + '.csv'
        else:
            file_data = base64.b64encode(self.generate_purchase_report_file())
            file_name = self.name + '.pdf'
        return self.env['ir.attachment'].create({
            'name': file_name,
            'datas': file_data,
            'datas_fname': file_name,
        })

    def generate_purchase_report_file(self):
        report = self.env.ref('purchase.action_report_purchase_order')
        result, format = report.render_qweb_pdf([self.id])
        return result

    def generate_purchase_edi_file(self):
        subscriber_code = self.get_centravet_subscriber_code()
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data, delimiter=',')
        for line in self.order_line:
            csv_writer.writerow([
                self.name,
                subscriber_code,
                self.operating_unit_id.email or '',
                self.operating_unit_id.password or '',
                self.operating_unit_id.code or '',
                line.product_id.cip or '',
                line.product_qty or 0,
                line.name or '',
                'PYXIS',
                '',
                '',
                '',
                fields.Date.from_string(line.date_planned).strftime('%Y%m%d') or '',
                ''
            ])
        return csv_data
