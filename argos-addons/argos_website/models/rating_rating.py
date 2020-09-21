# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields
from werkzeug.urls import url_encode
import logging

_logger = logging.getLogger(__name__)


class RatingRating(models.Model):
    _inherit = 'rating.rating'
    _order = 'create_date desc'

    is_published = fields.Boolean('Is published', related='message_id.website_published')

    def open_website_url(self):
        self.ensure_one()
        rated_model = self.message_id.model
        rated_record_id = self.message_id.res_id
        rated_record = self.env[rated_model].browse(rated_record_id)
        if hasattr(rated_record, 'website_url'):
            return {
                'type': 'ir.actions.act_url',
                'url': rated_record.website_url,
                'target': 'self',
            }
        return False

    def create(self, vals):
        res = super(RatingRating, self).create(vals)
        res.send_creation_mail()
        return res

    def send_creation_mail(self):
        self.ensure_one()
        try:
            email_template = self.sudo().env.ref('argos_website.rating_mail_template_data')
            email_template.sudo().send_mail(self.id, force_send=True, raise_exception=True)
        except Exception as e:
            _logger.error(repr(e))

    def get_url(self):
        self.ensure_one()
        base_url = self.env["ir.config_parameter"].get_param("web.base.url")
        url_params = {
            'id': self.id,
            'view_type': 'form',
            'model': 'rating.rating',
            'menu_id': self.env.ref('argos_website.rating_rating_menuitem').id,
            'action': self.env.ref('rating.action_view_rating').id,
        }
        params = '/web?#%s' % url_encode(url_params)
        return base_url + params

    def get_mail_recipients(self):
        partner_ids = self.env.ref('argos_website.group_rating_management').users.mapped('partner_id')
        return ','.join(str(partner.id) for partner in partner_ids)

    def publish_message(self):
        self.ensure_one()
        self.message_id.website_published = True
        return True

    def unpublish_message(self):
        self.ensure_one()
        self.message_id.website_published = False
        return True
