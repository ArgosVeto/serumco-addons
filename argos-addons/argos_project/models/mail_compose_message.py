# -*- coding: utf-8 -*-

from odoo import models, fields, _
import logging
import base64

_logger = logging.getLogger(__name__)


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    is_report = fields.Boolean('Report', default=False)

    def action_send_mail(self):
        if self.is_report:
            pdf = self.env.ref('argos_project.report_surgery_pdf').render_qweb_pdf(self.ids, data={'body': self.body})
            b64_pdf = base64.b64encode(pdf[0])
            name = _('surgery_report')
            self.env['ir.attachment'].create({
               'name': name + '.pdf',
               'type': 'binary',
               'datas': b64_pdf,
               'datas_fname': name + '.pdf',
               'store_fname': name,
               'res_model': self.model,
               'res_id': self.res_id,
               'mimetype': 'application/pdf'
            })
        self.send_mail()
        return {'type': 'ir.actions.client', 'tag': 'reload', 'infos': 'mail_sent'}

