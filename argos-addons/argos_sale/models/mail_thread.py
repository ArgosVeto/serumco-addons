# -*- coding: utf-8 -*-

from odoo import models, _


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _get_creation_message(self):
        if not self._context.get('default_is_consultation', False):
            return super(MailThread, self)._get_creation_message()
        return _('Consult created')