# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Account(models.Model):
    _inherit = 'account.account'

    @api.model
    def get_account_by_code(self, code):
        """
        Get account by code
        :param code: code of account
        :return: account.account
        """
        return self.search([('code', '=', code)], limit=1)

