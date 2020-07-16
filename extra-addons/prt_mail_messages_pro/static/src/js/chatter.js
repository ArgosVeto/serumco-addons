odoo.define('prt_mail_messages_pro.Chatter', function (require) {
    "use strict";

    var Chatter = require('mail.Chatter');

    Chatter.include({

        // Events
        events: {
            'click .o_chatter_button_new_message': '_onOpenComposerMessage',
            'click .o_chatter_button_log_note': '_onOpenComposerNote',
            'click .o_chatter_button_attachment': '_onClickAttachmentButton',
            'click .o_chatter_button_schedule_activity': '_onScheduleActivity',
            // Cetmix events
            'click .notif_checkbox': '_onCheckboxClick',
            'click .note_checkbox': '_onCheckboxClick',
            'click .message_checkbox': '_onCheckboxClick',
        },

        // Start
        start: function () {
            this.getMessageFilters();
            return this._super.apply(this, arguments);
        },

        // Get message filters
        getMessageFilters: function () {
            var self = this;
            if (typeof this.fields.thread !== typeof undefined && this.fields.thread !== false){
                if (typeof this.fields.thread.res_id !== typeof undefined && this.fields.thread.res_id !== false){
                    this._rpc({
                        model: this.fields.thread.model,
                        method: 'read',
                        args: [[this.fields.thread.res_id], ['hide_notifications', 'hide_notes', 'hide_messages']],
                    }).then(function (result) {
                        var res = result[0];
                        self.$('.notif_checkbox').prop("checked", !res.hide_notifications);
                        self.$('.note_checkbox').prop("checked", !res.hide_notes);
                        self.$('.message_checkbox').prop("checked", !res.hide_messages);

                        _.extend(self.fields.thread._threadWidget._disabledOptions,
                            {hide_notifications: res.hide_notifications, hide_notes: res.hide_notes,
                                hide_messages: res.hide_messages,});

                    });
                }
            }
        },

        // Click any of checkbox
        _onCheckboxClick: function (event) {
            var self = this;
            var hide = !event.target.checked;
            var fieldName;
            if (event.target.className === 'btn btn-link notif_checkbox') {
                fieldName = 'hide_notifications';
            } else if (event.target.className === 'btn btn-link note_checkbox') {
                fieldName = 'hide_notes';
            } else {
                fieldName = 'hide_messages';
            }
            // Write to db
            this._rpc({
                model: this.fields.thread.model,
                method: 'write',
                args: [[this.fields.thread.res_id], {[fieldName]: hide,},],
            }).then(function () {
                if (hide){
                    _.extend(self.fields.thread._threadWidget._disabledOptions, {[fieldName]: hide,});
                } else {
                    _.extend(self.fields.thread._threadWidget._disabledOptions, {[fieldName]: hide,});
                }
                // Update thread in value if there are deleted messages
                var hasDeleted = self.fields.thread._documentThread.deletedMessageIDs || false;
                if (hasDeleted){
                    self.fields.thread.value.res_ids = self.fields.thread._documentThread._messageIDs;
                    self.fields.thread._documentThread.deletedMessageIDs = false;
                }
                self.update(self.fields.thread.record);
            });
            event.stopPropagation();
        }
    });
});
