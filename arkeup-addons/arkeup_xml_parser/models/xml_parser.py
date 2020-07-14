# -*- coding: utf-8 -*-


import xml.etree.ElementTree as ET
import io
from io import BytesIO
import requests
import base64
import re

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class XmlParser(models.Model):
    _name = 'xml.parser'
    _description = 'Xml parser'

    name = fields.Char()
    file = fields.Binary('File', attachment=True, required=True)
    file_name = fields.Char('Filename')
    node = fields.Char(string="Reference node")
    model_id = fields.Many2one('ir.model', string="Model")
    fields_ids = fields.One2many('fields.mapping', 'parser_id')
    specific_domain = fields.Char(string="Domain", default="[('search_field', '=', 'field_name')]", required=True)

    @api.model
    def default_get(self, fields):
        res = super(XmlParser, self).default_get(fields)
        if not res.get('name') and 'name' not in res:
            res.update({'name': self.env['ir.sequence'].next_by_code('xml.parser.seq')})
        if not res.get('specific_domain') and 'specific_domain' not in res:
            res.update({'specific_domain': "[('search_field', '=', 'field_name')]"})
        return res

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals.update({'name': self.env['ir.sequence'].next_by_code('xml.parser.seq')})
        return super(XmlParser, self).create(vals)

    def _read_external_image(self, url):
        buffered = BytesIO(requests.get(url).content)
        img_base64 = base64.b64encode(buffered.getvalue())
        return img_base64.decode()

    def _prepare_image_medium(self, url):
        try:
            return self._read_external_image(url)
        except Exception as e:
            raise ValueError(_("Can't import image URL: %(url)s :  %(error)s") % {
                'url': url,
                'error': e
            })

    @api.onchange('model_id')
    def onchange_model_id(self):
        if self.model_id:
            for line in self.fields_ids:
                line.model_id = self.model_id.id

    def update_model_infos(self, vals):
        if not vals:
            return False

        base_domain = self.specific_domain.replace('[(', '').replace(')]', '')
        search_fields, operator, search_value = base_domain.split(', ')
        domain = [(search_fields.strip("'"), operator.strip("'"), vals.get(search_value.strip("'")))]
        record = self.env[str(self.model_id.model)].search(domain, limit=1)

        if not record:
            return False

        image_1920 = vals.get('image_1920', False)
        if image_1920 and isinstance(image_1920, str) and re.match(r"(?:http|https)://", image_1920):
            vals['image_1920'] = self._prepare_image_medium(image_1920)

        record.write(vals)
        return True

    def parse_xml(self):
        if not self.file:
            return False

        try:
            datastring = base64.decodebytes(self.file).decode('utf-8')
            xml_file = io.StringIO(datastring)
            tree = ET.parse(xml_file)

            root = tree.getroot()
            for element in root:
                if element.tag == self.node:
                    for line in self.fields_ids:
                        vals = {}
                        for subelement in element:
                            if subelement.tag == line.name:
                                vals.update({str(line.destination.name): subelement.text})

                        self.update_model_infos(vals)
        except Exception as error:
            raise ValidationError("Error when parsing xml data: %s" % error)

    def button_parse_xml(self):
        return self.parse_xml()
