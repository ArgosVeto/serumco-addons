# -*- coding: utf-8 -*-

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        res = super(WebsiteSale, self).shop(page, category, search, ppg, **post)
        attributes = res.qcontext.get('attributes', False)
        if attributes:
            res.qcontext.update(attributes=attributes.filtered(lambda attr: attr.is_attribute_visible))
        return res