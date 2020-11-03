odoo.define('argos_calendar.CalendarView', function (require) {
    "use strict";

    var CalendarView = require('web.CalendarView');

    CalendarView.include({
        jsLibs: [
            '/web/static/lib/fullcalendar/js/fullcalendar.js',
            '/argos_calendar/static/lib/scheduler.min.js',
        ],

        cssLibs: [
            '/web/static/lib/fullcalendar/css/fullcalendar.css',
            '/argos_calendar/static/lib/scheduler.min.css',
        ],

        init: function (viewInfo, params) {
            this._super.apply(this, arguments);
            var fieldNames = this.loadParams.fieldNames;
            var filters = this.loadParams.filters;
            var fields = this.loadParams.fields;
            if (params.context.column) {
                var fieldName = params.context.column;
                fieldNames.push(fieldName);
                if (params.context.agenda_calendar) {
                    filters['employee_id'] = {
                        'title': fields['employee_id'].string,
                        'fieldName': 'employee_id',
                        'filters': [],
                        'avatar_field': 'image_128',
                        'avatar_model': fields['employee_id'].relation,
                        'filter_model': 'planning.slot',
                    };
                }
            }
            this.loadParams.fieldColumn = params.context.column;
            this.loadParams.fieldNames = _.uniq(fieldNames);
            this.loadParams.forceColumns = params.context.force_columns;
        },
    });
});
