odoo.define('keyyo.phone', function (require) {
    "use strict";

    var BasicFields = require('web.basic_fields');
    var Phone = BasicFields.FieldPhone;
    var core = require('web.core');
    var _t = core._t;

    Phone.include({
        events: Object.assign({}, Phone.prototype.events, {
            'click': '_onClick',
        }),
        _onClick: function (event) {
            if (this.mode === 'readonly'){
                var self = this;
                var number = false;
                if (self.name == 'phone'){
                    number = self.record.data.phone;
                }else if (self.name == 'mobile'){
                    number = self.record.data.mobile;
                }
                event.preventDefault();
                self._rpc({
                    route: '/web/keyyo/makecall',
                    params: {
                        source: self.name,
                        callee: number,
                        callee_name: self.record.data.name
                    }
                }).then(function (result) {
                    self.do_notify(_t('Answer'), result.status + '\n' + result.msg);
                });
            }
        }
    });
});