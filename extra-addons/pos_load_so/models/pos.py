# -*- coding: utf-8 -*-


from openerp import fields, models,tools,api, _
import logging
from functools import partial
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from openerp.exceptions import UserError
import pytz

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = "pos.order"

    sale_order_id = fields.Many2one("sale.order",string="Sale Order",readonly=True)

    @api.model
    def _order_fields(self, ui_order):
        result = super(PosOrder, self)._order_fields(ui_order)
        if 'quot_id' in ui_order:
            result['sale_order_id'] = ui_order['quot_id']
            quotation_obj = self.env['sale.order'].sudo().browse(ui_order['quot_id'])
            if quotation_obj:
                quotation_obj.pos_sold = True
        return result



class pos_config(models.Model):
    _inherit = 'pos.config' 
    
    sale_order_days = fields.Integer("Sale Order Days",default=1)
    allow_load_so = fields.Boolean("Load Sales Order")

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pos_sold = fields.Boolean(string="Pos Sold")

    @api.model
    def new_sent_order_json(self,from_days,config_id):
        order_json_format = []
        total_ids = []
        for order in self.sudo().search([('state','=','draft'),('pos_sold','=',False),('date_order','>',from_days)]):
            order_json_format.append(order.read(['id','name','date_order','amount_total','partner_id','order_line','state']))
        return {'data':order_json_format}

    @api.model
    def quotation_fetch_line(self, quotation_id):
        quotation_obj = self.sudo().browse(int(quotation_id))
        if quotation_obj:
            return quotation_obj.order_line.read(['product_id','price_unit','product_uom_qty','tax_id'])
        return False




    