# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    _order = 'is_top_ten desc, name'

    net_weight = fields.Float('Net Weight')
    gross_weight = fields.Float('Gross Weight')
    species_ids = fields.Many2many('res.partner.category', 'product_template_species_rel', 'product_template_id', 'species_id', 'Species')
    race_ids = fields.Many2many('res.partner.parameter', 'product_template_race_rel', 'product_template_id', 'race_id', 'Race',
                                domain=[('type', '=', 'race')])
    nature = fields.Selection([('chemical', 'Chemical'), ('homeo', 'Homeopathic'), ('immuno', 'Immunological')], 'Nature')
    approval = fields.Char('Approval')
    indication = fields.Text('Indications')
    active_substance_id = fields.Many2one('active.substance', 'Active Substance')
    substance_quantity = fields.Float('Active Substance Quantity')
    substance_uom_id = fields.Many2one('uom.uom', 'Active Substance Unity')
    qsp_quantity = fields.Integer('Qsp Quantity')
    qsp_uom_id = fields.Many2one('uom.uom', 'Qsp Unity')
    issue_condition = fields.Char('Issue Condition')
    administration_route_ids = fields.Many2many('documents.tag', 'product_template_tag_rel', 'product_template_id', 'document_tag_id',
                                                'Administration Route')
    amm = fields.Char('AMM Code')
    price_sensivity = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C')], 'Price Sensivity')
    is_top_ten = fields.Boolean('Is Top Ten')
    routing_value_ids = fields.Many2many('product.attribute.value', compute='_compute_routing_value_ids')
    additional_features = fields.Text('Additional Features')
    doc_type = fields.Char('Documentation Type')
    doc_url = fields.Char('Documentation URL')
    aliment_type = fields.Char('Aliment Type')
    utilization = fields.Char('Utilization')
    composition = fields.Char('Composition')
    analytic_constitution = fields.Char('Analytic Constitution')
    additives = fields.Char('Additives')
    energetic_value = fields.Char('Energetic Value')
    daily_ratio_recommended = fields.Char('Daily Ratio Recommended')
    indications = fields.Char('Indications')
    waters_content = fields.Char('Waters Content')
    description_web = fields.Html('Description Web')
    act_type = fields.Selection([('undefined', _('Undefined')), ('surgery', _('Surgery')),
                                 ('incineration', _('Incineration')), ('euthanasia', _('Euthanasia')),
                                 ('hospitalization', _('Hospitalization'))], string='Act Type', default='undefined')

    @api.depends('attribute_line_ids')
    def _compute_routing_value_ids(self):
        for rec in self:
            attributes = rec.attribute_line_ids.filtered(lambda line: line.attribute_id.routing)
            rec.routing_value_ids = attributes.mapped('value_ids')


