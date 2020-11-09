odoo.define('argos_calendar.systray.ActivityMenu', function (require) {
    "use strict";

    var ActivityMenu = require('mail.systray.ActivityMenu');
    var fieldUtils = require('web.field_utils');
    var data_manager = require('web.data_manager');

    ActivityMenu.include({

        //-----------------------------------------
        // Private
        //-----------------------------------------

        /**
         * parse date to server value
         *
         * @private
         * @override
         */
        _getActivityData: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                var planning = _.find(self._activities, {type: 'next_planning'});
                if (planning && planning.plannings) {
                    _.each(planning.plannings, function (res) {
                        res.start_datetime = fieldUtils.parse.datetime(res.start_datetime, false, {isUTC: true});
                    });
                }
            });
        },

        //-----------------------------------------
        // Handlers
        //-----------------------------------------

        /**
         * @private
         * @override
         */
        _onActivityFilterClick: function (ev) {
            var $el = $(ev.currentTarget);
            var data = _.extend({}, $el.data());
            var self = this;
            if (data.res_model === "planning.slot" && data.filter === "my") {
                data_manager.load_action('argos_calendar.agenda_calendar_action_server').then(function (action) {
                    var planning = _.find(self._activities, {type: 'next_planning'});
                    action['context'] = {planning_domain: planning.domain};
                    self.do_action(action, {
                        additional_context: {
                            default_mode: 'day'
                        }
                    });
                });
            } else {
                this._super.apply(this, arguments);
            }
        },
    });

});
