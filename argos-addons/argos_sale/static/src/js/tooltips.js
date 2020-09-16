odoo.define('argos_sale.TooltipsWidget', function (require) {
    "use strict";

    var core = require('web.core');
    var QWeb = core.qweb;

    var Widget = require('web.Widget');
    var widget_registry = require('web.widget_registry');
    var config = require('web.config');

    var _t = core._t;

    var TooltipsWidget = Widget.extend({
        template: 'argos_sale.Tooltips',
        events: _.extend({}, Widget.prototype.events, {
            'click .fa-info-circle': '_onClickButton',
        }),

        init: function (parent, params) {
            this.data = params.data;
            this._super(parent);
        },

        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self._setPopOver();
            });
        },

        updateState: function (state) {
            this.$el.popover('dispose');
            var candidate = state.data[this.getParent().currentRow];
            if (candidate) {
                this.data = candidate.data;
                this.renderElement();
                this._setPopOver();
            }
        },

        _setPopOver: function () {
            var self = this;
            if (!this.data.product_id) {
                return;
            }
            this.data.debug = config.isDebug();
            this._rpc({
                model: 'sale.coupon.program',
                method: 'read',
                args: [this.data.coupon_program_ids.res_ids, ['name']],
            }).then(function (result) {
                self.data.program_list = result;
                var $content = $(QWeb.render('argos_sale.TooltipsPopOver', {
                    data: self.data,
                }));
                var options = {
                    content: $content,
                    html: true,
                    placement: 'left',
                    trigger: 'focus',
                    delay: {'show': 0, 'hide': 100},
                };
                self.$el.popover(options);
            });
        },

        _onClickButton: function () {
            this.$el.find('.fa-info-circle').prop('special_click', true);
        },

    });
    widget_registry.add('tooltips_widget', TooltipsWidget);
});