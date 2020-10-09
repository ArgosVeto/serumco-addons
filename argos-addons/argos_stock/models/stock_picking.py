# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_arg_prescription = fields.Boolean('Is prescription')
    is_duplicate = fields.Boolean('Is Duplicate')

    def action_prescription_send(self):
        self.ensure_one()
        template = self.env.ref('argos_stock.mail_template_prescription_send')
        lang = self.env.context.get('lang')
        if template.lang:
            lang = template._render_template(template.lang, 'stock.picking', self.id)
        context = {
            'default_model': 'stock.picking',
            'default_res_id': self.id,
            'default_use_template': bool(template.id),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': context,
        }

    def make_duplicate(self):
        self.ensure_one()
        self.is_duplicate = True
        return True

