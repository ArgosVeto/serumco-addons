# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    net_weight = fields.Float('Net Weight')
    gross_weight = fields.Float('Gross Weight')
    species_ids = fields.Many2many('res.partner.category', 'product_template_species_rel', 'product_template_id',
                                   'species_id', 'Species')
    race_ids = fields.Many2many('res.partner.parameter', 'product_template_race_rel', 'product_template_id', 'race_id',
                                'Race', domain=[('type', '=', 'race')])
    nature = fields.Selection([('chemical', 'Chemical'), ('homeo', 'Homeopathic'), ('immuno', 'Immunological')],
                              'Nature')
    approval = fields.Char('Approval')
    indication = fields.Text('Indications')
    usage_tips = fields.Text('Usage Tips')
    active_substance_id = fields.Many2one('active.substance', 'Active Substance')
    substance_quantity = fields.Float('Active Substance Quantity')
    substance_uom_id = fields.Many2one('uom.uom', 'Active Substance Unity')
    qsp_quantity = fields.Integer('Qsp Quantity')
    qsp_uom_id = fields.Many2one('uom.uom', 'Qsp Unity')
    issue_condition = fields.Char('Issue Condition')
    administration_route_ids = fields.Many2many('documents.tag', 'product_template_tag_rel', 'product_template_id',
                                            'document_tag_id', 'Administration Route')
