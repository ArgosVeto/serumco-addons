odoo.define('many2one_item_limit.relational_fields', function (require) {
    "use strict";

    var RelationalFields = require('web.relational_fields');

    RelationalFields.FieldMany2One.include({
        init: function (parent, name, record, options) {
            var self = this;
            this._super.apply(this, arguments);
            this._rpc({
                model: 'ir.config_parameter',
                method: 'get_param',
                args: ['many2one.limit'],
            }).then(function (result) {
                self.limit = parseInt(result);
            });

        }
    })
});