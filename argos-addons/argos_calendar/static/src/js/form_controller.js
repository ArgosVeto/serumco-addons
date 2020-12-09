odoo.define('argos_calendar.FormController', function (require) {
    "use strict";

    var FormController = require('web.FormController');
    FormController.include({
        _onButtonClicked: function (ev) {
            var self = this;
            if (self.modelName == 'planning.slot' && ev.data.attrs.name == 'button_validate_wizard') {
                ev.data.attrs.close = true;
            }
            return Promise.all([this._super.apply(this, arguments)]);
        }
    });
});
