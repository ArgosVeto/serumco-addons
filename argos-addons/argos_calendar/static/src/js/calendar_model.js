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

        _loadCalendar: function () {
            if (this.fieldColumn && !this.initial_load) {
                var self = this;
                this.data.fc_options = this._getFullCalendarOptions();

                var defs = _.map(this.data.filters, this._loadFilter.bind(this));

                return Promise.all(defs.concat(this._update_inactive_filters())).then(function () {
                    return self._rpc({
                        model: self.modelName,
                        method: 'search_read',
                        context: self.data.context,
                        fields: self.fieldNames,
                        domain: self.data.domain.concat(self._getRangeDomain()).concat(self._getFilterDomain())
                    }).then(function (events) {
                        self._parseServerData(events);
                        self.data.unfiltered_data = _.map(events, self._recordToCalendarEvent.bind(self));
                        self.data.data = _.filter(self.data.unfiltered_data, function(filter){
                            return self.data.inactive_filters.indexOf(filter.record.role_id[0]) == -1;
                        });
                        self.initial_load = true;
                        return Promise.all([
                            self._loadColors(self.data, self.data.data),
                            self._loadRecordsToFilters(self.data, self.data.unfiltered_data)
                        ]);
                    });
                });
            } else {
                return Promise.all([this._super.apply(this, arguments)]);
            }
        },

        _update_inactive_filters: function () {
            var self = this;
            return self._rpc({
                model: 'planning.slot',
                method: 'get_inactive_filters',
                context: self.data.context,
            }).then(function (inactive_filters) {
                self.data.inactive_filters = inactive_filters;
                return inactive_filters;
            });
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
                            if (key == "false" || key == false) {
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
                    var startDate = self.data.start_date.format('Y-M-D');
                    var endDate = self.data.end_date.format('Y-M-D');
                    return self._rpc({
                        model: self.modelName,
                        method: 'get_resources',
                        args: [startDate, endDate],
                        context: self.data.context
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
                var slotDuration = '00:15:00';
                result.minTime = '08:00';
                result.maxTime = '20:00';
                result.slotDuration = slotDuration;
                result.dragScroll = true;
                result.resources = [];
                result.groupByDateAndResource = true;
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
