# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

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
