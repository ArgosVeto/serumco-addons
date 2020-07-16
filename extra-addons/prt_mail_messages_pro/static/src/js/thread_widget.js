odoo.define('prt_mail_messages_pro.widget.Thread', function (require) {
    "use strict";

    var ThreadWidget = require('mail.widget.Thread');
    var core = require('web.core');
    var QWeb = core.qweb;
    var _t = core._t;
    var time = require('web.time');


    ThreadWidget.include({

        events: {
            'click a': '_onClickRedirect',
            'click img': '_onClickRedirect',
            'click strong': '_onClickRedirect',
            'click .o_thread_show_more': '_onClickShowMore',
            'click .o_attachment_download': '_onAttachmentDownload',
            'click .o_attachment_view': '_onAttachmentView',
            'click .o_attachment_delete_cross': '_onDeleteAttachment',
            'click .o_thread_message_needaction': '_onClickMessageNeedaction',
            'click .o_thread_message_star': '_onClickMessageStar',
            'click .o_thread_message_reply': '_onClickMessageReply',
            'click .oe_mail_expand': '_onClickMailExpand',
            'click .o_thread_message': '_onClickMessage',
            'click': '_onClick',
            'click .o_thread_message_email_exception': '_onClickEmailException',
            'click .o_thread_message_email_bounce': '_onClickEmailException',
            'click .o_thread_message_moderation': '_onClickMessageModeration',
            'change .moderation_checkbox': '_onChangeModerationCheckbox',

            // Cetmix
            "click .o_thread_message_reply_composer_quote": function (event) {
                event.stopPropagation();
                var message_id = $(event.currentTarget).data('message-id');
                this.reply_composer('quote', message_id);
            },
            "click .o_thread_message_reply_composer_forward": function (event) {
                event.stopPropagation();
                var message_id = $(event.currentTarget).data('message-id');
                this.reply_composer('forward', message_id);
            },
            "click .o_thread_message_reply_composer_move": function (event) {
                event.stopPropagation();
                var message_id = $(event.currentTarget).data('message-id');
                this.move_composer(message_id);
            },
            "click .o_thread_message_reply_composer_delete": function (event) {
                if (confirm(_t("Message will be deleted! Continue?"))) {
                    var message_id = $(event.currentTarget).data('message-id');
                    this._rpc({
                        model: 'mail.message',
                        method: 'unlink',
                        args: [[message_id]],
                    });
                    event.stopPropagation();
                }
            },
            "click .o_thread_message_reply_composer_edit": function (event) {
                // Open wizard
                var message_id = $(event.currentTarget).data('message-id');
                var action = {
                    type: 'ir.actions.act_window',
                    res_model: 'cx.message.edit.wiz',
                    view_mode: 'form',
                    view_type: 'form',
                    views: [[false, 'form']],
                    target: 'new',
                    context: {message_edit_id: message_id}
                };
                this.do_action(action, {});
                event.stopPropagation();
            },
        },

        // Reply or Quote
        reply_composer: function(wiz_mode, message_id) {
            var self = this;
            this._rpc({
                model: 'mail.message',
                method: 'reply_prep_context',
                args: [[message_id]],
                context: {wizard_mode:wiz_mode}
            }).then(function(result){
                var action = {
                    type: 'ir.actions.act_window',
                    res_model: 'mail.compose.message',
                    view_mode: 'form',
                    view_type: 'form',
                    views: [[false, 'form']],
                    target: 'new',
                    context: result,
                };
                self.do_action(action, {
                    on_close: function ()
                    {
                        self.trigger_up('reload');
                    }
                });
            })
        },

        // Move message
        move_composer: function(message_id) {
            var self = this;
            var thread;
            // Check thread type
            if (typeof self.__parentedParent._documentThread !== typeof undefined){
                thread = self.__parentedParent._documentThread
            } else {
                thread = self.__parentedParent._threadWidget
            }
            var message = _.filter(thread._messages, function (message) {
                return message._id === message_id;
            })[0];

            var oldThreadID = false;
            // Store old thread
            _.each(message.getThreadIDs(), function (thread_id) {
                var thread = self.call('mail_service', 'getThread', thread_id);
                if (thread && thread._type) {
                    // Count non document threads
                    if (thread._type === 'document_thread') {
                        oldThreadID = thread._id;
                    }
                }
            });


            // Open wizard
            var action = {
                type: 'ir.actions.act_window',
                res_model: 'prt.message.move.wiz',
                view_mode: 'form',
                view_type: 'form',
                views: [[false, 'form']],
                target: 'new',
                context: {thread_message_id: message_id, old_thread_id: oldThreadID},
            };
            self.do_action(action, {});
        },

        // Render thread
        render: function (thread, options) {
            var self = this;

            // Cetmix
            if (typeof this._disabledOptions.hide_notifications === typeof undefined)
            {
                return this._super.apply(this, arguments);
            }

            // Odoo
            var shouldScrollToBottomAfterRendering = false;
            if (this._currentThreadID === thread.getID() && this.isAtBottom()) {
                shouldScrollToBottomAfterRendering = true;
            }
            this._currentThreadID = thread.getID();

            // copy so that reverse do not alter order in the thread object
            // Cetmix. Filter messages
            var messages = _.clone(thread.getMessages({ domain: options.domain || [] }));

            // Filter notifications
            if (self._disabledOptions.hide_notifications) {
                messages = _.filter(messages, function (message) {
                    return message._type !== 'notification';
                });
            }

            // Filter notes
            if (self._disabledOptions.hide_notes) {
                messages = _.filter(messages, function (message) {
                    return !message._isNote;
                });
            }

            // Filter messages
            if (self._disabledOptions.hide_messages) {
                messages = _.filter(messages, function (message) {
                    return message._isNote || message._type === 'notification';
                });
            }

            var modeOptions = options.isCreateMode ? this._disabledOptions :
                this._enabledOptions;

            // attachments ordered by messages order (increasing ID)
            this.attachments = _.uniq(_.flatten(_.map(messages, function (message) {
                return message.getAttachments();
            })));

            options = _.extend({}, modeOptions, options, {
                selectedMessageID: this._selectedMessageID,
            });

            // dict where key is message ID, and value is whether it should display
            // the author of message or not visually
            var displayAuthorMessages = {};

            // Hide avatar and info of a message if that message and the previous
            // one are both comments wrote by the same author at the same minute
            // and in the same document (users can now post message in documents
            // directly from a channel that follows it)
            var prevMessage;
            _.each(messages, function (message) {
                if (
                    // is first message of thread
                    !prevMessage ||
                    // more than 1 min. elasped
                    (Math.abs(message.getDate().diff(prevMessage.getDate())) > 60000) ||
                    prevMessage.getType() !== 'comment' ||
                    message.getType() !== 'comment' ||
                    // from a different author
                    (prevMessage.getAuthorID() !== message.getAuthorID()) ||
                    (
                        // messages are linked to a document thread
                        (
                            prevMessage.isLinkedToDocumentThread() &&
                            message.isLinkedToDocumentThread()
                        ) &&
                        (
                            // are from different documents
                            prevMessage.getDocumentModel() !== message.getDocumentModel() ||
                            prevMessage.getDocumentID() !== message.getDocumentID()
                        )
                    )
                ) {
                    displayAuthorMessages[message.getID()] = true;
                } else {
                    displayAuthorMessages[message.getID()] = !options.squashCloseMessages;
                }
                prevMessage = message;
            });

            // Cetmix. We do not need to reverse messages becaue they already arrive reversed
            // if (modeOptions.displayOrder === ORDER.DESC) {
            //     messages.reverse();
            // }

            this.$el.html(QWeb.render('mail.widget.Thread', {
                thread: thread,
                displayAuthorMessages: displayAuthorMessages,
                options: options,
                ORDER: -1,
                messages: messages, // Cetmix
                is_cetmix_thread: true,
                dateFormat: time.getLangDatetimeFormat(),
            }));

            _.each(messages, function (message) {
                var $message = self.$('.o_thread_message[data-message-id="'+ message.getID() +'"]');
                $message.find('.o_mail_timestamp').data('date', message.getDate());

                self._insertReadMore($message);
            });

            if (shouldScrollToBottomAfterRendering) {
                this.scrollToBottom();
            }

            if (!this._updateTimestampsInterval) {
                this.updateTimestampsInterval = setInterval(function () {
                    self._updateTimestamps();
                }, 1000*60);
            }

            this._renderMessageMailPopover(messages);
            if (thread.hasSeenFeature()) {
                this._renderMessageSeenPopover(thread, messages);
            }
        },
    });

});
