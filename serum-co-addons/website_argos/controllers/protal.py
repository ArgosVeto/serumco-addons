# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Developed by Bizople Solutions Pvt. Ltd.

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
import werkzeug
from odoo import fields, http, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, date_utils
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website_sale.controllers.main import WebsiteSale
import urllib
from odoo.addons.portal.controllers.web import Home
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
import json
import base64
from datetime import datetime
from odoo.http import route, content_disposition
from odoo.exceptions import UserError


class AuthSignupHomeSS(AuthSignupHome):
    def check_password(self, passwd):
        special_sym = ['!', '@', '#', '$', '%', '^', '&', '*']
        val = True
        if len(passwd) < 10:
            val = False
        if not any(char.isdigit() for char in passwd):
            val = False
        if not any(char.isupper() for char in passwd):
            val = False
        if not any(char.islower() for char in passwd):
            val = False
        if not any(char in special_sym for char in passwd):
            val = False
        return val

    def do_signup(self, qcontext):
        vals_qcontext = {}
        if qcontext:
            vals_qcontext = dict(qcontext)
        values = {key: qcontext.get(key) for key in (
            'login', 'name', 'password', 'firstname', 'lastname')}
        chk_password = True
        if not values:
            raise UserError(_("The form was not properly filled in."))
        passwd = values.get('password')
        if values.get('password'):
            passwd = values.get('password')
            chk_password = self.check_password(passwd)
        if not chk_password:
            raise UserError(
                _("Your password must have at least 10 characters minimum, 1 uppercase, 1 lowercase, 1 special character, 1 figure "))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code,
                                _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '').split('_')[0]
        if lang in supported_lang_codes:
            values['lang'] = lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()


class CustomerPortal(CustomerPortal):

    MANDATORY_BILLING_FIELDS = ["firstname", "lastname", "phone",
                                "email", "street", "zipcode", "city", "country_id"]
    OPTIONAL_BILLING_FIELDS = ["state_id", "vat", "company_name"]

    @route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })
        error = False
        if post and request.httprequest.method == 'POST':
            error, error_message = self.details_form_validate(post)
            values.update(
                {'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key]
                          for key in self.MANDATORY_BILLING_FIELDS}
                values.update(
                    {key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                for field in set(['country_id', 'state_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                values.update({'zip': values.pop('zipcode', '')})
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


class AuthSignupHome(Home):
    @http.route()
    def web_login(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        if 'error' not in qcontext and qcontext.get('last_name'):
            last_name = qcontext.get('last_name')
            if last_name:
                current_user = request.env['res.users'].sudo().browse(
                    request.session.uid)
                current_user.partner_id.last_name = last_name
        return super(AuthSignupHome, self).web_login(*args, **kw)


class PortalContent(http.Controller):
    @http.route(['/job/resume-attachment'], type='json', auth="none")
    def customer_resume_attachment(self, **post):
        file_datas = str(post['file_upload1']).split(',')
        ir_attachment = request.env['ir.attachment'].sudo().create(
            {
                'name': post['file_name'],
                'datas': file_datas[1],
                'type': 'binary',
                'datas_fname':  post['file_upload1'],
                'mimetype': str(post['mimetype']),
            })
        return ir_attachment.id

    @http.route(['''/add-product-cart'''], type='http', auth="user", website=True)
    def add_product_cart(self, **post):
        if 'product_id' in post and post['product_id']:
            sale_order = request.website.sale_get_order(force_create=True)
            sale_order._cart_update(
                product_id=int(post['product_id']),
                add_qty=1,
            )
        return request.redirect('/my-content')

    @http.route(['''/my-appointment'''], type='http', auth="user", website=True)
    def my_appointment(self, **post):
        old_appointment_ids = False
        new_appointment_ids = False
        partner = request.env.user.partner_id
        if partner:
            now = fields.datetime.now()
            old_app_dommain = [('partner_id', '=', partner.id), ('mrdv_event_id', '!=', 0), (
                'start_datetime', '<=', now.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
            new_app_dommain = [('partner_id', '=', partner.id), ('mrdv_event_id', '!=', 0), (
                'start_datetime', '>=', now.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
            old_appointment_ids = request.env['planning.slot'].sudo().search(
                old_app_dommain, order="start_datetime desc")
            new_appointment_ids = request.env['planning.slot'].sudo().search(
                new_app_dommain, order="start_datetime")
        values = {'new_appointment_ids': new_appointment_ids,
                  'old_appointment_ids': old_appointment_ids}
        return request.env['ir.ui.view'].render_template("website_argos.my_appointment", values)

    @route(['''/planning/<model("planning.slot"):planning>/ics'''], type='http',
           auth="public")
    def event_ics_file(self, planning, **kwargs):
        files = planning._get_ics_file()
        if not planning.id in files:
            return request.not_found()
        content = files[planning.id]
        return request.make_response(content, [
            ('Content-Type', 'application/octet-stream'),
            ('Content-Length', len(content)),
            ('Content-Disposition', content_disposition('%s.ics' % planning.name))
        ])

    @http.route(['''/my-content'''], type='http', auth="user", website=True)
    def portal_content(self, **post):
        values = {}
        # erwq
        next_appointment_id = False
        pervious_appointment_id = False

        now = fields.datetime.now()
        partner = request.env.user.partner_id

        next_appointment_id = request.env['planning.slot'].sudo().search([('partner_id', '=', partner.id), ('mrdv_event_id', '!=', 0), (
            'start_datetime', '>=', now.strftime(DEFAULT_SERVER_DATETIME_FORMAT))], order="start_datetime", limit=1)
        pervious_appointment_id = request.env['planning.slot'].sudo().search([('partner_id', '=', partner.id), ('mrdv_event_id', '!=', 0), (
            'start_datetime', '<=', now.strftime(DEFAULT_SERVER_DATETIME_FORMAT))], order="start_datetime desc", limit=1)
        fav_clinic = partner.clinic_shortlisted_ids or False
        order_ids = request.env['sale.order'].sudo().search(
            [('partner_id', '=', partner.id)], order="date_order desc", limit=2, )

        product_wishlist_ids = request.env['product.wishlist'].sudo().search(
            [('partner_id', '=', partner.id)])
        values.update({'next_appointment_id': next_appointment_id,
                       'pervious_appointment_id': pervious_appointment_id,
                       'fav_clinic': fav_clinic,
                       'order_ids': order_ids,
                       'partner': partner,
                       'product_wishlist_ids': product_wishlist_ids})
        return request.env['ir.ui.view'].render_template("website_argos.portal_template", values)

    @http.route(['/my/clinic-shortlisted'], type='http', auth="user", website=True)
    def portal_clinic_shortlisted(self):
        partner = request.env.user.partner_id
        values = {
            'clinic_shortlisted_ids': partner.clinic_shortlisted_ids.sudo(),
        }
        return request.render("website_argos.wishlist_product_template", values)

    @http.route(['/wishlist-product'], type='http', auth="user", website=True)
    def portal_wishlist_product(self):
        partner = request.env.user.partner_id
        product_wishlist_ids = request.env['product.wishlist'].sudo().search(
            [('partner_id', '=', partner.id)])
        values = {
            'product_wishlist_ids': product_wishlist_ids,
        }
        return request.render("website_argos.wishlist_product_template", values)

    @http.route(['/update/preference/contact'], type='json', auth="user", website=True)
    def update_preference_contact(self, **kw):
        partner = request.env.user.partner_id
        if kw:
            vals = {'send_sms': kw.get('send_sms'),
                    'send_email': kw.get('send_email'),
                    'send_letter': kw.get('send_letter'),
                    'to_call': kw.get('to_call'),
                    }
            partner.sudo().write(vals)

        return werkzeug.utils.redirect('/my-content')
