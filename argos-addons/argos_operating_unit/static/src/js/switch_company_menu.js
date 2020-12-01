odoo.define('argos_operating_unit.SwitchCompanyMenu', function (require) {
    "use strict";

    var session = require('web.session');
    var SwitchCompanyMenu = require('web.SwitchCompanyMenu');

    SwitchCompanyMenu.include({
        template: 'SwitchOperatingUnitMenu',
        events: {
            'click .dropdown-item[data-menu] div.log_into': '_onSwitchCompanyClick',
            'click .dropdown-item[data-menu] div.toggle_company': '_onToggleCompanyClick',
            'click .dropdown-item[data-menu] div.switch_ou': '_onSwitchOperatingUnitClick',
        },

        init: function () {
            this._super.apply(this, arguments);
        },

        willStart: function () {
            var self = this;
            this.allowed_company_ids = String(session.user_context.allowed_company_ids)
                .split(',')
                .map(function (id) {
                    return parseInt(id);
                });
            this.current_company = this.allowed_company_ids[0];
            this.operating_unit_id = session.operating_unit_id;
            this.user_operating_unit_ids = session.user_operating_unit_ids;
            this.user_operating_units = session.user_operating_units;
            this.operating_unit_name = false;
            if (this.user_operating_units[this.current_company].length > 0) {
                var op_unit = _.find(this.user_operating_units[this.current_company], function (operating_unit) {
                    return operating_unit[0] === self.operating_unit_id;
                });
                if (op_unit && op_unit.length > 0) {
                    this.operating_unit_name = op_unit[1];
                }
            }
            var def;
            if (!_.contains(this.user_operating_unit_ids[this.allowed_company_ids[0]], this.operating_unit_id)) {
                if (this.user_operating_unit_ids[this.allowed_company_ids[0]].length > 0) {
                    def = this._rpc({
                        model: 'res.users',
                        method: 'write',
                        args: [session.uid, {'default_operating_unit_id': this.user_operating_unit_ids[this.allowed_company_ids[0]][0]}],
                        context: session.user_context,
                    }).then(function () {
                        self.operating_unit_id = self.user_operating_unit_ids[self.allowed_company_ids[0]][0];
                        if (self.user_operating_units[self.current_company].length > 0) {
                            var op_unit = _.find(self.user_operating_units[self.current_company], function (operating_unit) {
                                return operating_unit[0] === self.operating_unit_id;
                            });
                            if (op_unit && op_unit.length > 0) {
                                self.operating_unit_name = op_unit[1];
                            }
                        }
                    })
                } else {
                    this.operating_unit_id = false;
                }
            }
            return Promise.resolve(def).then(this._super.apply(self, arguments));
        },

        _onSwitchOperatingUnitClick: function (ev) {
            ev.stopPropagation();
            var dropdownItem = $(ev.currentTarget).parent();
            var dropdownMenu = dropdownItem.parent().parent();
            var dropdownCompanyItem = dropdownItem.parent().find('.dropdown-item[data-menu] div.log_into').parent();
            var dropdownCompanyMenu = dropdownCompanyItem.parent();
            var companyID = dropdownCompanyItem.data('company-id');
            var operationUnitID = dropdownItem.data('ou-id');
            var allowed_company_ids = this.allowed_company_ids;
            if (dropdownCompanyItem.find('.fa-square-o').length) {
                if (this.allowed_company_ids.length === 1) {
                    dropdownCompanyMenu.find('.fa-check-square').removeClass('fa-check-square').addClass('fa-square-o');
                    dropdownCompanyItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
                    allowed_company_ids = [companyID]
                } else {
                    allowed_company_ids.push(companyID);
                    dropdownCompanyItem.find('.fa-square-o').removeClass('fa-square-o').addClass('fa-check-square');
                }
            }
            dropdownMenu.find('.fa-check-circle').removeClass('fa-check-circle').addClass('fa-circle-o');
            dropdownItem.find('.fa-circle-o').removeClass('fa-circle-o').addClass('fa-check-circle');
            this._rpc({
                model: 'res.users',
                method: 'write',
                args: [session.uid, {'default_operating_unit_id': operationUnitID}],
                context: session.user_context,
            }).then(function () {
                session.setCompanies(companyID, allowed_company_ids);
            })
        },
    });
});
