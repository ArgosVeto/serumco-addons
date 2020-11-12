from odoo import models, api, fields, _, http
from odoo.http import request
from odoo.addons.website_argos.controllers.clinic_main import ClinicDetail
from odoo.addons.website_argos.controllers.main import bizcommonSliderSettings
from odoo.osv import expression
import httpagentparser
from device_detector import DeviceDetector


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

	# @http.route([
 #            '''/clinic-detail''',
 #        ],type='http', auth="public", website=True) 
	# def clinic_detail(self,**post):
	# 	res = super(ClinicDetail, self).clinic_detail(**post)
	# 	operating_unit_ids = request.env['operating.unit'].sudo().search(domain)
	# 	print("kkllllllkkkkkkkkkkklllllllll",res.context,post,operating_unit_ids)
	# 	# domain_ids = request.env["operating.domain"].sudo().search([])
	# 	# if domain_ids:
	# 	# 	domain_ids.update({'operating_ids':operating_unit_ids.ids})
	# 	# else:
	# 	# 	domain_ids.create({'operating_ids':operating_unit_ids.ids})
	# 	return res


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


class OperatingDomain(models.Model):
    _name = "operating.domain"

    operating_ids = fields.Many2many("operating.unit", string="Domain Ids")


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
