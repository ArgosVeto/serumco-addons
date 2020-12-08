# -*- coding: utf-8 -*-

import logging
from odoo import models

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def _send_rating_mail(self):
        for rec in self:
            try:
                email_template = self.env.ref('helpdesk.rating_ticket_request_email_template')
                email_template.send_mail(rec.id, raise_exception=True)
            except Exception as e:
                _logger.error(repr(e))
        return True

    def write(self, vals):
        res = super(HelpdeskTicket, self).write(vals)
        solved_stage = self.env.ref('helpdesk.stage_solved', raise_if_not_found=False)
        if vals.get('stage_id') and solved_stage and vals['stage_id'] == solved_stage.id:
            self._send_rating_mail()
        return res