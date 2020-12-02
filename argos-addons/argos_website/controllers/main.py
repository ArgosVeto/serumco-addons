# -*- coding: utf-8 -*-

import odoo
from odoo import http, _
from odoo.http import request
from odoo.addons.web.controllers.main import Home
from odoo.addons.web.controllers.main import ensure_db


class WebsiteController(Home):

    @http.route('/mrdv/home', type='http', auth='public', method=['POST'])
    def mrdv_index(self, **post):
        """
        :param post:
        :return:
        """
        return request.render('argos_website.mrdv_home', {})

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        request.params['login_success'] = False
        values = request.params.copy()
        if request.httprequest.method == 'POST':
            try:
                request.session.authenticate(request.session.db, request.params['login'], request.params['password'])
            except odoo.exceptions.AccessDenied:
                if request.env['res.users'].sudo().search([('login', '=', request.params['login'])]):
                    values['error'] = _('Wrong password')
                else:
                    values['error'] = _('This email does not match to any Argos account')
                response = request.render('web.login', values)
                response.headers['X-Frame-Options'] = 'DENY'
                return response
        return super(WebsiteController, self).web_login(*args, **kw)
