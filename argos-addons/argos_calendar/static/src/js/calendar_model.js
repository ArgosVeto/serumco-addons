odoo.define('argos_calendar.CalendarModel', function (require) {
    "use strict";

    var CalendarModel = require('web.CalendarModel');
    var core = require('web.core');
    var _t = core._t;

    CalendarModel.include({
        load: function (params) {
            this.fieldColumn = params.fieldColumn;
            this.forceColumns = params.forceColumns;
            return this._super.apply(this, arguments);
        },

        _filter_visible_filters: function () {
            var self = this;
            _.each(self.data.filters, function (filter) {
                if (filter.filter_model == 'planning.slot') {
                    var new_filters = [];
                    _.each(self.data.columns, function (value, key) {
                        var f = _.find(filter.filters, function (l) {
                            return l.value == key || (l.value == false && key == "false");
                        });
                        if (f) {
                            if(key == "false" || key == false){
                                f.label = _t('To assign');
                            }
                            new_filters.push(f);
                        } else {
                            new_filters.push({
                                'color_index': false,
                                'value': (key == "false" || key == false) ? false : parseInt(key),
                                'label': value,
                                'avatar_model': 'hr.employee',
                                'active': true,
                                'display': true,
                            });
                        }
                    });
                    filter.filters = new_filters;
                }
            });
        },

        _loadRecordsToFilters: function (element, events) {
            var self = this;
            return this._super.apply(this, arguments).then(function (result) {
                if (self.fieldColumn) {
                    return self._rpc({
                        model: self.modelName,
                        method: 'get_resources',
                        context: self.data.context,
                    }).then(function (events) {
                        self._compute_columns(self.data, events);
                        self._filter_visible_filters();
                        return result;
                    });
                }
            });
        },

        _compute_columns: function (element, events) {
            if (this.fieldColumn && this.forceColumns) {
                this.data.columns = this.forceColumns;
            } else if (this.fieldColumn) {
                var fieldName = this.fieldColumn;
                events = events[fieldName];
                this.data.columns = events;
            }
        },

        _recordToCalendarEvent: function (evt) {
            var result = this._super.apply(this, arguments);
            if (this.fieldColumn) {
                var value = evt[this.fieldColumn];
                result.resourceId = _.isArray(value) ? value[0] : value;
                if (evt.background_event) {
                    result.rendering = 'background';
                }
            }
            return result;
        },

        _getFullCalendarOptions: function () {
            var result = this._super.apply(this, arguments);
            result.schedulerLicenseKey = 'GPL-My-Project-Is-Open-Source';
            if (this.fieldColumn) {
                // var minTime = '08:00';
                // var maxTime = '20:00';
                var slotDuration = '00:15:00';
                // var slotLabelInterval = 15;
                // result.minTime = minTime;
                // result.maxTime = maxTime;
                result.slotDuration = slotDuration;
                // result.slotLabelInterval = slotLabelInterval;
                result.dragScroll = true;
                result.resources = [];
                result.groupByDateAndResource = true;
                // result.eventOverlap = false;
            }
            return result;
        },

        calendarEventToRecord: function (event) {
            var result = this._super.apply(this, arguments);
            if (event.resourceId)
                result[this.fieldColumn] = parseInt(event.resourceId);
            return result;
        },
    });
});
