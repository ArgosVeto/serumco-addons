# -*- coding: utf-8 -*-
import re
from odoo import api, fields , models
from odoo.exceptions import Warning
from odoo.exceptions import except_orm, AccessError, MissingError, ValidationError
from odoo.tools.translate import _
from collections import Counter

# import logging
# _logger = logging.getLogger(__name__)

ProductMetaAttributes = [
	'name',
	'categ_id',
	'description',
	"description_sale",
	'ean13',
	'default_code',
	'company_id'
]
CategoryMetaAttributes = [
	'categ_name',
	'categ_parent_id',
	'category_description'
]

class product_template(models.Model):

	_inherit = 'product.template'
	seo_auto_update = fields.Boolean(string = 'Auto update', default = 1)

class product_public_category(models.Model):

	_name = 'product.public.category'
	_inherit = ['product.public.category',"website.seo.metadata"]

	seo_auto_update = fields.Boolean(string = 'Auto update', default = 1)
	category_description = fields.Text(string = "Description (About this category)")

class WebsiteSeoAttribute(models.Model):

	_name  = "website.seo.attribute"
	_order = 'sequence asc'

	name = fields.Char('Name',required=True)
	sequence = fields.Integer('Sequence',default=100)

	model_name = fields.Selection([
		# ('custom',"Custom Keyword"),
		('product','Product'),
		('category','Public Category')]
		,string='Models',required=True)
	code = fields.Char('Technical Name',required =True)


class WebsiteSeo(models.Model):
	_name="website.seo"

	@api.depends('website_seo_meta_title_ids')
	def _compute_seo_title(self):
		for record in self:
			record.website_meta_title = (" "+str(record.multi_attribute_seperator)+" ").join('{'+str(rec.name)+"}" for rec in record.website_seo_meta_title_ids)

	@api.depends('website_seo_meta_description_ids')
	def _compute_seo_description(self):
		for record in self:
			record.website_meta_description = (" "+str(record.multi_attribute_seperator)+" ").join('{'+str(rec.name)+"}" for rec in record.website_seo_meta_description_ids)

	@api.depends('website_seo_meta_keyword_ids')
	def _compute_seo_keyword(self):
		for record in self:
			record.website_meta_keyword = ', '.join('{'+str(rec.name)+"}" for rec in record.website_seo_meta_keyword_ids)


	def _get_seo_config_values(self):
		seo_config_values_list_tuples = self.env['website.seo.config.settings'].get_values()
		return seo_config_values_list_tuples

	name = fields.Char("Name" ,
			default = "Website SEO"
		)
	model_name = fields.Selection(
			[('product','Product'),('category','Public Category')],
			string='SEO Meta Configuration for',
			required=True,
			default = 'product'
		)

	website_seo_meta_title_ids = fields.Many2many("website.seo.attribute",  "website_seo_title_seo_attribute_relation", "wk_website_seo_title","wk_website_seo_attribute_title",  "Add Title")
	website_seo_meta_description_ids = fields.Many2many(comodel_name = "website.seo.attribute", relation = "website_seo_description_seo_attribute_relation", column1 = "wk_website_seo_description",column2 = "wk_website_seo_attribute_description", string="Add Description" )
	website_seo_meta_keyword_ids = fields.Many2many(comodel_name = "website.seo.attribute", relation = "website_seo_keyword_seo_attribute_relation", column1 = "wk_website_seo_keywords",column2 = "wk_website_seo_attribute_keyword", string="Add Keywords" )

	multi_value_seperator = fields.Char("Multi Value Separator")
	multi_attribute_seperator = fields.Char("Multi Attribute Separator",required=True, default="|")

	website_meta_title = fields.Char("Meta Title",compute = _compute_seo_title)
	website_meta_description = fields.Char("Meta Description",compute = _compute_seo_description)
	website_meta_keyword =  fields.Char("Meta Keywords", compute = _compute_seo_keyword)

	_sql_constraints = [('unique_name', 'unique(model_name)', 'A single SEO can be configured for a model!')]

	def _seo_genrated(self,message):
		message_id = self.env['wk.wizard.message'].create(dict(text=message))
		return {
				'name':"SEO information Updated !",
				'view_mode': 'form',
				'view_id': False,
				'view_type': 'form',
				'res_model': 'wk.wizard.message',
				'res_id': message_id.id,
				'type': 'ir.actions.act_window',
				'nodestroy': True,
				'target': 'new',
				'domain': '[]',
				}

	def _get_arrtribute_value(self, attribute, model_name_obj):

		if self.model_name == "product" and (not attribute in ProductMetaAttributes):
			raise ValidationError("Attribute with Technical name = {"+ attribute +"} is not valid for "+ self.model_name)
		if self.model_name == "category" and (not attribute in CategoryMetaAttributes):
			raise ValidationError("Attribute with Technical name = {"+ attribute +"} is not valid for "+ self.model_name)

		if attribute =='name':
			value = model_name_obj.name
		elif attribute =='categ_id':
			value= model_name_obj.categ_id.name
		elif attribute =='description_sale':
			value= model_name_obj.description_sale
		elif attribute =='ean13':
			value= model_name_obj.barcode
		elif attribute =='description':
			value= model_name_obj.description
		elif attribute == 'default_code':
			value= model_name_obj.default_code
		elif attribute == 'company_id':
			value= model_name_obj.company_id and model_name_obj.company_id.name or self.env.company.name
		elif attribute == 'categ_name':
			value= model_name_obj.name
		elif attribute == 'categ_parent_id':
			value = model_name_obj.parent_id.name
		elif attribute == 'category_description':
			value=model_name_obj.category_description
		else:
			value=""
		return value

	def _get_wrap_arrtribute_value(self, attribute, model_name_obj):
		value = self._get_arrtribute_value(attribute, model_name_obj)
		return value and (self.multi_value_seperator + ' ' if self.multi_value_seperator else ' ').join(x for x in value.split(" ") if x)

	def _get_wrap_keywords(self, attribute, model_name_obj):
		value = self._get_arrtribute_value(attribute, model_name_obj)
		seo_keywords = ['']
		if value:
			seo_config_values = self._get_seo_config_values()
			keyword_max_len = seo_config_values.get('wk_seo_website_meta_keywords_size',10)
			keyword_max_num = seo_config_values.get('wk_seo_website_meta_keywords_number',27)
			seo_keywords = [x for x in value.split(" ") if x and len(x)<=keyword_max_len]
		return seo_keywords

	def  _set_meta_info(self, model_name_obj, meta_title_attribute_ids, meta_description_attribute_ids, meta_keyword_attribute_ids):
		seo_config_values = self._get_seo_config_values()
		seo_title, title_max_len = '', seo_config_values.get('wk_seo_website_meta_title_size',70)
		seo_description, description_max_len  =  '', seo_config_values.get('wk_seo_website_meta_description_size',165)
		seo_keywords, keyword_max_len, keyword_max_num  =  [], seo_config_values.get('wk_seo_website_meta_keywords_size',10), seo_config_values.get('wk_seo_website_meta_keywords_number',27)
		for attribute in meta_title_attribute_ids:
			if attribute.model_name=="custom":
				# seo_title += attribute.code + (self.multi_value_seperator + ' ' if self.multi_value_seperator else " ")
				seo_title += attribute.code + ' ' + self.multi_attribute_seperator + ' '
			else:
				value = self._get_wrap_arrtribute_value(attribute.code ,model_name_obj)
				if value:
					seo_title += value + ' ' + self.multi_attribute_seperator + ' '
					
		seo_title = seo_title[:-len(self.multi_attribute_seperator) -1].strip()
		model_name_obj.website_meta_title = seo_title if len(seo_title) < title_max_len else seo_title[:title_max_len]

		for attribute in meta_description_attribute_ids:
			if attribute.model_name=="custom":
				# seo_description += attribute.code + (self.multi_value_seperator + ' ' if self.multi_value_seperator else " ")
				seo_description += attribute.code + ' ' + self.multi_attribute_seperator + ' '
			else:
				value = self._get_wrap_arrtribute_value(attribute.code ,model_name_obj)
				if value:
					seo_description += value + ' ' + self.multi_attribute_seperator + ' '

		seo_description = seo_description[:-len(self.multi_attribute_seperator) -1].strip()
		model_name_obj.website_meta_description = seo_description if len(seo_description) < description_max_len else seo_description[:description_max_len]

		for attribute in meta_keyword_attribute_ids:
			if attribute.model_name=="custom":
				keywords = [str(attribute.code)]
			else:
				keywords = self._get_wrap_keywords(attribute.code ,model_name_obj)
			seo_keywords.extend(keywords)
		seo_keywords = Counter(seo_keywords).most_common(keyword_max_num)
		temp_seo_words = ", ".join(t[0] for t in seo_keywords)

		model_name_obj.website_meta_keywords = temp_seo_words
		return True

	def save_meta_info(self):
		titles = self.website_meta_title
		descriptions = self.website_meta_description
		keyword = self.website_meta_keyword
		if self.model_name == 'product':
			products = self.env['product.template'].search([('seo_auto_update','=',True),('website_published','=',True)])
			for product in products:
				self._set_meta_info( product,  self.website_seo_meta_title_ids, self.website_seo_meta_description_ids, self.website_seo_meta_keyword_ids)
			message=_("<h2>The SEO information for  products has been Updated successfully...!</h2><h4>Total %d products items is now influenced  by this SEO Updation.</h4><h4>NOTE: SEO information for those products will not update in which you  have unchecked \"Auto Update\". </h4> "%(len(products)))
			return self._seo_genrated(message)
		elif self.model_name == 'category':
			categories = self.env['product.public.category'].search([('seo_auto_update','=',True)])
			for category in categories:
				self._set_meta_info( category ,self.website_seo_meta_title_ids ,self.website_seo_meta_description_ids, self.website_seo_meta_keyword_ids)
			message=_("<h2>The SEO information for  Categories has been Updated successfully...!</h2><h4>Total %d categories  are influenced  by this SEO Updation.</h4><h4>NOTE: SEO information for those Categories will not update where you have unchecked   \"Auto Update\". </h4>"%(len(categories)))
			return self._seo_genrated(message)
