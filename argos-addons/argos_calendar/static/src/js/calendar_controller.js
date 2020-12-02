odoo.define('argos_calendar.CalendarController', function (require) {
    "use strict";

    var CalendarController = require('web.CalendarController');
    var config = require('web.config');
    var core = require('web.core');
    var dialogs = require('web.view_dialogs');
    var Dialog = require('web.Dialog');
    var QuickCreate = require('web.CalendarQuickCreate');
    var session = require('web.session');

    var _t = core._t;
    var QWeb = core.qweb;


    function dateToServer(date) {
        return date.clone().utc().locale('en').format('YYYY-MM-DD HH:mm:ss');
    }

    CalendarController.include({
        init: function () {
            this._super.apply(this, arguments);
        },

        _onChangeFilter: function (event) {
            if (this.context.agenda_calendar && event.data.fieldName == 'employee_id') {
                if (this.model.changeFilter(event.data) && !event.data.no_reload) {
                    Promise.all([this.renderer._updateEventResources()]).then(this.reload());
                } else {
                    this.reload();
                }
            } else {
                this._super.apply(this, arguments);
            }
        },

        _onViewUpdated: function (event) {
            this._super.apply(this, arguments);
            if (this.context.agenda_calendar) {
                this.updateView(0);
            }
        },

        _onOpenEvent: function (event) {
            if (this.context.agenda_calendar) {
                var self = this;
                var id = event.data._id;
                id = id && parseInt(id).toString() === id ? parseInt(id) : id;

                if (!this.eventOpenPopup) {
                    this._rpc({
                        model: self.modelName,
                        method: 'get_formview_id',
                        //The event can be called by a view that can have another context than the default one.
                        args: [[id]],
                        context: event.context || self.context,
                    }).then(function (viewId) {
                        self.do_action({
                            type: 'ir.actions.act_window',
                            res_id: id,
                            res_model: self.modelName,
                            views: [[viewId || false, 'form']],
                            target: 'current',
                            context: event.context || self.context,
                        });
                    });
                    return;
                }

                var options = {
                    res_model: self.modelName,
                    res_id: id || null,
                    context: event.context || self.context,
                    title: _t("Open: ") + event.data.title,
                    on_saved: function () {
                        if (event.data.on_save) {
                            event.data.on_save();
                        }
                        var $calendar = self.renderer.$calendar;
                        var $fc_view = $calendar.find('.fc-view-container');
                        var scrollPosition = $fc_view.scrollLeft();
                        self.updateView(scrollPosition, true);
                    }
                };
                if (this.formViewId) {
                    options.view_id = parseInt(this.formViewId);
                }
                options.buttons = [{
                    text: _t("Close"),
                    classes: "btn-secondary o_form_button_cancel pull-right",
                    close: true,
                    click: function () {
                        var $calendar = self.renderer.$calendar;
                        var $fc_view = $calendar.find('.fc-view-container');
                        var scrollPosition = $fc_view.scrollLeft();
                        self.updateView(scrollPosition, true);
                    },
                }];
                new dialogs.FormViewDialog(this, options).open();
            } else {
                return this._super.apply(this, arguments);
            }
        },

        _onOpenCreate: function (event) {
            if (this.context.agenda_calendar) {
                var self = this;
                if (event.data.resource && event.data.resource.id) {
                    var value = event.data.resource.id;
                    if (this.model.fields[this.model.fieldColumn].type === 'many2one')
                        value = parseInt(value);
                    this.context['default_' + this.model.fieldColumn] = value;
                } else
                    this.context['default_' + this.model.fieldColumn] = false;
                this.context['default_operating_unit_id'] = session.operating_unit_id;

                if (this.model.get().scale === "month") {
                    event.data.allDay = true;
                }
                var data = this.model.calendarEventToRecord(event.data);

                var context = _.extend({}, this.context, event.options && event.options.context);
                context.default_name = data.name || null;
                context['default_' + this.mapping.date_start] = data[this.mapping.date_start] || null;
                if (this.mapping.date_stop) {
                    context['default_' + this.mapping.date_stop] = data[this.mapping.date_stop] || null;
                }
                if (this.mapping.date_delay) {
                    context['default_' + this.mapping.date_delay] = data[this.mapping.date_delay] || null;
                }
                if (this.mapping.all_day) {
                    context['default_' + this.mapping.all_day] = data[this.mapping.all_day] || null;
                }

                for (var k in context) {
                    if (context[k] && context[k]._isAMomentObject) {
                        context[k] = dateToServer(context[k]);
                    }
                }

                var options = _.extend({}, this.options, event.options, {
                    context: context,
                    title: _.str.sprintf(_t('Create: %s'), (this.displayName || this.renderer.arch.attrs.string))
                });

                if (this.quick != null) {
                    this.quick.destroy();
                    this.quick = null;
                }

                if (!options.disableQuickCreate && !event.data.disableQuickCreate && this.quickAddPop) {
                    this.quick = new QuickCreate(this, true, options, data, event.data);
                    this.quick.open();
                    this.quick.opened(function () {
                        self.quick.focus();
                    });
                    return;
                }

                var title = _t("Create");
                if (this.renderer.arch.attrs.string) {
                    title += ': ' + this.renderer.arch.attrs.string;
                }
                if (this.eventOpenPopup) {
                    if (this.previousOpen) {
                        this.previousOpen.close();
                    }

                    this.previousOpen = new dialogs.FormViewDialog(self, {
                        res_model: this.modelName,
                        context: context,
                        title: title,
                        view_id: this.formViewId || false,
                        disable_multiple_selection: true,
                        buttons: [{
                            text: _t("Close"),
                            classes: "btn-secondary o_form_button_cancel pull-right",
                            close: true,
                            click: function () {
                                var $calendar = self.renderer.$calendar;
                                var $fc_view = $calendar.find('.fc-view-container');
                                var scrollPosition = $fc_view.scrollLeft();
                                self.updateView(scrollPosition, true);
                            },
                        }],
                        on_saved: function () {
                            if (event.data.on_save) {
                                event.data.on_save();
                            }
                            var $calendar = self.renderer.$calendar;
                            var $fc_view = $calendar.find('.fc-view-container');
                            var scrollPosition = $fc_view.scrollLeft();
                            self.updateView(scrollPosition, true);
                        },
                    });
                    this.previousOpen.open();
                } else {
                    this.do_action({
                        type: 'ir.actions.act_window',
                        res_model: this.modelName,
                        views: [[this.formViewId || false, 'form']],
                        target: 'current',
                        context: context,
                    });
                }
            } else {
                this._super.apply(this, arguments);
            }
        },

        _onDropRecord: function (event) {
            if (this.context.agenda_calendar) {
                var self = this;
                var $calendar = this.renderer.$calendar;
                var $fc_view = $calendar.find('.fc-view-container');
                var scrollPosition = $fc_view.scrollLeft();
                return Promise.all([this._super.apply(this, arguments)]).then(function () {
                    self.updateView(scrollPosition, true);
                });
            } else {
                this._super.apply(this, arguments);
            }
        },

        _onUpdateRecord: function (event) {
            if (this.context.agenda_calendar) {
                var self = this;
                var $calendar = this.renderer.$calendar;
                var $fc_view = $calendar.find('.fc-view-container');
                var scrollPosition = $fc_view.scrollLeft();
                return Promise.all([this._super.apply(this, arguments)]).then(function () {
                    self.updateView(scrollPosition, true);
                });
            } else {
                this._super.apply(this, arguments);
            }
        },

        _onDeleteRecord: function (event) {
            if (this.context.agenda_calendar) {
                var self = this;
                Dialog.confirm(this, _t("Are you sure you want to delete this record ?"), {
                    confirm_callback: function () {
                        self.model.deleteRecords([event.data.id], self.modelName).then(function () {
                            var $calendar = self.renderer.$calendar;
                            var $fc_view = $calendar.find('.fc-view-container');
                            var scrollPosition = $fc_view.scrollLeft();
                            self.updateView(scrollPosition, true);
                        });
                    }
                });
            } else {
                this._super.apply(this, arguments);
            }
        },

        updateView: function (position, reload = false) {
            var self = this;
            var $calendar = this.renderer.$calendar;
            var $fc_view = $calendar.find('.fc-view-container');
            if (reload) {
                Promise.all([this.reload()]).then(function () {
                    self.renderer._updateEventResources();
                    self.renderer._renderActivityGrid();
                    self.renderer._renderTaskGrid();
                    self.renderer._renderStickyTimeline();
                    self.renderer._toogleCalendarHeader();
                    self.renderer._updateCalendarStyle();
                    $fc_view.scrollLeft(position);
                });
            } else {
                $fc_view.scrollLeft(position);
                self.renderer._updateEventResources();
                self.renderer._renderActivityGrid();
                self.renderer._renderTaskGrid();
                self.renderer._renderStickyTimeline();
                self.renderer._toogleCalendarHeader();
                self.renderer._updateCalendarStyle();
                self.renderer._renderStickyTimeline();
            }
        },

        renderButtons: function ($node) {
            if (this.context.agenda_calendar) {
                var self = this;
                var clockInterval = [{
                    'name': _t('Default'),
                    'interval': '00:00-24:00',
                }, {
                    'name': _t('Morning'),
                    'interval': '08:00-14:00',
                }, {
                    'name': _t('Afternoon'),
                    'interval': '14:00-20:00',
                }, {
                    'name': _t('Whole day'),
                    'interval': '08:00-20:00',
                }];
                this.$buttons = $(QWeb.render('AgendaView.buttons', {
                    isMobile: config.device.isMobile,
                    clockInterval: clockInterval
                }));
                this.$buttons.on('click', 'button.o_calendar_button_new', function () {
                    self.trigger_up('switch_view', {view_type: 'form'});
                });
                this.$buttons.on('click', '.dropdown-menu button', function (event) {
                    var $target = $(event.target);
                    var interval = $target.attr('data-interval');
                    var min_interval = interval.split('-')[0];
                    var max_interval = interval.split('-')[1];
                    var active_max_interval = self.renderer.$calendar.fullCalendar('option', 'maxTime');
                    if (min_interval < active_max_interval) {
                        self.renderer.$calendar.fullCalendar('option', 'minTime', min_interval);
                        self.renderer.$calendar.fullCalendar('option', 'maxTime', max_interval);
                    } else {
                        self.renderer.$calendar.fullCalendar('option', 'maxTime', max_interval);
                        self.renderer.$calendar.fullCalendar('option', 'minTime', min_interval);
                    }
                    self.$buttons.find('button.o_calendar_button_clock').html(interval);
                    $(window).trigger('resize');
                });
                _.each(['prev', 'today', 'next'], function (action) {
                    self.$buttons.on('click', '.o_calendar_button_' + action, function () {
                        self._move(action);
                    });
                });
                _.each(['day', 'week'], function (scale) {
                    self.$buttons.on('click', '.o_calendar_button_' + scale, function () {
                        self.model.setScale(scale);
                        self.reload();
                    });
                });
                this.$buttons.find('.o_calendar_button_' + this.mode).addClass('active');
                if ($node) {
                    this.$buttons.appendTo($node);
                } else {
                    this.$('.o_calendar_buttons').replaceWith(this.$buttons);
                }
            } else {
                this._super.apply(this, arguments);
            }
        }
    });
});
