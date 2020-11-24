from odoo.http import request
from odoo import fields, http, _
from odoo.addons.website_sale.controllers.main import WebsiteSale
import json
from odoo.osv import expression
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
from datetime import datetime,date
import pytz
from odoo.addons.http_routing.models.ir_http import slug




class Appointment(http.Controller):
	@http.route([
			'''/appointment-two''',
		],type='http', auth="public", website=True)	
	def prendre_two(self, **post):
		clinic_id = False
		working_timing = {}
		clinic_working_slot = ''
		clinic_working_timing = {}
		consultation_type_ids = request.env['consultation.type'].sudo().search([])
		if 'clinic_id' in post and post['clinic_id']:
			clinic_id = request.env['operating.unit'].sudo().search([('id','=',int(post['clinic_id']))])
		if clinic_id and clinic_id.employee_ids:
			for emp in clinic_id.employee_ids:
				if emp.resource_calendar_id:
					date_today = date.today()
					working_slot = emp.resource_calendar_id.get_employee_slot(emp.resource_calendar_id)
					working_timing.update({emp.id:working_slot})
		
		if clinic_id and clinic_id.calendar_id:
			date_today = date.today()
			clinic_working_slot = clinic_id.calendar_id.get_employee_slot(clinic_id.calendar_id)
		values = {'mrdv_id':clinic_id.mrdv_id,
				'consultation_type_ids':consultation_type_ids,
				'clinic_id':clinic_id,
				'working_timing':working_timing,
				'clinic_working_slot':clinic_working_slot}
		return request.env['ir.ui.view'].render_template("website_argos.prendre_rendez_vous_two_tmp",values)


class MailingList(http.Controller):
	@http.route(['''/update-mailinglist'''], type='http', auth="public", website=True,methods=['POST'])
	def update_mailinglist(self, **kwargs):
		ContactSubscription = request.env['mailing.contact.subscription'].sudo()
		Contacts = request.env['mailing.contact'].sudo()
		name = request.env.user.partner_id.name
		mailing_list_id = False
		email = ''
		if 'news' in kwargs and kwargs['news']:
			mailing_list_id = request.env['mailing.list'].sudo().browse(int(kwargs['news']))
		if 'email' in kwargs and kwargs['email']:
			email = kwargs['email']
		if email and mailing_list_id:
			contact_id = Contacts.search([('email', '=', email)], limit=1)
			if not contact_id:
				contact_id = Contacts.create({'name': name, 'email': email})
			ContactSubscription.create({'contact_id': contact_id.id, 'list_id': int(mailing_list_id.id)})
		return request.redirect('/subscribe-thank-you')

class Application(http.Controller):	
	@http.route(['''/application/<model("hr.job", "[('website_id', 'in', (False, current_website_id))]"):job>'''],type='http', auth="public", website=True)	
	def application(self, job, **kwargs):
		cities = []
		jobs = []
		if job.job_type_id.id:
			jobs_post_domain = [('job_type_id', '=', job.job_type_id.id)]
			jobs = request.env['hr.job'].sudo().search(jobs_post_domain)
		agglomeration_ids = request.env['applicant.agglomeration'].sudo().search([])
		country_ids = request.env['res.country'].sudo().search([])
		job_type_ids = request.env['job.type'].sudo().search([])
		job_ids = request.env['hr.job'].sudo().search([])
		operating_unit_ids = request.env['operating.unit'].sudo().search([])
		for unit in operating_unit_ids:
			if unit.city  and unit.city  not in cities:
				cities.append(unit.city)
		values = {
			'country_ids':country_ids,
			'job': job,
			'jobs':jobs,
			'job_ids':job_ids,
			'agglomeration_ids':cities,
		}
		return request.env['ir.ui.view'].render_template("website_argos.application_template",values)

	
	@http.route(['''/application-confirm'''], type='http', auth="public", website=True,methods=['POST'])
	def application_confirm(self, **kwargs):
		applicant_vals = {}
		partner_name = ''
		name = '' 
		hr_applicant = request.env['hr.applicant']
		if 'first_name' in kwargs and kwargs['first_name']:
			partner_name += kwargs['first_name']
			name = kwargs['first_name'] +' Application'
		if 'last_name' in kwargs and kwargs['last_name']:
			partner_name += " " + kwargs['last_name']
		if 'email_from' in kwargs and kwargs['email_from']:
			applicant_vals.update({'email_from':kwargs['email_from']})
		if 'actual_post' in kwargs and kwargs['actual_post']:
			applicant_vals.update({'actual_post':kwargs['actual_post']})
		if 'code_postal' in kwargs and kwargs['code_postal']:
			applicant_vals.update({'code_postal':kwargs['code_postal']})
		if 'number_of_exp' in kwargs and kwargs['number_of_exp']:
			applicant_vals.update({'number_of_exp':kwargs['number_of_exp']})
		if 'address' in kwargs and kwargs['address']:
			applicant_vals.update({'address':kwargs['address']})
		if 'code_postal' in kwargs and kwargs['code_postal']:
			applicant_vals.update({'code_postal':kwargs['code_postal']})
		if 'city' in kwargs and kwargs['city']:
			applicant_vals.update({'city':kwargs['city']})
		if 'country_id' in kwargs and kwargs['country_id']:
			applicant_vals.update({'country_id':int(kwargs['country_id'])})
		if 'agglomeration_id' in kwargs and kwargs['agglomeration_id']:
			applicant_vals.update({'agglomeration_id':kwargs['agglomeration_id']})
		if 'job_id' in kwargs and kwargs['job_id']:
			applicant_vals.update({'job_id':int(kwargs['job_id'])})
		applicant_vals.update({'partner_name':partner_name,'name':name})
		app_id = hr_applicant.sudo().create(applicant_vals)
		if 'div_file1' in kwargs and kwargs['div_file1']:
			ir_attachment_id = request.env['ir.attachment'].sudo().browse(int(kwargs['div_file1']))
			if ir_attachment_id and app_id:
				ir_attachment_id.res_id = app_id.id
				ir_attachment_id.res_model = 'hr.applicant'				
		return request.redirect('/job-thank-you')

class WebsiteHrRecruitment(WebsiteHrRecruitment):
	def sitemap_jobs(env, rule, qs):
		if not qs or qs.lower() in '/jobs':
			yield {'loc': '/jobs'}

	@http.route([
		'/jobs',
		'/jobs/country/<model("res.country"):country>',
		'/jobs/department/<model("hr.department"):department>',
		'/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>',
		'/jobs/office/<int:office_id>',
		'/jobs/country/<model("res.country"):country>/office/<int:office_id>',
		'/jobs/department/<model("hr.department"):department>/office/<int:office_id>',
		'/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>/office/<int:office_id>',
	], type='http', auth="public", website=True, sitemap=sitemap_jobs)
	def jobs(self, country=None, department=None, office_id=None, **kwargs):
		env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
		subdomains = []
		domain = []
		Country = env['res.country']
		Jobs = env['hr.job']
		# domain = request.website.website_domain()
		if 'search_job_type' in kwargs and kwargs['search_job_type']:
			job_type_id = request.env['job.type'].sudo().search([('id','=',int(kwargs['search_job_type']))])
			subdomains.append([('job_type_id', '=', job_type_id.id)])
		if 'search' in kwargs and kwargs['search']:
			subdomains.append([('name','ilike',kwargs['search'])])
			subdomains.append([('address_id.street','ilike',kwargs['search'])])
			subdomains.append([('address_id.street2','ilike',kwargs['search'])])
			subdomains.append([('address_id.city','ilike',kwargs['search'])])
			subdomains.append([('address_id.zip','ilike',kwargs['search'])])
		if subdomains:
			domain.append(expression.OR(subdomains))
		domain = expression.AND(domain)
		job_ids = Jobs.search(domain, order="is_published desc, no_of_recruitment desc").ids
		# Browse jobs as superuser, because address is restricted
		jobs = Jobs.sudo().browse(job_ids)
		if not (country or department or office_id or kwargs.get('all_countries')):
			country_code = request.session['geoip'].get('country_code')
			if country_code:
				countries_ = Country.search([('code', '=', country_code)])
				country = countries_[0] if countries_ else None
				if not any(j for j in jobs if j.address_id and j.address_id.country_id == country):
					country = False
		if country and not kwargs.get('all_countries'):
			jobs = [j for j in jobs if j.address_id is None or j.address_id.country_id and j.address_id.country_id.id == country.id]
			offices = set(j.address_id for j in jobs if j.address_id is None or j.address_id.country_id and j.address_id.country_id.id == country.id)
		else:
			offices = set(j.address_id for j in jobs if j.address_id)

		departments = set(j.department_id for j in jobs if j.department_id)
		countries = set(o.country_id for o in offices if o.country_id)
		job_type_ids = request.env['job.type'].sudo().search([])
		if department:
			jobs = [j for j in jobs if j.department_id and j.department_id.id == department.id]
		if office_id and office_id in [x.id for x in offices]:
			jobs = [j for j in jobs if j.address_id and j.address_id.id == office_id]
		else:
			office_id = False
		return request.render("website_hr_recruitment.index", {
			'jobs': jobs,
			'countries': countries,
			'job_type_ids':job_type_ids,
			'departments': departments,
			'offices': offices,
			'country_id': country,
			'department_id': department,
			'office_id': office_id,
		})


	@http.route('''/jobs/apply/<model("hr.job", "[('website_id', 'in', (False, current_website_id))]"):job>''', type='http', auth="public", website=True)
	def jobs_apply(self, job, **kwargs):
		if not job.can_access_from_current_website():
			raise NotFound()
		error = {}
		default = {}
		if 'website_hr_recruitment_error' in request.session:
			error = request.session.pop('website_hr_recruitment_error')
			default = request.session.pop('website_hr_recruitment_default')
		agglomeration_ids = request.env['applicant.agglomeration'].sudo().search([])
		country_ids = request.env['res.country'].sudo().search([])
		job_type_ids = request.env['job.type'].sudo().search([])
		return request.render("website_hr_recruitment.apply", {
			'job': job,
			'error': error,
			'default': default,
			'country_ids':country_ids,
			'job_type_ids':job_type_ids,
			'agglomeration_ids':agglomeration_ids,
		})

class WebsiteForm(WebsiteForm):
	@http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
	def website_form(self, model_name, **kwargs):
		res = super(WebsiteForm, self).website_form(model_name, **kwargs)
		if model_name == 'hr.applicant' and request.session['form_builder_id']:
			applicant_vals = {}
			partner_name = ''
			hr_applicant_id = request.env['hr.applicant'].sudo().browse(request.session['form_builder_id'])
			if 'partner_name' in kwargs and kwargs['partner_name']:
				partner_name += kwargs['partner_name']
			if 'last_name' in kwargs and kwargs['last_name']:
				partner_name += " " + kwargs['last_name']
			if 'actual_post' in kwargs and kwargs['actual_post']:
				applicant_vals.update({'actual_post':kwargs['actual_post']})
			if 'code_postal' in kwargs and kwargs['code_postal']:
				applicant_vals.update({'code_postal':kwargs['code_postal']})
			if 'number_of_exp' in kwargs and kwargs['number_of_exp']:
				applicant_vals.update({'number_of_exp':kwargs['number_of_exp']})
			if 'address' in kwargs and kwargs['address']:
				applicant_vals.update({'address':kwargs['address']})
			if 'code_postal' in kwargs and kwargs['code_postal']:
				applicant_vals.update({'code_postal':kwargs['code_postal']})
			if 'city' in kwargs and kwargs['city']:
				applicant_vals.update({'city':kwargs['city']})
			if 'country_id' in kwargs and kwargs['country_id']:
				applicant_vals.update({'country_id':int(kwargs['country_id'])})
			if 'agglomeration_id' in kwargs and kwargs['agglomeration_id']:
				applicant_vals.update({'agglomeration_id':int(kwargs['agglomeration_id'])})
			if 'job_type_id' in kwargs and kwargs['job_type_id']:
				applicant_vals.update({'job_type_id':int(kwargs['job_type_id'])})
			applicant_vals.update({'partner_name':partner_name,'description':''})
			hr_applicant_id.update(applicant_vals)
		return res

class WebsiteSale(WebsiteSale):

	@http.route(['/shop/checkout'], type='http', auth="public", website=True)
	def checkout(self, **post):
		order = request.website.sale_get_order()

		redirection = self.checkout_redirection(order)
		if redirection:
			return redirection

		if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
			return request.redirect('/add-address?new-address=1')
		for f in self._get_mandatory_billing_fields():
			if not order.partner_id[f]:
				return request.redirect('/add-address?new-address=1')

		values = self.checkout_values(**post)

		if post.get('express'):
			return request.redirect('/shop/confirm_order')

		values.update({'website_sale_order': order})

		# Avoid useless rendering if called in ajax
		if post.get('xhr'):
			return 'ok'
		return request.render("website_sale.checkout", values)

	@http.route(['/shop/cart/update'], type='http', auth="public", methods=['GET', 'POST'], website=True, csrf=False)
	def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
		product_tmpl_id = False
		if 'product_tmpl_id' in kw and kw['product_tmpl_id']:
			product_tmpl_id = int(kw['product_tmpl_id'])
		if 'ptal' in kw and kw['ptal']:
			product_variant_ids = False
			if product_tmpl_id:
				cart_product_id = request.env['product.template'].sudo().browse(product_tmpl_id)
				if cart_product_id.product_variant_ids:
					product_variant_ids = cart_product_id.product_variant_ids.filtered(lambda s:  int(kw['ptal']) in s.product_template_attribute_value_ids.ids)
				if product_variant_ids:
					product_id = product_variant_ids[0]
					product_id = product_id.id
		sale_order = request.website.sale_get_order(force_create=True)
		if sale_order.state != 'draft':
			request.session['sale_order_id'] = None
			sale_order = request.website.sale_get_order(force_create=True)

		product_custom_attribute_values = None
		if kw.get('product_custom_attribute_values'):
			product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))

		no_variant_attribute_values = None
		if kw.get('no_variant_attribute_values'):
			no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))

		no_variant_attribute_values = None
		if kw.get('ptal'):
			no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))
		sale_order._cart_update(
			product_id=int(product_id),
			add_qty=add_qty,
			set_qty=set_qty,
			product_custom_attribute_values=product_custom_attribute_values,
			no_variant_attribute_values=no_variant_attribute_values,
		)
		if kw.get('express'):
			return request.redirect("/shop/checkout?express=1")
		return request.redirect("/shop/cart")

class ClinicDetail(http.Controller):

	
	@http.route(['''/service-detail/<model("operating.unit.service"):operating_service>'''],type='http', auth="public", website=True)	
	def service_detail(self,operating_service,**post):
		values = {'service':operating_service}
		return request.env['ir.ui.view'].render_template("website_argos.service_template",values)



	@http.route(['/update-delivery-address'], type='json', auth="public")
	def update_delivery_address(self,**post):
		partner = request.env.user.partner_id
		sale_order_id = request.session['sale_order_id']
		sale_order = request.env['sale.order'].sudo().browse(sale_order_id).exists() if sale_order_id else None
		fav_clinic = False
		if partner.clinic_shortlisted_ids:
			fav_clinic = partner.clinic_shortlisted_ids[0].favorite_clinic_id
		if sale_order and fav_clinic:
			sale_order.operating_unit_id = fav_clinic.id
			sale_order.fav_clinic = True
			sale_order.all_clinic = False
		values = {'website_sale_order':sale_order}
		return request.env['ir.ui.view'].render_template("website_argos.load_clinic_add_tmp",values)

	@http.route(['/update-delivery/<model("operating.unit"):operating_unit>'], type='http', auth="public", website=True)
	def update_delivery(self,operating_unit, **post):
		order = request.website.sale_get_order()
		order.operating_unit_id = operating_unit.id
		order.operating_unit_id = operating_unit.id
		order.all_clinic = True
		order.fav_clinic = False
		return request.redirect("/shop/checkout")

	@http.route(['/find-matched-clinic'], type='json', auth="public")
	def matched_clinic(self,**post):
		domain = []
		subdomains = []
		if 'cn' in post and post['cn']:
			subdomains.append([('name','ilike',post['cn'])])
			subdomains.append([('street','ilike',post['cn'])])
			subdomains.append([('street2','ilike',post['cn'])])
			subdomains.append([('zip','ilike',post['cn'])])
			subdomains.append([('city','ilike',post['cn'])])
			subdomains.append([('zip','ilike',post['cn'])])
		if subdomains:
			domain.append(expression.OR(subdomains))
		domain = expression.AND(domain)
		clinic_ids = request.env['operating.unit'].sudo().search(domain)
		values = {'clinic_ids': clinic_ids}
		return request.env['ir.ui.view'].render_template("website_argos.clinic_load",values)


	@http.route([
			'''/clinic-detail''',
		],type='http', auth="public", website=True)	
	def clinic_detail(self,**post):
		subdomains = []
		domain = [[('active', '=', True)]]
		clinic_collect_ids = request.env['operating.unit'].sudo().search([('click_and_collect','=',True)])
		clinic_appoint_ids = request.env['operating.unit'].sudo().search([('online_appointment_booking','=',True)])

		if 'clinic-collect' in post and post['clinic-collect']:
			clinic_type_ids = request.env['operating.unit'].sudo().search([('click_and_collect','=',True)])
			subdomains.append([('click_and_collect','=',True)])
			
		if 'clinic-appoint' in post and post['clinic-appoint']:
			clinic_type_ids = request.env['operating.unit'].sudo().search([('online_appointment_booking','=',True)])
			subdomains.append([('online_appointment_booking','=',True)])
		
		if 'clinic-parking' in post and post['clinic-parking']:
			clinic_type_ids = request.env['operating.unit'].sudo().search([('parking','=',True)])
			subdomains.append([('parking','=',True)])
		
		if 'clinic-mobility' in post and post['clinic-mobility']:
			clinic_type_ids = request.env['operating.unit'].sudo().search([('access_reduced_mobility','=',True)])
			subdomains.append([('access_reduced_mobility','=',True)])
		
		if 'service-type' in post and post['service-type']:
			service_ids = request.env['operating.unit.service'].sudo().search([('id','=',post['service-type'])])
			subdomains.append([('service_ids', 'in', service_ids.ids)])

		if 'search' in post and post['search']:
			subdomains.append([('name','ilike',post['search'])])
			subdomains.append([('street','ilike',post['search'])])
			subdomains.append([('street2','ilike',post['search'])])
			subdomains.append([('city','ilike',post['search'])])
			subdomains.append([('zip','ilike',post['search'])])
		if subdomains:
			domain.append(expression.OR(subdomains))

		domain = expression.AND(domain)
		if 'clear_search' in post and post['clear_search']:
			domain = []

		operating_unit_ids = request.env['operating.unit'].sudo().search(domain)
		if 'open_today' in post and post['open_today'] == str(1):
			unit_list = []
			date_today = date.today()
			date_today = date_today.weekday()
			for unit in operating_unit_ids:
				if unit.calendar_id and unit.calendar_id.attendance_ids:
					day_timimg = unit.calendar_id.attendance_ids.filtered(lambda x:x.dayofweek == str(date_today))
					if day_timimg:
						unit_list.append(unit.id)
			operating_unit_ids = operating_unit_ids.filtered(lambda x:x.id in unit_list)
		type_ids = request.env['operating.unit.type'].sudo().search([])
		service_ids = request.env['operating.unit.service'].sudo().search([])
		values = {'operating_unit_ids':operating_unit_ids,'service_ids':service_ids,'type_ids':type_ids, 'clinic_type_ids':clinic_collect_ids, 'clinic_appoint_ids':clinic_appoint_ids}
		return request.env['ir.ui.view'].render_template("website_argos.clinic_template",values)

	@http.route(['/add-fav-clinic-detail/<model("operating.unit"):operating_unit>'], type='http', auth="user", website=True)
	def add_fav_clinic_detail_favorite(self,operating_unit,**post):
		add_fav_clinic = request.env['website'].sudo().add_fav_clinic(operating_unit)
		values = {'clinic_id':operating_unit}
		return request.redirect("/clinic-detail/clinic-pratice/%s" % slug(operating_unit))

	@http.route(['/add-fav-clinic/<model("operating.unit"):operating_unit>'], type='http', auth="user", website=True)
	def add_fav_clinic_favorite(self,operating_unit,**post):
		add_fav_clinic = request.env['website'].sudo().add_fav_clinic(operating_unit)
		values = {'clinic_id':operating_unit}
		return request.redirect("/appointment-two?clinic_id=%s" % operating_unit.id)


	@http.route(['/add-clinic/<model("operating.unit"):operating_unit>'], type='http', auth="user", website=True)
	def add_clinic_favorite(self,operating_unit,**post):
		partner_id =  request.env.user.partner_id
		if partner_id.clinic_shortlisted_ids.ids:
			check_operating_uni = any(operating_unit.id == cs.favorite_clinic_id.id for cs in partner_id.clinic_shortlisted_ids)
			if not check_operating_uni:
				for cs in partner_id.clinic_shortlisted_ids:
					cs.unlink()
				partner_id.clinic_shortlisted_ids = [(0,0,{'favorite_clinic_id':operating_unit.id})]
			else:
				for cs in partner_id.clinic_shortlisted_ids:
					cs.unlink()
		else:
			partner_id.clinic_shortlisted_ids = [(0,0,{'favorite_clinic_id':operating_unit.id})]
		return request.redirect("/clinic-detail")

	@http.route(['/clinic-detail/clinic-pratice/<model("operating.unit"):operating_unit>'], type='http', auth="public", website=True)
	def add_clinic_pratice(self,operating_unit,**post):	
		service_ids = request.env['operating.unit.service'].sudo().search([])
		payment_method_ids = request.env['payment.acquirer'].sudo().search([])
		practical_service_ids = request.env['practical.service'].sudo().search([])
		operating_unit_id = request.env['operating.unit'].sudo().browse(int(operating_unit))
		working_timing = {}
		not_working_time = False
		week_slot = {'0':'Lun.','1':'Mar.','2':'Mer','3':'Jeu','4':'Ven.','5':'Sam.','6':'Dim.'}
		if operating_unit_id.calendar_id:
			resource_id = operating_unit_id.calendar_id
			attendance_ids = operating_unit_id.calendar_id.attendance_ids
			if attendance_ids:
				for day_week in range(0,6):
					now_time = datetime.now()
					date_today = date.today()
					date_today = date_today.weekday()
					if date_today == day_week:
						now_time =  pytz.timezone('UTC').localize(now_time).astimezone(pytz.timezone(request.env.user.tz  or 'UTC')).time()
						now_time = now_time.hour + now_time.minute/60.0 + now_time.second/3600
					start_time = 'fermé' 
					end_time = 'fermé'
					day_timimg = attendance_ids.filtered(lambda x:x.dayofweek == str(day_week))
					if day_timimg:
						if len(day_timimg) == 2:
							t1 = day_timimg[0].hour_from
							t2 = day_timimg[0].hour_to
							t3 = day_timimg[1].hour_from
							t4 = day_timimg[1].hour_to
							if (date_today == day_week):
								if (now_time >= t1) and (now_time <= t2):
									not_working_time = True
								if (now_time >= t3) and (now_time <= t4):
									not_working_time = True
							start_time = resource_id.convert_to_time(t1 * 3600) +' - ' + resource_id.convert_to_time(t2 * 3600)
							end_time = resource_id.convert_to_time(t3 * 3600) +' - ' + resource_id.convert_to_time(t4 * 3600)

						elif len(day_timimg) == 1:
							t1 = day_timimg[0].hour_from
							t2 = day_timimg[0].hour_to
							if (date_today == day_week):
								if (now_time >= t1) and (now_time <= t2):
									not_working_time = True
							hour_from_1 = str(day_timimg[0].hour_from)
							hour_from_1 = hour_from_1.split('.')
							hour_to_1 = str(day_timimg[0].hour_to)
							hour_to_1 = hour_to_1.split('.')							
							start_time = resource_id.convert_to_time(t1 * 3600) +' - ' + resource_id.convert_to_time(t2 * 3600)
						elif len(day_timimg) > 2:
							day_timimg = day_timimg[0:2]
							t1 = day_timimg[0].hour_from
							t2 = day_timimg[0].hour_to
							t3 = day_timimg[1].hour_from
							t4 = day_timimg[1].hour_to
							if (date_today == day_week):							
								if ((now_time >= t1) and (now_time <= t2)) or ((now_time >= t3) and (now_time <= t4)):
									not_working_time = True
							start_time = resource_id.convert_to_time(t1 * 3600) +' - ' + resource_id.convert_to_time(t2 * 3600)
							end_time = resource_id.convert_to_time(t3 * 3600) +' - ' + resource_id.convert_to_time(t4 * 3600)
						else:
							if (date_today == day_week):
								not_working_time = True
					time_range = {'start_time':start_time,'end_time':end_time}
					working_timing.update({week_slot[str(day_week)]:time_range})	
		values = {'service_ids':service_ids, 'payment_method_ids':payment_method_ids, 'operating_unit':operating_unit_id,'working_timing':working_timing,'not_working_time':not_working_time}
		return request.env['ir.ui.view'].render_template("website_argos.clinic_pratice",values)

class ClinicContact(http.Controller):	
	@http.route(['''/clinic-contact'''],type='http', auth="public", website=True)	
	def clinic_contact(self,**post):
		contact_questions_ids = request.env['contact.questions'].sudo().search([])
		partner_ids = False
		partner =  request.env.user.partner_id
		if partner.clinic_shortlisted_ids:
			partner_ids = partner.clinic_shortlisted_ids
		clinic_ids = request.env['operating.unit'].sudo().search([])
		# contact_ids = request.env['operating.unit'].sudo().search([('visible_in_contact','=',True)])
		values = {'clinic_ids':clinic_ids,'partner_ids':partner_ids,'contact_questions_ids':contact_questions_ids}
		return request.env['ir.ui.view'].render_template("website_argos.clinic_contact_us",values)
	
	@http.route(['''/clinic-contact/confirm'''],type='http', auth="public", website=True)	
	def clinic_contact_confirm(self,**post):
		crm_vals = {}
		if 'name' in post and post['name']:
			crm_vals.update({'name':post['name']})
		if 'name' in post and post['name']:
			crm_vals.update({'contact_name':post['name']})
		if 'email_from' in post and post['email_from']:
			crm_vals.update({'email_from':post['email_from']})
		if 'message' in post and post['message']:
			crm_vals.update({'description': post['message']})
		if 'contact_msg' in post and post['contact_msg']:
			crm_vals.update({'contact_questions_id': int(post['contact_msg'])})
		if 'clinic_contact_id' in post and post['clinic_contact_id']:
			crm_vals.update({'operating_unit_id': int(post['clinic_contact_id'])})
		lead_id = request.env['crm.lead'].sudo().create(crm_vals)
		return request.redirect("/contactus-thank-you")