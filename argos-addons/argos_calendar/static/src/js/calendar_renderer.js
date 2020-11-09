odoo.define('argos_calendar.CalendarRenderer', function (require) {
    "use strict";

    var CalendarRenderer = require('web.CalendarRenderer');
    var config = require('web.config');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var FieldManagerMixin = require('web.FieldManagerMixin');
    var session = require('web.session');
    var Widget = require('web.Widget');

    var qweb = core.qweb;
    var _t = core._t;

    var SidebarFilter = Widget.extend(FieldManagerMixin, {
        template: 'CalendarView.sidebar.filter',
        custom_events: _.extend({}, FieldManagerMixin.custom_events, {
            field_changed: '_onFieldChanged',
        }),

        init: function (parent, options) {
            this._super.apply(this, arguments);
            FieldManagerMixin.init.call(this);

            this.title = options.title;
            this.fields = options.fields;
            this.fieldName = options.fieldName;
            this.write_model = options.write_model;
            this.write_field = options.write_field;
            this.avatar_field = options.avatar_field;
            this.avatar_model = options.avatar_model;
            this.filters = options.filters;
            this.label = options.label;
            this.getColor = options.getColor;
            this.isSwipeEnabled = true;
        },
        /**
         * @override
         */
        willStart: function () {
            var self = this;
            var defs = [this._super.apply(this, arguments)];

            if (this.write_model || this.write_field) {
                var def = this.model.makeRecord(this.write_model, [{
                    name: this.write_field,
                    relation: this.fields[this.fieldName].relation,
                    type: 'many2one',
                }]).then(function (recordID) {
                    self.many2one = new SidebarFilterM2O(self,
                        self.write_field,
                        self.model.get(recordID),
                        {
                            mode: 'edit',
                            attrs: {
                                placeholder: "+ " + _.str.sprintf(_t("Add %s"), self.title),
                                can_create: false
                            },
                        });
                });
                defs.push(def);
            }
            return Promise.all(defs);

        },
        /**
         * @override
         */
        start: function () {
            this._super();
            if (this.many2one) {
                this.many2one.appendTo(this.$el);
                this.many2one.filter_ids = _.without(_.pluck(this.filters, 'value'), 'all');
            }
            this.$el.on('click', '.o_remove', this._onFilterRemove.bind(this));
            this.$el.on('click', '.o_calendar_filter_items input', this._onFilterActive.bind(this));
        },

        //--------------------------------------------------------------------------
        // Handlers
        //--------------------------------------------------------------------------

        /**
         * @private
         * @param {OdooEvent} event
         */
        _onFieldChanged: function (event) {
            var self = this;
            event.stopPropagation();
            var createValues = {'user_id': session.uid};
            var value = event.data.changes[this.write_field].id;
            createValues[this.write_field] = value;
            this._rpc({
                model: this.write_model,
                method: 'create',
                args: [createValues],
            })
                .then(function () {
                    self.trigger_up('changeFilter', {
                        'fieldName': self.fieldName,
                        'value': value,
                        'active': true,
                    });
                });
        },
        /**
         * @private
         * @param {MouseEvent} e
         */
        _onFilterActive: function (e) {
            var $input = $(e.currentTarget);
            this.trigger_up('changeFilter', {
                'fieldName': this.fieldName,
                'value': $input.closest('.o_calendar_filter_item').data('value'),
                'active': $input.prop('checked'),
            });
        },
        /**
         * @private
         * @param {MouseEvent} e
         */
        _onFilterRemove: function (e) {
            var self = this;
            var $filter = $(e.currentTarget).closest('.o_calendar_filter_item');
            Dialog.confirm(this, _t("Do you really want to delete this filter from favorites ?"), {
                confirm_callback: function () {
                    self._rpc({
                        model: self.write_model,
                        method: 'unlink',
                        args: [[$filter.data('id')]],
                    })
                        .then(function () {
                            self.trigger_up('changeFilter', {
                                'fieldName': self.fieldName,
                                'id': $filter.data('id'),
                                'active': false,
                                'value': $filter.data('value'),
                            });
                        });
                },
            });
        },
    });

    CalendarRenderer.include({
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.dispose_popover = true;
            this.toggle_header = true;
            this.toogle_sidebar = true;
        },

        _unselectEvent: function () {
            if (this.state.context.agenda_calendar) {
                if (!this.$('.o_cw_popover').length) {
                    this.event_click = false;
                }
                this.$('.fc-event').removeClass('o_cw_custom_agenda_highlight');
                this.$('.o_cw_popover').popover('dispose');
            } else {
                this._super.apply(this, arguments);
            }
        },

        _render: function () {
            if (this.state.context.agenda_calendar) {
                var self = this;
                return Promise.all([self._super.apply(self, arguments)]).then(function (res) {
                    self._renderOffTime();
                    self._renderActivityGrid();
                    self._renderTaskGrid();
                    self._renderStickyTimeline();
                    self._toogleCalendarHeader();
                    if (!config.device.isMobile) {
                        self._toogleCalendarSidebar();
                    }
                    self._updateCalendarStyle();
                    return res;
                })
            } else {
                return Promise.all([this._super.apply(this, arguments)])
            }
        },

        _eventRender: function (event) {
            if (this.state.context.agenda_calendar) {
                var qweb_context = {
                    event: event,
                    record: event.record,
                    color: this.getColor(event.color_index),
                };
                this.qweb_context = qweb_context;
                if (_.isEmpty(qweb_context.record)) {
                    return '';
                } else {
                    return qweb.render("agenda-box", qweb_context);
                }
            }
            return this._super.apply(this, arguments);
        },

        _renderFilters: function () {
            var self = this;
            return Promise.all([this._super.apply(this, arguments)]).then(function (res) {
                if (self.state.context.agenda_calendar && !self.initial_filter) {
                    self._rpc({
                        model: 'planning.slot',
                        method: 'get_inactive_filters',
                        context: self.state.context,
                    }).then(function (inactive_filters) {
                        _.each(inactive_filters, function (f) {
                            self.trigger_up('changeFilter', {
                                'fieldName': 'role_id',
                                'value': f,
                                'active': false,
                            });
                            self.initial_filter = true;
                        });
                    });
                }
                return res;
            });
        },

        _renderFiltersOneByOne: function (filterIndex) {
            if (this.state.context.agenda_calendar) {
                filterIndex = filterIndex || 0;
                var arrFilters = _.sortBy(_.toArray(this.state.filters), function (f) {
                    return f.fieldName;
                });
                var prom;
                if (filterIndex < arrFilters.length) {
                    var options = arrFilters[filterIndex];
                    _.each(options.filters, function (f) {
                        f.display = true;
                    });
                    if (!_.find(options.filters, function (f) {
                        return f.display == null || f.display;
                    })) {
                        return;
                    }
                    var self = this;
                    options.getColor = this.getColor.bind(this);
                    options.fields = this.state.fields;
                    var filter = new SidebarFilter(self, options);
                    prom = filter.appendTo(this.$sidebar).then(function () {
                        // Show filter popover
                        if (options.avatar_field) {
                            _.each(options.filters, function (f) {
                                if (f.value !== 'all') {
                                    var selector = _.str.sprintf('.o_calendar_filter_item[data-value=%s]', f.value);
                                    self.$sidebar.find(selector).popover({
                                        animation: false,
                                        trigger: 'hover',
                                        html: true,
                                        placement: 'top',
                                        title: f.label,
                                        delay: {show: 300, hide: 0},
                                        content: function () {
                                            return $('<img>', {
                                                src: _.str.sprintf('/web/image/%s/%s/%s', options.avatar_model, f.value, options.avatar_field),
                                                class: 'mx-auto',
                                            });
                                        },
                                    });
                                }
                            });
                        }
                        return self._renderFiltersOneByOne(filterIndex + 1);
                    });
                    this.filters.push(filter);
                }
                return Promise.resolve(prom);
            } else {
                return Promise.all([this._super.apply(this, arguments)]);
            }
        },

        _disposePopover: function (eventData) {
            if (this.dispose_popover && this.last_event == eventData.id && !this.drag_start) {
                this.$('.fc-event').removeClass('o_cw_custom_agenda_highlight');
                this.$('.o_cw_popover').popover('dispose');
                this.event_click = false;
                this.dispose_popover = false;
            }
        },

        _onPopoverShown: function ($popoverElement, calendarPopover) {
            var self = this;
            this._super.apply(this, arguments);
            if (this.state.context.agenda_calendar) {
                var $popover = $($popoverElement.data('bs.popover').tip);
                $popover.on('mouseleave', function (event) {
                    self.dispose_popover = false;
                    self._unselectEvent();
                });
                $popover.on('mouseenter', function (event) {
                    self.dispose_popover = false;
                });
            }
        },

        _initCalendar: function () {
            var self = this;

            if (this.state.context.agenda_calendar) {
                this.$calendar = this.$(".o_calendar_widget");
                this.$calendar.addClass('calendar_agenda');

                var locale = moment.locale();
                $.fullCalendar.locale(locale);

                var fc_options = $.extend({}, this.state.fc_options, {
                    dayRender: function (date, cell) {
                        var today = $.fullCalendar.moment();
                        if (date.get('date') == today.get('date')) {
                            $(".fc-" + date.locale('en').format('ddd', 'en').toLowerCase()).addClass('fc-cur-day');
                        }
                    },
                    eventDrop: function (event) {
                        self.dispose_popover = false;
                        self.drag_start = false;
                        self.trigger_up('dropRecord', event);
                    },
                    eventResize: function (event) {
                        self.trigger_up('updateRecord', event);
                    },
                    eventClick: function (eventData, ev) {
                        self._unselectEvent();
                        self.event_click = true;
                        self.$calendar.find(_.str.sprintf('[data-event-id=%s]', eventData.id)).addClass('o_cw_custom_agenda_highlight');
                        self._renderEventPopover(eventData, $(ev.currentTarget));
                    },
                    select: function (startDate, endDate, event, _js_event, resource) {
                        self.isSwipeEnabled = false;
                        if (self.$('.o_cw_popover').length || self.event_click) {
                            self._unselectEvent();
                        } else {
                            self.$calendar.fullCalendar('unselect');
                            var data = {'start': startDate, 'end': endDate, 'resource': resource};
                            if (self.state.context.default_name) {
                                data.title = self.state.context.default_name;
                            }
                            self.trigger_up('openCreate', data);
                        }
                        self.$calendar.fullCalendar('unselect');
                    },
                    resourceRender: function (resourceObj, $th) {
                        var parent = $th;
                        var wrapper = document.createElement('div');
                        var span = document.createElement('span');
                        span.textContent = parent.text();
                        wrapper.appendChild(span);
                        parent.empty().append(wrapper).addClass('rotate');
                    },
                    eventAfterRender: function (event, element, view) {
                        if (event.rendering != "background") {
                            var $after_element = element.next();
                            var zindex = element.css('z-index');
                            var after_zindex = $after_element.css('z-index');
                            var element_style = $after_element.attr('style');
                            if ($after_element && after_zindex > zindex) {
                                if (element_style.split(';')[0].split(' ').length == 5) {
                                    element.width((element_style.split(';')[0].split(' ')[4].replace('%', '') / zindex) + '%');
                                } else {
                                    element.width(element_style.split(';')[0].split(' ')[2]);
                                }
                            }
                            var element_width = element.find('.fc-content').outerWidth();
                            var element_height = element.find('.fc-content').parent().outerHeight();
                            if (element_width < 100) {
                                element.find('.fc-content i.o_event_cock').addClass('d-none');
                                element.find('.fc-content div.event_icon').removeClass('float-right');
                                if (element_height < 70) {
                                    element.find('.fc-content div.event_icon').addClass('d-none');
                                }
                            }
                        }
                    },
                    eventRender: function (event, element, view) {
                        self.isSwipeEnabled = false;
                        var $render = $(self._eventRender(event));
                        element.find('.fc-content').html($render.html());
                        element.addClass($render.attr('class'));
                        element.attr('data-event-id', event.id);
                        if (!element.find('.fc-bg').length) {
                            element.find('.fc-content').after($('<div/>', {class: 'fc-bg'}));
                        }
                        if (view.name === 'month' && event.record) {
                            var start = event.r_start || event.start;
                            var end = event.r_end || event.end;
                            var isSameDayEvent = start.clone().add(1, 'minute').isSame(end.clone().subtract(1, 'minute'), 'day');
                            if (!event.record.allday && isSameDayEvent) {
                                element.addClass('o_cw_nobg');
                            }
                        }

                        element.on('dblclick', function () {
                            self.trigger_up('edit_event', {id: event.id});
                        });
                    },
                    eventAfterAllRender: function () {
                        self.isSwipeEnabled = true;
                        self._updateResourcesWidth();
                    },
                    viewRender: function (view) {
                        var mode = view.name === 'month' ? 'month' : (view.name === 'agendaWeek' ? 'week' : 'day');
                        self.trigger_up('viewUpdated', {
                            mode: mode,
                            title: view.title,
                        });
                    },
                    eventMouseover: function (eventData, ev) {
                        self.last_event = eventData.id;
                        self.dispose_popover = false;
                        self._unselectEvent();
                        self.$calendar.find(_.str.sprintf('[data-event-id=%s]', eventData.id)).addClass('o_cw_custom_agenda_hover');
                        var container_width = self.$calendar.find('.fc-view-container').outerWidth();
                        if (eventData.record && container_width >= 780) {
                            self._renderEventPopover(eventData, $(ev.currentTarget));
                        }
                    },
                    eventMouseout: function (eventData, ev) {
                        self.dispose_popover = true;
                        if (!self.event_click) {
                            setTimeout(function () {
                                self._disposePopover(eventData);
                            }, 100);
                            self.$calendar.find(_.str.sprintf('[data-event-id=%s]', eventData.id)).removeClass('o_cw_custom_agenda_hover');
                        } else {
                            self.$calendar.find(_.str.sprintf('[data-event-id=%s]', eventData.id)).removeClass('o_cw_custom_agenda_hover');
                        }
                    },
                    eventDragStart: function (eventData, ev) {
                        self.drag_start = true;
                        self._unselectEvent();
                        self.dispose_popover = false;
                    },
                    eventResizeStart: function () {
                        self._unselectEvent();
                    },
                    eventLimitClick: function () {
                        self._unselectEvent();
                        return 'popover';
                    },
                    windowResize: function () {
                        Promise.all([self._updateEventResources()]).then(function () {
                            self._render();
                        });
                    },
                    views: {
                        day: {
                            columnFormat: 'LL',
                        },
                        week: {
                            columnFormat: 'dddd D',
                        },
                        month: {
                            columnFormat: config.device.isMobile ? 'ddd' : 'dddd',
                        }
                    },
                    height: 'parent',
                    unselectAuto: false,
                    isRTL: _t.database.parameters.direction === "rtl",
                    schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
                    locale: locale,
                });

                this.$calendar.fullCalendar(fc_options);
                $(window).trigger('resize');
            } else {
                this._super.apply(this, arguments);
            }
        },

        _toogleCalendarHeader: function () {
            var self = this;
            this.$calendar.find('th.fc-axis.fc-week-number:last').unbind();
            this.$calendar.find('th.fc-axis.fc-week-number:last').on('click', function (ev) {
                ev.stopPropagation();
                self.toggle_header = !self.toggle_header;
                self._toogleCalendarHeader();
                $(window).trigger('resize');
            });
            this.$calendar.find('.fc-day-activity-grid').toggle(this.toggle_header);
            this.$calendar.find('.fc-day-task-grid').toggle(this.toggle_header);
            this.$calendar.find('.fc-day-grid').toggle(this.toggle_header);
            if (this.toggle_header) {
                this.$calendar.find('th.fc-axis.fc-week-number:last').html($('<button class="btn btn-secondary fa fa-caret-down" style="color: #63BAE9"></button>'));
            } else {
                this.$calendar.find('th.fc-axis.fc-week-number:last').html($('<button class="btn btn-secondary fa fa-caret-right" style="color: #63BAE9"></button>'));
            }
        },

        _toogleCalendarSidebar: function () {
            var self = this;
            if (this.$sidebar_container.find('.toogle_sidebar').length <= 0) {
                var wrapper = document.createElement('div');
                $(wrapper).addClass('toogle_sidebar');
                this.$sidebar_container.prepend(wrapper);
                this.$sidebar_container.toggleClass('d-md-block d-flex');
            }
            this.$sidebar_container.find('.o_calendar_sidebar').toggle(this.toogle_sidebar);
            if (this.toogle_sidebar) {
                this.$sidebar_container.find('.toogle_sidebar').html($('<button class="toogle_sidebar_button btn btn-secondary fa fa-chevron-left" style="color: #63BAE9"></button>'));
            } else {
                this.$sidebar_container.find('.toogle_sidebar').html($('<button class="toogle_sidebar_button btn btn-secondary fa fa-chevron-right" style="color: #63BAE9"></button>'));
            }
            this.$sidebar_container.find('.toogle_sidebar_button').on('click', function (ev) {
                ev.stopPropagation();
                self.toogle_sidebar = !self.toogle_sidebar;
                self._toogleCalendarSidebar();
                $(window).trigger('resize');
            });
        },

        _updateCalendarStyle: function () {
            var first_resource_id = this.$calendar.find('th.fc-resource-cell:first').attr('data-resource-id');
            var last_resource_id = this.$calendar.find('th.fc-resource-cell:last').attr('data-resource-id');
            if (first_resource_id && last_resource_id) {
                this.$calendar.find('td .fc-day[data-resource-id=' + first_resource_id + ']').addClass('fc-resource-cell-first');
                this.$calendar.find('td .fc-day[data-resource-id=' + last_resource_id + ']').addClass('fc-resource-cell-last');
            }
        },

        _updateResourcesWidth: function () {
            var container_width = this.$calendar.find('.fc-view-container').outerWidth();
            var width = this.$calendar.fullCalendar('getResources').length * 7 * 140;
            if (width < container_width) {
                width = container_width;
            }
            var header_elem = this.$calendar.find('.fc-view.fc-agendaWeek-view.fc-agenda-view');
            header_elem.width(width);
        },

        _updateEventResources: function () {
            var self = this;
            this.$calendar.fullCalendar('refetchResources');
            if (this.state.columns) {
                _.each(Object.entries(this.state.columns), function (column) {
                    var f = _.find(self.state.filters['employee_id'].filters, function (l) {
                        return l.value == column[0] || (l.value == false && column[0] == "false");
                    });
                    if (f && f.active) {
                        self.$calendar.fullCalendar('addResource', {
                            id: column[0],
                            title: column[1]
                        });
                    }
                });
            }
        },

        _renderOffTime: function () {
            var self = this;
            var startDate = $(self.$calendar.find('.fc-day-grid .fc-day.fc-widget-content')[0]).attr('data-date');
            var endDate = $(self.$calendar.find('.fc-day-grid .fc-day.fc-widget-content').slice(-1)[0]).attr('data-date');
            if (startDate && endDate) {
                self._rpc({
                    model: 'planning.slot',
                    method: 'get_resources_data',
                    args: [startDate, endDate],
                    context: self.state.context
                }).then(function (events) {
                    self.$calendar.fullCalendar('addEventSource', events);
                });
            }
        },

        _renderStickyTimeline: function () {
            var self = this;
            if (self.state.scale == 'week') {
                var $nowIndicator = self.$calendar.find('.fc-content-col .fc-now-indicator.fc-now-indicator-line').parent();
                $nowIndicator.off("DOMSubtreeModified");
                $nowIndicator.on('DOMSubtreeModified', function () {
                    self._renderStickyTimeline();
                });
                self.$calendar.find('.clone-time-grid-wrap').remove();
                var timelineWidth = self.$calendar.find('.fc-axis.fc-time.fc-widget-content').outerWidth();
                var $timeGrid = self.$calendar.find('.fc-time-grid.fc-unselectable').clone();
                var $timeGridClass = 'clone-time-grid-wrap';
                var $timeGridWrap = $('<div class="' + $timeGridClass + '"></div>')
                    .append($timeGrid)
                    .css('position', 'absolute')
                    .css('overflow', 'hidden')
                    .css('width', timelineWidth)
                    .css('background', 'white')
                    .css('z-index', 1);
                self.$calendar.find('.fc-scroller.fc-time-grid-container').append($timeGridWrap);
                self.$calendar.find('.fc-view-container').on('scroll', function () {
                    $timeGridWrap.css('left', -1 * self.$calendar.find('.fc-time-grid.fc-unselectable').offset().left);
                    $timeGridWrap.css('top', 0);
                });
                self.$calendar.find('.fc-scroller.fc-time-grid-container').on('scroll', function () {
                    $timeGridWrap.css('left', -1 * self.$calendar.find('.fc-time-grid.fc-unselectable').offset().left);
                    $timeGridWrap.css('top', 0);
                })
            }
        },

        _renderActivityGrid: function () {
            var self = this;
            var $activityGrid = self.$calendar.find('.fc-day-grid').clone();
            $activityGrid.removeClass().addClass('fc-day-activity-grid');
            $activityGrid.find('.fc-content-skeleton').remove();
            $activityGrid.find('.fc-axis span').text(_t('Activities'));
            var startDate = $($activityGrid.find('.fc-day.fc-widget-content')[0]).attr('data-date');
            var endDate = $($activityGrid.find('.fc-day.fc-widget-content').slice(-1)[0]).attr('data-date');
            if (startDate && endDate) {
                var resources = _.filter(Object.keys(self.state.columns), function (resource) {
                    return resource != 'false';
                });
                Promise.all([this.getActivities(startDate, endDate, resources)]).then(function (result) {
                    var activities = result[0];
                    _.each($activityGrid.find('.fc-day.fc-widget-content'), function (element) {
                        var resourceId = $(element).attr('data-resource-id');
                        var eventDate = $(element).attr('data-date');
                        if (activities[resourceId]) {
                            var eventCount = activities[resourceId][eventDate];
                            if (eventCount > 0) {
                                var $activities = $('<a class="o_mail_systray_item" title="' + _t('Activities') + '" href="#" role="button"><i class="fa fa-lg fa-clock-o" role="img" aria-label="Activities"></i><span class="o_notification_counter badge badge-pill">' + eventCount + '</span></a>');
                                $(element).append($activities);
                            }
                        }
                    });
                    $activityGrid.find('.fc-day.fc-widget-content a').on('click', function (event) {
                        self.openActivity(event);
                    });
                });
                self.$calendar.find('.fc-day-activity-grid').remove();
                self.$calendar.find('.fc-day-grid').before($activityGrid);
            }
        },

        _renderTaskGrid: function () {
            var self = this;
            var $taskGrid = self.$calendar.find('.fc-day-grid').clone();
            $taskGrid.removeClass().addClass('fc-day-task-grid');
            $taskGrid.find('.fc-content-skeleton').remove();
            $taskGrid.find('.fc-axis span').text(_t('Tasks'));
            var startDate = $($taskGrid.find('.fc-day.fc-widget-content')[0]).attr('data-date');
            var endDate = $($taskGrid.find('.fc-day.fc-widget-content').slice(-1)[0]).attr('data-date');
            if (startDate && endDate) {
                var resources = _.filter(Object.keys(self.state.columns), function (resource) {
                    return resource != 'false';
                });
                Promise.all([this.getTasks(startDate, endDate, resources)]).then(function (result) {
                    var tasks = result[0];
                    _.each($taskGrid.find('.fc-day.fc-widget-content'), function (element) {
                        var resourceId = $(element).attr('data-resource-id');
                        var eventDate = $(element).attr('data-date');
                        if (tasks[resourceId]) {
                            var eventCount = tasks[resourceId][eventDate];
                            if (eventCount > 0) {
                                var $tasks = $('<a class="o_mail_systray_item" title="' + _t('Tasks') + '" href="#" role="button"><i class="fa fa-lg fa-clock-o" role="img" aria-label="Tasks"></i><span class="o_notification_counter badge badge-pill">' + eventCount + '</span></a>');
                                $(element).append($tasks);
                            }
                        }
                    });
                    $taskGrid.find('.fc-day.fc-widget-content a').on('click', function (event) {
                        self.openTask(event);
                    });
                });
                self.$calendar.find('.fc-day-task-grid').remove();
                self.$calendar.find('.fc-day-grid').before($taskGrid);
            }
        },

        openActivity: function (event) {
            event.stopPropagation();
            event.preventDefault();
            var self = this;
            var $target = $(event.currentTarget).parent();
            var resourceId = parseInt($target.attr('data-resource-id'));
            var eventDate = $target.attr('data-date');
            this._rpc({
                model: 'planning.slot',
                method: 'get_activity_action',
                args: [resourceId, eventDate],
                context: self.state.context,
            }).then(function (action) {
                self.do_action(action);
            });
        },

        openTask: function (event) {
            event.preventDefault();
            event.stopPropagation();
            var self = this;
            var $target = $(event.currentTarget).parent();
            var resourceId = parseInt($target.attr('data-resource-id'));
            var eventDate = $target.attr('data-date');
            this._rpc({
                model: 'planning.slot',
                method: 'get_task_action',
                args: [resourceId, eventDate],
                context: self.state.context,
            }).then(function (action) {
                self.do_action(action);
            });
        },

        getActivities: function (startDate, endDate, resources) {
            var self = this;
            return self._rpc({
                model: 'planning.slot',
                method: 'get_activities',
                args: [startDate, endDate, resources],
                context: self.state.context,
            }).then(function (activities) {
                return activities;
            });
        },

        getTasks: function (startDate, endDate, resources) {
            var self = this;
            return self._rpc({
                model: 'planning.slot',
                method: 'get_tasks',
                args: [startDate, endDate, resources],
                context: self.state.context,
            }).then(function (tasks) {
                return tasks;
            });
        },
    });
});
