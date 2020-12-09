odoo.define('argos_pos.models', function (require) {
    "use strict";
    var exports = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var QWeb = core.qweb;

    var _super_order = exports.Order.prototype;
    var _super_orderline = exports.Orderline.prototype;
	var _t = core._t;

    exports.Order = exports.Order.extend({
        initialize: function (attributes, options) {
            _super_order.initialize.apply(this, arguments);
        },
        add_product: function (product, options) {
            if (this._printed) {
                this.destroy();
                return this.pos.get_order().add_product(product, options);
            }
            this.assert_editable();
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            var line = new exports.Orderline({}, {pos: this.pos, order: this, product: product});
            this.fix_tax_included_price(line);

            if (options.extras !== undefined) {
                for (var prop in options.extras) {
                    line[prop] = options.extras[prop];
                }
            }

            if (options.quantity !== undefined) {
                line.set_quantity(options.quantity);
            }

            if (options.quantity_delivered !== undefined) {
                line.set_quantity_delivered(options.quantity_delivered);
            }

            if (options.quantity_invoiced !== undefined) {
                line.set_quantity_invoiced(options.quantity_invoiced);
            }

            if (options.price !== undefined) {
                line.set_unit_price(options.price);
                this.fix_tax_included_price(line);
            }

            if (options.lst_price !== undefined) {
                line.set_lst_price(options.lst_price);
            }

            if (options.discount !== undefined) {
                line.set_discount(options.discount);
            }

            var to_merge_orderline;
            for (var i = 0; i < this.orderlines.length; i++) {
                if (this.orderlines.at(i).can_be_merged_with(line) && options.merge !== false) {
                    to_merge_orderline = this.orderlines.at(i);
                }
            }
            if (to_merge_orderline) {
                to_merge_orderline.merge(line);
                this.select_orderline(to_merge_orderline);
            } else {
                this.orderlines.add(line);
                this.select_orderline(this.get_last_orderline());
            }

            if (line.has_product_lot) {
                this.display_lot_popup();
            }
            if (this.pos.config.iface_customer_facing_display) {
                this.pos.send_current_order_to_customer_facing_display();
            }
        },
    });

    exports.Orderline = exports.Orderline.extend({
        initialize: function (attr, options) {
            _super_orderline.initialize.apply(this, arguments);
            this.set_quantity_delivered(0);
            this.set_quantity_invoiced(0);
        },
        set_quantity_delivered: function (quantity_delivered) {
            // var decimals = this.pos.dp['Product Unit of Measure'];
            var quant = parseFloat(quantity_delivered) || 0;
            this.quantityDelivered = quant;
            this.quantityDeliveredStr = '' + quant;
        },
		set_quantity_invoiced: function (quantity_invoiced) {
            // var decimals = this.pos.dp['Product Unit of Measure'];
            var quant = parseFloat(quantity_invoiced) || 0;
            this.quantityInvoiced = quant;
            this.quantityInvoicedStr = '' + quant;
        },
        clone: function () {
            var orderline = _super_orderline.clone.apply(this, arguments);
            orderline.quantityDeliveredStr = this.quantityDeliveredStr;
            orderline.quantityInvoicedStr = this.quantityInvoicedStr;
            return orderline;
        },
        get_quantity_delivered_str: function () {
            return this.quantityDeliveredStr;
        },
		get_quantity_invoiced_str: function () {
            return this.quantityInvoicedStr;
        },
		get_quantity_invoiced: function () {
            return this.quantityInvoiced;
        },
        get_quantity_delivered: function () {
            return this.quantityDelivered;
        },
    });

   var SaleOrderListScreenWidget = screens.ScreenWidget.extend({
	    template: 'SaleOrderListScreenWidget',

	    auto_back: true,
	    renderElement: function() {
	        var self = this;
	        this._super();
	       	this.$('.back').click(function(){
	            self.gui.back();
	        });
	        var search_timeout = null;
	       	this.$('.searchbox input').on('keyup',function(event){
	            var query = this.value;
	            if(query==""){
	            	self.render_list(self.pos.quotations);
	            }
	            else{
	            	self.perform_search(query);
	            }
	        });
	        this.$('.client-list-contents').delegate('.wv_checkout_button','click',function(event){
            	var quotation = self.get_quotations_by_id($(this).data('id'));
            	var order = self.pos.get_order();
	            var orderlines = order.get_orderlines();
		        if(orderlines.length == 0){
			        rpc.query({
	                    model: 'sale.order',
	                    method: 'quotation_fetch_line',
	                    args: [quotation.id],
	                }).then(function(quotation_data){
			            order.set('client',undefined);
			            order.quotation_id = quotation.name;
			            order.quot_id = quotation.id;
			            if(quotation.partner_id){
			            	order.set_client(self.pos.db.get_partner_by_id(quotation.partner_id[0]));
			            }
			            for(var i=0;i<quotation_data.length;i++){
		            		var product = self.pos.db.get_product_by_id(quotation_data[i]['product_id'][0]);
		            		if(product && quotation_data[i]['product_uom_qty'] - quotation_data[i]['qty_invoiced'] > 0 ){
		            			order.add_product(product, {
                                    'quantity': quotation_data[i]['product_uom_qty'] - quotation_data[i]['qty_invoiced'],
                                    'quantity_delivered': quotation_data[i]['qty_delivered'],
									'quantity_invoiced': quotation_data[i]['qty_invoiced']
                                });
		            		}
		            	}
		            	self.gui.back();
			        },function(err,event){
			            event.preventDefault();
			            self.gui.show_popup('error',{
			                'title': _t('Error: Could not Save Changes'),
			                'body': _t('Your Internet connection is probably down.'),
			            });
			        });
		    }
		    else{
		    	self.gui.show_popup('error',{
		                'title': _t('Error: Could not Check-Out Order'),
		                'body': _t('Please remove all products from cart and try again.'),
			        });
		    }
		});
	    },
	    show: function(){
	        var self = this;
	        this._super();
	        this.renderElement();
	        this.render_list(self.pos.quotations);
	    },

	    perform_search: function(query){
	    	var quotations = this.pos.quotations;
	    	var results = [];
	        for(var i = 0; i < quotations.length; i++){
	        	var res = this.search_quotations(query, quotations[i]);
	        	if(res != false){
	        	results.push(res);
	        }
	        }
	        this.render_list(results);
	    },
	    search_quotations: function(query,quotations){
	        try {
	            query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
	            query = query.replace(' ','.+');
	            var re = RegExp("([0-9]+):.*?"+query,"gi");
	        }catch(e){
	            return [];
	        }
	        var results = [];
            var r = re.exec(this._quotations_search_string(quotations));
            if(r){
                var id = Number(r[1]);
                return this.get_quotations_by_id(id);
            }
	        return false;
	    },
	    get_quotations_by_id:function(id){
	    	var quotations = this.pos.quotations;
	    	for(var i=0;i<quotations.length;i++){
	    		if(quotations[i].id == id){
	    			return quotations[i];
	    		}
	    	}
	    },
	    _quotations_search_string: function(quotations){
		        var str =  quotations.name;
		        if(quotations.partner_id){
		            str += '|' + quotations.partner_id[1];
		        }
		        str = '' + quotations.id + ':' + str.replace(':','') + '\n';
		        return str;
		    },
	    render_list: function(quotationsVal){
	    	var self = this;
	        var contents = this.$el[0].querySelector('.client-list-contents');
	        contents.innerHTML = "";
	        var quotations = quotationsVal;
	        for(var i = 0;i<quotations.length; i++){
	            var quotation    = quotations[i];
                var clientline_html = QWeb.render('SaleOrderLine',{widget: self, quotation:quotation});
                var clientline = document.createElement('tbody');
                clientline.innerHTML = clientline_html;
                clientline = clientline.childNodes[1];
	            contents.appendChild(clientline);
	        }
	    },

	    close: function(){
	        this._super();
	    },
	});
	gui.define_screen({name:'sale-order-list', widget: SaleOrderListScreenWidget});
});
