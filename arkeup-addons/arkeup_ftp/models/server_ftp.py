# -*- coding: utf-8 -*-

import logging

from ftplib import FTP

from odoo import models, fields, api, _
from odoo.exceptions import Warning

_logger = logging.getLogger(__name__)

datas = []

class ServerFTP(models.Model):
    _name = 'server.ftp'
    _description = 'Server FTP'

    name = fields.Char(copy=False)
    url = fields.Char('URL', required=True)
    login = fields.Char('Login')
    password = fields.Char('Password')
    filename = fields.Char('Filename', default='/', required=True,
                           help="Complete remote path of the file to be downloaded")
    active = fields.Boolean(default=True)

    @api.model
    def default_get(self, fields):
        res = super(ServerFTP, self).default_get(fields)
        if not res.get('name') and 'name' not in res:
            res.update({'name': self.env['ir.sequence'].next_by_code('server.ftp.seq')})
        return res

    def connect(self):
        self.ensure_one()
        _logger.info(_('starting ftp connection ...'))
        ftp = FTP(self.url)
        ftp.set_pasv(False)
        ftp.login(self.login, self.password)
        _logger.info(_('connection established succesfully.'))
        return ftp

    def retrieve_data(self):
        """
        retrieve data in memory
        :return:
        """
        self.ensure_one()
        ftp = self.connect()
        datas = []
        ftp.retrbinary('RETR ' + self.filename, lambda block: datas.append(block))
        return b''.join(datas)

    def button_check_connection(self):
        """
        check if all parameters are correctly set
        :return:
        """
        if self.connect():
            title = _("Connection Test Succeeded!")
            message = _("Everything seems properly set up!")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {'title': title, 'message': message, 'sticky': False}
            }

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals.update({'name': self.env['ir.sequence'].next_by_code('server.ftp.seq')})
        return super(ServerFTP, self).create(vals)
