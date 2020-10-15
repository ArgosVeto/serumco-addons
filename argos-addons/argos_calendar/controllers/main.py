# -*- coding: utf-8 -*-

import base64
import functools
from io import BytesIO

from odoo import http
from odoo.addons.web.controllers.main import Binary as _Binary
from odoo.http import request
from odoo.modules import get_resource_path

IMAGE_FORMATS = ['png', 'svg']


class Binary(_Binary):

    def _logo(self, img='logo', fmt=None, **kwargs):
        if fmt and fmt not in IMAGE_FORMATS:
            raise ValueError(fmt)

        placeholder = functools.partial(get_resource_path, 'argos_calendar', 'static', 'src', 'img')
        company = request.env['res.company'].sudo().search([], limit=1)
        for try_fmt in [fmt] if fmt else IMAGE_FORMATS:
            field = '%s_icon' % img
            values = company.read([field, 'write_date'])[0]
            if values[field]:
                image = BytesIO(base64.b64decode(values[field]))
                return http.send_file(image, filename='%s.%s' % (img, try_fmt), mtime=values['write_date'])

        return http.send_file(placeholder('%s.%s' % (img, fmt or IMAGE_FORMATS[0])))

    @http.route(['/web/binary/invoice_icon'], type='http', auth='none', cors='*')
    def invoice_icon(self, **kwargs):
        return self._logo(img='invoice', **kwargs)

    @http.route(['/web/binary/hospital_icon'], type='http', auth='none', cors='*')
    def hospital_icon(self, **kwargs):
        return self._logo(img='hospital', **kwargs)

    @http.route(['/web/binary/medical_icon'], type='http', auth='none', cors='*')
    def medical_icon(self, **kwargs):
        return self._logo(img='medical', **kwargs)

    @http.route(['/web/binary/hour_icon'], type='http', auth='none', cors='*')
    def hour_icon(self, **kwargs):
        return self._logo(img='hour', **kwargs)
