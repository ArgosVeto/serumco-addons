# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Developed by Bizople Solutions Pvt. Ltd.

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
from odoo import fields, http, _
from odoo.addons.portal.controllers.portal import CustomerPortal,pager as portal_pager
from odoo.addons.website_sale.controllers.main import WebsiteSale
import urllib
from odoo.addons.portal.controllers.web import Home
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.auth_signup.controllers.main import AuthSignupHome
import json
from datetime import datetime
from odoo.http import route
from odoo.exceptions import UserError


class AuthSignupHomeSS(AuthSignupHome):
	def check_password(self,passwd):
		special_sym =['!','@','#','$','%','^','&','*'] 
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
		if 'confirm_second' not in vals_qcontext.keys():
			raise UserError(_("Veuillez confirmer J’accepte de recevoir la newsletter lorem ipsum dolor sit amet"))
		if 'confirm_first' not in vals_qcontext.keys():
			raise UserError(_("Veuillez confirmer J'ai lu et j'accepte les CGU et la politique de confidentialité"))
		values = { key: qcontext.get(key) for key in ('login', 'name', 'password') }
		chk_password = True
		if not values:
			raise UserError(_("The form was not properly filled in."))
		passwd = values.get('password')
		if values.get('password'):
			passwd = values.get('password')
			chk_password = self.check_password(passwd)
		if not chk_password:
			raise UserError(_("Your password must have at least 10 characters minimum, 1 uppercase, 1 lowercase, 1 special character, 1 figure "))
		if values.get('password') != qcontext.get('confirm_password'):
			raise UserError(_("Passwords do not match; please retype them."))
		supported_lang_codes = [code for code, _ in request.env['res.lang'].get_installed()]
		lang = request.context.get('lang', '').split('_')[0]
		if lang in supported_lang_codes:
			values['lang'] = lang
		self._signup_with_values(qcontext.get('token'), values)
		request.env.cr.commit()

class CustomerPortal(CustomerPortal):
	@route(['/my/account'], type='http', auth='user', website=True)
	def account(self, redirect=None, **post):
		values = self._prepare_portal_layout_values()
		partner = request.env.user.partner_id
		values.update({
			'error': {},
			'error_message': [],
		})

		if post and request.httprequest.method == 'POST':
			error, error_message = self.details_form_validate(post)
			values.update({'error': error, 'error_message': error_message})
			values.update(post)
			if not error:
				values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
				values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
				values.update({'country_id': int(values.pop('country_id', 0))})
				values.update({'zip': values.pop('zipcode', '')})
				if values.get('state_id') == '':
					values.update({'state_id': False})
				partner.sudo().write(values)
				if redirect:
					return request.redirect(redirect)
				return request.redirect('/my/home')
		countries = request.env['res.country'].sudo().search([('code','=','FR')])
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
				current_user = request.env['res.users'].sudo().browse(request.session.uid)
				current_user.partner_id.last_name = last_name
		return super(AuthSignupHome,self).web_login(*args, **kw)

class PortalContent(http.Controller):
	@http.route(['''/add-product-cart'''],type='http', auth="user", website=True)
	def add_product_cart(self,**post):
		if 'product_id' in post and post['product_id']:
			sale_order = request.website.sale_get_order(force_create=True)
			sale_order._cart_update(
	            product_id=int(post['product_id']),
	            add_qty=1,
	        )
		return request.redirect('/my-content')


	@http.route(['''/my-appointment'''],type='http', auth="user", website=True)
	def my_appointment(self,**post):
		old_appointment_ids = False
		new_appointment_ids = False
		employee_id = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
		if employee_id:
			now = datetime.now()
			old_app_dommain = [('employee_id','=',employee_id.id),('mrdv_event_id','!=',0),('start_datetime','<=',now)]
			new_app_dommain = [('employee_id','=',employee_id.id),('mrdv_event_id','!=',0),('start_datetime','>=',now)]
			old_appointment_ids = request.env['planning.slot'].sudo().search(old_app_dommain)
			new_appointment_ids = request.env['planning.slot'].sudo().search(new_app_dommain)
		values  = {'new_appointment_ids':new_appointment_ids,'old_appointment_ids':old_appointment_ids}
		return request.env['ir.ui.view'].render_template("website_argos.my_appointment",values)
		
	@http.route(['''/my-content'''],type='http', auth="user", website=True)
	def portal_content(self,**post):
		values = {}
		# erwq
		next_appointment_id = False
		pervious_appointment_id = False

		employee_id = request.env['hr.employee'].sudo().search([('user_id','=',request.env.user.id)])
		if employee_id:
			now = datetime.now()
			next_dommain = [('employee_id','=',employee_id.id),('mrdv_event_id','!=',0),('start_datetime','>=',now)]
			next_appointment_id = request.env['planning.slot'].sudo().search(next_dommain,limit=1)
			pervious_dommain = [('employee_id','=',employee_id.id),('mrdv_event_id','!=',0),('start_datetime','<=',now)]
			pervious_appointment_id = request.env['planning.slot'].sudo().search(pervious_dommain,limit=1)

		partner = request.env.user.partner_id
		fav_clinic = False
		fav_clinic = partner.clinic_shortlisted_ids
		order_ids = request.env['sale.order'].sudo().search([('partner_id','=',partner.id)],limit=2)
	
		product_wishlist_ids = request.env['product.wishlist'].sudo().search([('partner_id','=',partner.id)])
		values.update({'next_appointment_id':next_appointment_id,
					'pervious_appointment_id':pervious_appointment_id,
					'fav_clinic':fav_clinic,
					'order_ids':order_ids,
					'product_wishlist_ids':product_wishlist_ids})
		return request.env['ir.ui.view'].render_template("website_argos.portal_template",values)


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
		product_wishlist_ids = request.env['product.wishlist'].sudo().search([('partner_id','=',partner.id)])
		values = {
			'product_wishlist_ids': product_wishlist_ids,
		}
		return request.render("website_argos.wishlist_product_template", values)