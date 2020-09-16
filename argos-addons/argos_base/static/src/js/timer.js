odoo.define('argos_base.timer', function (require) {
"use strict";

var fieldRegistry = require('web.field_registry');
var AbstractField = require('web.AbstractField');

var TimerFieldWidget = AbstractField.extend({

    isSet: function () {
        return true;
    },
    _getDuration: function (dateStart, dateEnd) {
        if (dateEnd && dateStart) {
            return moment(dateEnd).diff(moment(dateStart));
        }
        if (dateStart) {
            return moment().diff(moment(dateStart));
        }
        else return 0;
    },
    _render: function () {
        this._startTimeCounter();

    },
    destroy: function () {
        this._super.apply(this, arguments);
        clearTimeout(this.timer);
    },
    _startTimeCounter: function () {
        var self = this;
        clearTimeout(this.timer);
        if (self.record.data.arrival_time && !self.record.data.pickup_time) {
            this.timer = setTimeout(function () {
                self._startTimeCounter();
            }, 1000);
            this.$el.text(moment.utc(self._getDuration(self.record.data.arrival_time, self.record.data.pickup_time)).format("HH:mm:ss"));
        } else if (self.record.data.pickup_time){
            clearTimeout(this.timer);
            this.$el.text(moment.utc(self._getDuration(self.record.data.arrival_time, self.record.data.pickup_time)).format("HH:mm:ss"));
        }
    },
});

fieldRegistry.add('timer', TimerFieldWidget);

});
