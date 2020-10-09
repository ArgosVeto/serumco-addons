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