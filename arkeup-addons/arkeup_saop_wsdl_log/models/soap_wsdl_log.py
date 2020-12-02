# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SoapWsdlLog(models.Model):
    _name = 'soap.wsdl.log'
    _description = 'Soap Wsdl Log'
    _order = 'name desc'

    @api.model
    def default_get(self, fields_list):
        res = super(SoapWsdlLog, self).default_get(fields_list)
        if not res.get('name') and 'name' not in res:
            res.update({'name': self.env['ir.sequence'].next_by_code('soap.wsdl.log.seq')})
        return res

    name = fields.Char()
    description = fields.Char('Description', required=False)
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
