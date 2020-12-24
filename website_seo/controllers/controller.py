# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
# import logging
# _logger = logging.getLogger(__name__)
import re
class WebsiteSale(WebsiteSale):

    @http.route(['/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False,brand=None, **post):
        response=super(WebsiteSale,self).shop(page=page, category=category, search=search,ppg=ppg,brand=None,**post)
        if category and ('/shop/category/' in request.httprequest.url) and category.website_meta_title:
            response.qcontext.update({'main_object': category})
            if page:
                category.sudo().website_meta_title += '|page-' + str(page)
            else:
                meta_title = re.sub(r'(?<=page).*', '',
                                    category.website_meta_title)
                category.sudo().website_meta_title = meta_title.rstrip('|page')

        return response
