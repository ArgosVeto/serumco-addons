# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_antibiotic = fields.Boolean(compute='_compute_is_antibiotic')
    is_critical_antibiotic = fields.Boolean(compute='_compute_is_antibiotic')
    tooltip_text = fields.Text(compute='_compute_tooltip_text')
    is_add_subline_allowed = fields.Boolean(compute='_compute_is_add_subline_allowed')
    has_promotion = fields.Boolean(compute='_compute_program_ids')
    coupon_program_ids = fields.Many2many('sale.coupon.program', compute='_compute_program_ids')
    consultation_date = fields.Date(related='order_id.consultation_date')
    invoice_creation_date = fields.Date(related='order_id.invoice_creation_date')
    comment = fields.Text('Comment')
    patient_id = fields.Many2one(related='order_id.patient_id')
    employee_id = fields.Many2one(related='order_id.employee_id')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments', compute='_compute_attachment_ids')

    def _compute_attachment_ids(self):
        for rec in self:
            rec.attachment_ids = self.env['ir.attachment'].search(
                [('res_id', '=', rec.id), ('res_model', '=', rec._name)])

    @api.depends('product_id')
    def _compute_is_add_subline_allowed(self):
        for rec in self:
            if rec.product_id.pack_ok and rec.product_id.pack_type == 'detailed':
                rec.is_add_subline_allowed = rec.product_id.is_add_subline_allowed
            else:
                rec.is_add_subline_allowed = False

    @api.depends('product_id', 'product_id.categ_id')
    def _compute_is_antibiotic(self):
        for rec in self:
            rec.is_antibiotic = rec.product_id.categ_id.is_antibiotic
            rec.is_critical_antibiotic = rec.product_id.categ_id.is_antibiotic and rec.product_id.categ_id.is_critical

    @api.depends('product_id', 'product_id.categ_id', 'is_critical_antibiotic')
    def _compute_tooltip_text(self):
        for rec in self:
            if rec.is_critical_antibiotic:
                rec.tooltip_text = rec.product_id.categ_id.tooltip_text
            else:
                rec.tooltip_text = ''

    @api.depends('product_id', 'order_id')
    def _compute_program_ids(self):
        for rec in self:
            rec.coupon_program_ids = self.env['sale.coupon.program']._filter_promotion_programs_from_product(
                rec.order_id, rec.product_id)
            rec.has_promotion = bool(rec.coupon_program_ids)

    @api.onchange('product_id')
    def product_id_change(self):
        super(SaleOrderLine, self).product_id_change()
        if self.product_id.pack_ok and self.pack_type == 'detailed' and self.pack_component_price == 'detailed':
            self.price_unit = 0.0

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        super(SaleOrderLine, self).product_uom_change()
        if self.product_id.pack_ok and self.pack_type == 'detailed' and self.pack_component_price == 'detailed':
            self.price_unit = 0.0

    @api.model
    def create(self, vals):
        if self._context.get('from_add_subline'):
            pack_parent_line_id = self.browse(vals.get('pack_parent_line_id'))
            new_values = self.get_subline_vals(vals, pack_parent_line_id)
            vals.update(new_values)
        return super(SaleOrderLine, self).create(vals)

    def save_add_line(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def get_subline_vals(self, values, line):
        quantity = values.get('product_uom_qty') * line.product_uom_qty
        order = line.order_id
        line_vals = {
            'product_id': values.get('product_id'),
            'order_id': order.id,
            'pack_depth': line.pack_depth + 1,
            'company_id': order.company_id.id,
            'pack_modifiable': line.product_id.pack_modifiable,
            'sequence': line.sequence
        }
        sol = line.new(line_vals)
        sol.product_id_change()
        sol.product_uom_qty = quantity
        sol.product_uom_change()
        sol._onchange_discount()
        vals = sol._convert_to_write(sol._cache)
        pack_price_types = {'totalized', 'ignored'}
        sale_discount = 0.0
        if line.product_id.pack_component_price == 'detailed':
            sale_discount = 100.0 - (
                    (100.0 - sol.discount) * (100.0 - values.get('discount', 0.0)) / 100.0
            )
        elif (
                line.product_id.pack_type == 'detailed'
                and line.product_id.pack_component_price in pack_price_types
        ):
            vals['price_unit'] = 0.0
        vals.update(
            {
                'discount': sale_discount,
                'name': '{}{}'.format('> ' * (line.pack_depth + 1), sol.name),
            }
        )
        return vals
