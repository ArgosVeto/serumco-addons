# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class WebsiteController(http.Controller):

    @http.route('/mrdv/home', type='http', auth='public', method=['POST'])
    def mrdv_index(self, **post):
        """
        :param post:
        :return:
        """
        return request.render('argos_website.mrdv_home', {})
