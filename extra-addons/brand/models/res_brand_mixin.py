# # Copyright (C) 2020 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from lxml import etree
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResBrandMixin(models.AbstractModel):
    _name = 'res.brand.mixin'
    _description = 'Brand Mixin'

    brand_id = fields.Many2one('res.brand', 'Brand', help="Brand to use for this sale")
    brand_use_level = fields.Selection([('no', 'Do not use brands on business document'), ('optional', 'Optional'),
                                        ('required', 'Required')], 'Brand Use Level', default='no', related='company_id.brand_use_level')
    company_id = fields.Many2one('res.company', 'Company')

    def check_brand_required(self):
        self.ensure_one()
        return self.company_id.brand_use_level == 'required'

    @api.constrains('brand_id', 'company_id')
    def _check_brand_requirement(self):
        for rec in self:
            if rec.check_brand_required() and not rec.brand_id:
                raise ValidationError(_("Brand is required"))

    @api.constrains('brand_id', 'company_id')
    def _check_brand_company_id(self):
        for rec in self:
            if rec.brand_id.company_id and rec.brand_id.company_id != rec.company_id:
                raise ValidationError(_("Brand company must match document company for %s") % rec.display_name)

    @api.onchange('brand_id')
    def _onchange_brand_id(self):
        for rec in self.filtered('brand_id.company_id'):
            if rec.brand_id.company_id:
                rec.company_id = rec.brand_id.company_id

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
            set visibility and requirement rules
        :param view_id:
        :param view_type:
        :param toolbar:
        :param submenu:
        :return:
        """
        result = super(ResBrandMixin, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type in ['tree', 'form']:
            doc = etree.XML(result['arch'])
            for node in doc.xpath("//field[@name='brand_id']"):
                elem = etree.Element('field', {'name': 'brand_use_level', 'modifiers': json.dumps({'invisible': 1})})
                node.addprevious(elem)
                modifiers = json.loads(node.get("modifiers"))
                modifiers['invisible'] = [('brand_use_level', '=', 'no')]
                modifiers['required'] = [('brand_use_level', '=', 'required')]
                node.set("modifiers", json.dumps(modifiers))
            result['arch'] = etree.tostring(doc, encoding='unicode')
        return result
