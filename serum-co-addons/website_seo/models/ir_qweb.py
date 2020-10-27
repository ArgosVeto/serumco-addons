# -*- coding: utf-8 -*-
import re
from odoo import api
from odoo.addons.web_editor.models.ir_qweb import Image

class Image(Image):

	@api.model
	def record_to_html(self, record, field_name, options):
		result = super(Image, self).record_to_html(record, field_name, options)
		if field_name == 'image' and options.get('widget')=='image':
			try:
				if field_name == 'image' and options.get('widget')=='image':
					alt_text = record.name
					result = re.sub('src'," alt = \'"+alt_text+"\' src ",result)
					return result
			except AttributeError:
				pass
		return result
