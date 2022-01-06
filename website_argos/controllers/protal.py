# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Developed by Bizople Solutions Pvt. Ltd.

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
import werkzeug
import logging
from odoo import fields, http, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, date_utils
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.website_sale.controllers.main import WebsiteSale
import urllib
from odoo.addons.portal.controllers.web import Home
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
from odoo.addons.auth_signup.models.res_users import SignupError
import json
import base64
from datetime import datetime
from odoo.http import route, content_disposition
from odoo.exceptions import UserError
try:
    import phonenumbers
except ImportError:
    _logger.debug('Cannot `import phonenumbers`.')

_logger = logging.getLogger(__name__)


class AuthSignupHomeSS(AuthSignupHome):
    def check_password(self, passwd):
        special_sym = ['?', '!', '@', '#', '$', '%', '^', '&', '(', ')', '~', '{', '}', '*']
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
        _logger.info("Web signup : signup in progress, adding numerous fields")
        values = {key: qcontext.get(key) for key in
                  ('login', 'name', 'password', 'firstname', 'lastname', 'phone', 'country_id', 'operating_unit_id',
                   'delivery_operating_unit_id', 'send_letter', 'send_email', 'send_sms', 'to_call')}
        if not values:
            raise UserError(_("The form was not properly filled in."))
        passwd = values.get('password', '')
        chk_password = self.check_password(passwd)
        if not chk_password:
            raise UserError(_(
                "Your password must have at least 10 characters minimum, 1 uppercase, 1 lowercase, 1 special character, 1 figure "))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '').split('_')[0]
        if lang in supported_lang_codes:
            values['lang'] = lang
        country_code = 'FR'
        if values.get('country_id', False):
            country_id = qcontext.get('country_id', False)
            country = ''.join(x for x in country_id if x.isdigit())
            update_country_id = request.env['res.country'].sudo().browse(int(country))
            country_code = update_country_id.code.upper()
            if update_country_id:
                values.update({'country_id': update_country_id.id})
        if values.get('operating_unit_id', False):
            operating_unit_id = qcontext.get('operating_unit_id', False)
            operating_unit = ''.join(x for x in operating_unit_id if x.isdigit())
            update_operating_id = request.env['operating.unit'].sudo().browse(int(operating_unit))
            if update_operating_id:
                values.update({'operating_unit_id': update_operating_id.id})
        if values.get('delivery_operating_unit_id', False):
            delivery_operating_unit_id = qcontext.get('delivery_operating_unit_id', False)
            delivery_operating_unit = ''.join(x for x in delivery_operating_unit_id if x.isdigit())
            update_delivery_operating_id = request.env['operating.unit'].sudo().browse(int(delivery_operating_unit))
            if update_delivery_operating_id:
                values.update({'delivery_operating_unit_id': update_delivery_operating_id.id})
        if values.get('phone', ''):
            phone = qcontext.get('phone')
            parse_phone = phonenumbers.parse(phone, country_code)
            phone = phonenumbers.format_number(parse_phone, phonenumbers.PhoneNumberFormat.E164)
            values.update({'phone': phone})
        if values.get('send_letter', False):
            values.update({'send_letter': qcontext.get('send_letter', False)})
        if values.get('send_email', False):
            values.update({'send_email': qcontext.get('send_email', False)})
        if values.get('send_sms', False):
            values.update({'send_sms': qcontext.get('send_sms', False)})
        if values.get('to_call', False):
            values.update({'to_call': qcontext.get('to_call', False)})
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()

    def do_signup_password(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = { key: qcontext.get(key) for key in ('login', 'name', 'password') }
        if not values:
            raise UserError(_("The form was not properly filled in."))
        if values.get('password') != qcontext.get('confirm_password'):
            raise UserError(_("Passwords do not match; please retype them."))
        supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
        lang = request.context.get('lang', '').split('_')[0]
        if lang in supported_lang_codes:
            values['lang'] = lang
        self._signup_with_values(qcontext.get('token'), values)
        request.env.cr.commit()

    @http.route('/web/signup', type='http', auth='public', website=True,
                sitemap=False)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        qcontext['states'] = request.env['res.country.state'].sudo().search([])
        qcontext['countries'] = request.env['res.country'].sudo().search([])

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                _logger.info("Web signup : new signup registered")
                # Send an account creation confirmation email
                if qcontext.get('token'):
                    user_sudo = request.env['res.users'].sudo().search(
                        [('login', '=', qcontext.get('login'))])
                    template = request.env.ref(
                        'auth_signup.mail_template_user_signup_account_created',
                        raise_if_not_found=False)
                    if user_sudo and template:
                        template.sudo().with_context(
                            lang=user_sudo.lang,
                            auth_login=werkzeug.url_encode({
                                'auth_login': user_sudo.email
                            }),
                        ).send_mail(user_sudo.id, force_send=True)
                return super(AuthSignupHome, self).web_login(*args, **kw)
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except (SignupError, AssertionError) as e:
                if request.env["res.users"].sudo().search(
                        [("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _(
                        "Another user is already registered using this email address.")
                else:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")

        response = request.render('auth_signup.signup', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_signup_password(qcontext)
                    return self.web_login(*args, **kw)
                else:
                    login = qcontext.get('login')
                    assert login, _("No login provided.")
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        login, request.env.user.login, request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(login)
                    qcontext['message'] = _("An email has been sent with credentials to reset your password")
            except UserError as e:
                qcontext['error'] = e.name or e.value
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                qcontext['error'] = str(e)

        response = request.render('auth_signup.reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    def _signup_with_values(self, token, values):
        lang_fr = request.env.ref('base.lang_fr', raise_if_not_found=False)
        if lang_fr:
            values['lang'] = lang_fr.code
        return super(AuthSignupHomeSS, self)._signup_with_values(token, values)


class CustomerPortal(CustomerPortal):

    MANDATORY_BILLING_FIELDS = ["firstname", "lastname", "phone",
                                "email", "street", "zipcode", "city", "country_id", "street2"]
    OPTIONAL_BILLING_FIELDS = ["state_id", "vat", "company_name"]

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        order = request.website.sale_get_order()
        if order:
            return request.redirect('shop/cart')
        return request.redirect('/my-content')

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
            if 'street2' in error.keys():
                error.pop('street2')
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

                if 'country_id' in post and post['country_id']:
                        country = ''.join(x for x in post['country_id'] if x.isdigit())
                        update_country_id = request.env['res.country'].sudo().browse(
                            int(country))
                        country_code = update_country_id.code.upper()

                if 'phone' in post and post['phone']:
                        res_parse = phonenumbers.parse(
                            post['phone'], country_code)
                        phone = phonenumbers.format_number(
                            res_parse, phonenumbers.PhoneNumberFormat.E164)
                        values.update({'phone': phone})
 
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my-content')

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
        file_datas = str(post['file_upload']).split(',')
        ir_attachment = request.env['ir.attachment'].sudo().create(
            {
                'name': post['file_name'],
                'datas': file_datas[1],
                'type': 'binary',
                'datas_fname':  post['file_upload'],
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


