# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2019-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################
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
