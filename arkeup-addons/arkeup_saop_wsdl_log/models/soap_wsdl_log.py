# -*- coding: utf-8 -*-

from odoo import models, fields


class SoapWsdlLog(models.Model):
    _name = 'soap.wsdl.log'
    _description = 'Soap Wsdl Log'

    name = fields.Char()
    partner_id = fields.Many2one('res.partner', 'Partner')
    res_id = fields.Integer('Res Id', required=True)
    model_id = fields.Many2one('ir.model', 'Model', required=True)
    msg = fields.Text('Message SOAP')
    date = fields.Datetime('Sending Date')
    state = fields.Selection([('new', 'New'), ('successful', 'Successful'), ('error', 'Error')], 'State', default='new')
    reason = fields.Text('Detailed error message', readonly=True)
    user_id = fields.Many2one('res.users', 'Sender UID', readonly=True)

    def button_send_msg_soap(self):
        #to be overrided to add corresponding code
        pass
