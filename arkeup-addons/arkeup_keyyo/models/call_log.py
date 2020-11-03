# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CallLog(models.Model):
    _name = 'call.log'
    _rec_name = 'partner_id'
    _order = 'date desc'
    _description = 'Call Log'

    @api.model
    def default_get(self, default_fields):
        res = super(CallLog, self).default_get(default_fields)
        if 'date' not in res and not res.get('date'):
            res['date'] = fields.Datetime.now()
        return res

    user_id = fields.Many2one('res.users', 'User')
    caller_number = fields.Char('Caller Number')
    date = fields.Datetime('Date')
    callee_number = fields.Char('Callee Number')
    partner_id = fields.Many2one('res.partner', 'Contact Callee')
    type = fields.Selection([('incoming', 'Incoming'), ('outgoing', 'Outgoing')], 'Type', default='outgoing')
    status = fields.Integer('Status')
    url = fields.Text('URL')
    message = fields.Text('Message')
