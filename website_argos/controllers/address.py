# -*- coding: utf-8 -*-
from odoo.http import request
from odoo import fields, http
import json

class Address(http.Controller):
	@http.route(['/add-address'], type='http', auth="public", website=True)
	def add_new_address(self,**post):
		sale_order_id = request.session['sale_order_id']
		sale_order = request.env['sale.order'].sudo().browse(sale_order_id).exists() if sale_order_id else None
		required_fields = []
		predefine_data = {}
		user_id = request.env.user
		company_id = user_id.company_id
		values = {}
		partner_id = False
		error_message = ""
		print ("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
		if 'data' in post and post['data']:
			predefine_data = json.loads(post['data'].replace("'", '"'))
		if 'error' in post and post['error']:
			required_fields = post['error'].strip().split(',')
			error_message = "Update required fields!"		
		countries = request.env['res.country'].sudo().search([])
		state_ids = request.env['res.country.state'].sudo().search([])
		if 'edit-mode' in  post and post['edit-mode']:
			partner_id = request.env['res.partner'].sudo().browse(int(post['edit-mode']))
			values.update({
				'mode':'edit-mode',		
			})
		elif 'new-address' in post and post['new-address']:
			values.update({
				'mode':'new-address',		
			})
		if 'submitted' in post and post['submitted']:
			required_fields = ['firstname', 'lastnane','zip','city','street','country_id','email']
			values = {}
			update_partner_id = False
			rfields = []
			if 'partner_id' in post and post['partner_id']:
				partner = ''.join(x for x in post['partner_id'] if x.isdigit())
				update_partner_id = request.env['res.partner'].sudo().browse(int(partner))
				
			error_message = ''
			for require_field in required_fields:
				if require_field in post and not post[require_field]:
					rfields.append(require_field)
			if rfields:
				error_message = ','.join(rfields)
			if  error_message:		
				return request.redirect("/add-address?data=%s&error=%s" % (post, error_message))
			partner_id = request.env.user.partner_id
			partner_vals = {}
			if 'firstname' in post and post['firstname']:
				partner_vals.update({'firstname':post['firstname']})
			if 'lastname' in post and post['lastname']:
				partner_vals.update({'lastname':post['lastname']})
			if 'email' in post and post['email']:
				partner_vals.update({'email':post['email']})
			if 'phone' in post and post['phone']:
				partner_vals.update({'phone':post['phone']})
			if 'street' in post and post['street']:
				partner_vals.update({'street':post['street']})
			if 'street2' in post and post['street2']:
				partner_vals.update({'street2':post['street2']})
			if 'zip' in post and post['zip']:
				partner_vals.update({'zip':post['zip']})
			if 'city' in post and post['city']:
				partner_vals.update({'city':post['city']})

			if 'state_id' in post and post['state_id']:
				state_id = request.env['res.country.state'].sudo().search([('name','=',post['state_id'])])
				partner_vals.update({'state_id': state_id.id})
			if 'country_id' in post and post['country_id']:
				partner_vals.update({'country_id':int(post['country_id'])})
			if 'mode' in  post and post['mode']:
				if post['mode'] == 'edit-mode' and update_partner_id:
					delivery_partner_id = update_partner_id.sudo().write(partner_vals)
				elif post['mode'] == 'new-address':
					delivery_partner_id = request.env['res.partner'].sudo().create(partner_vals)
					sale_order.partner_invoice_id = delivery_partner_id.id
					sale_order.partner_id = delivery_partner_id.id
					sale_order.onchange_partner_id()
					sale_order.team_id = request.website.salesteam_id and request.website.salesteam_id.id
					sale_order.user_id = request.website.salesperson_id and request.website.salesperson_id.id
					sale_order.website_id = request.website.id
			return request.redirect('/shop/checkout')
		else:
			values.update({
				'partner_id':partner_id,
				'required_fields':required_fields,
				'error_message':error_message,
				'countries':countries,
				'predefine_data':predefine_data,
				'state_ids':state_ids,			
			})
		print ("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
		values.update({'partner_id':partner_id})
		return request.render('website_argos.add_address',values)