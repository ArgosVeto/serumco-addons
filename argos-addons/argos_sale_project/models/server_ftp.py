# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ServerFtp(models.Model):
    _inherit = 'server.ftp'

    def retrieve_file_data(self, filename=''):
        self.ensure_one()
        ftp = self.connect()
        datas = []
        ftp.retrbinary('RETR ' + filename, lambda block: datas.append(block))
        ftp.close()
        return b''.join(datas)