from odoo import models, api, fields, _, http
from odoo.http import request
from odoo.addons.website_argos.controllers.clinic_main import ClinicDetail
from odoo.addons.website_argos.controllers.main import bizcommonSliderSettings
from datetime import datetime,date
from odoo.osv import expression
import httpagentparser
from device_detector import DeviceDetector
import pytz


class bizcommonSliderSettings(bizcommonSliderSettings):

    @http.route(['/website_argos/multi_tab_product_call'], type='json', auth='public', website=True)
    def product_multi_product_image_dynamic_slider(self, **post):
        slider_data = request.env['multi.tab.product.slider'].sudo().search(
            [('id', '=', int(post.get('slider_filter')))])
        slider_data.identify_device()
        values = {
            's_id': slider_data.no_of_tabs + '-' + str(slider_data.id),
            'counts': slider_data.no_of_tabs,
            'auto_slide': slider_data.auto_slide,
            'auto_play_time': slider_data.sliding_speed,
            'mobile': slider_data.is_mobile,
        }
        return values

class ClinicDetail(ClinicDetail):

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

		domain_ids = request.env["operating.domain"].sudo().search([])
		if domain_ids:
			domain_ids.update({'operating_ids':operating_unit_ids.ids})
		else:
			domain_ids.create({'operating_ids':operating_unit_ids.ids})

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

	@http.route(['/clinic-detail/clinic-pratice/<model("operating.unit"):operating_unit>'], type='http', auth="public", website=True)
	def add_clinic_pratice(self,operating_unit,**post):	
		service_ids = request.env['operating.unit.service'].sudo().search([])
		payment_method_ids = request.env['payment.acquirer'].sudo().search([])
		practical_service_ids = request.env['practical.service'].sudo().search([])
		operating_unit_id = request.env['operating.unit'].sudo().browse(int(operating_unit))
		operating_detail_domain_id = request.env['operating.domain'].sudo().search([])
		if operating_detail_domain_id:
			operating_detail_domain_id.sudo().update({'operating_id':operating_unit_id.id})
		else:
			operating_detail_domain_id.sudo().create({'operating_id':operating_unit_id.id})
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


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    @api.model
    def clinic_detail_json(self):
        domain_ids = self.env["operating.domain"].sudo().search([],limit=1)
        operating_unit_ids = self.sudo().search([('id', 'in', domain_ids.operating_ids.ids)])
        unit_dic = {}
        for unit in operating_unit_ids:
            lis = []
            if unit.street:
                lis.append(unit.street)
            if unit.city:
                lis.append(unit.city)
            if unit.zip:
                lis.append(unit.zip)
            unit_dic.setdefault(unit.id, {})
            unit_dic[unit.id]['name'] = unit.name
            unit_dic[unit.id]['city'] = ','.join(rec for rec in lis)
        return unit_dic

    @api.model
    def clinic_detail(self):
    	detail_domain_ids = self.env['operating.domain'].sudo().search([])
    	operating_unit_ids = self.sudo().search([('id', '=', detail_domain_ids.operating_id.id)])
    	unit_dic = {}
    	for unit in operating_unit_ids:
    		lis = []
    		if unit.street:
    			lis.append(unit.street)
    		if unit.city:
    			lis.append(unit.city)
    		if unit.zip:
    			lis.append(unit.zip)
    		unit_dic.setdefault(unit.id, {})
    		unit_dic[unit.id]['name'] = unit.name
    		unit_dic[unit.id]['city'] = ','.join(rec for rec in lis)
    	return unit_dic


class OperatingDomain(models.Model):
    _name = "operating.domain"

    operating_ids = fields.Many2many("operating.unit", string="Domain Ids")
    operating_id = fields.Many2one("operating.unit", string="Domain Id")


class HrJob(models.Model):
    _inherit = 'hr.job'

    @api.model
    def job_detail_json(self):
        job_ids = self.sudo().search([])
        unit_dic = {}
        for unit in job_ids:
            lis = []
            if unit.address_id.street:
                lis.append(unit.address_id.street)
            if unit.address_id.street2:
                lis.append(unit.address_id.street2)
            if unit.address_id.city:
                lis.append(unit.address_id.city)
            if unit.address_id.zip:
                lis.append(unit.address_id.zip)
            unit_dic.setdefault(unit.id, {})
            unit_dic[unit.id]['name'] = unit.name
            unit_dic[unit.id]['city'] = ','.join(rec for rec in lis)
        return unit_dic


class MobileResponsive(models.Model):
	_inherit = "multi.tab.product.slider"

	is_mobile = fields.Boolean("Is Mobile")

	def identify_device(self):
		slider_ids = self.sudo().search([])
		dic = {}
		for rec in slider_ids:
			agent = request.httprequest.environ.get('HTTP_USER_AGENT')
			device = DeviceDetector(agent).parse()
			if device.device_type() == 'smartphone':
				rec.is_mobile = True
			else:
				rec.is_mobile = False
