# -*- coding: utf-8 -*-

from collections import defaultdict

from odoo import api, fields, models, exceptions, _
import logging

from odoo.tools.misc import clean_context
_logger = logging.getLogger(__name__)


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    product_id = fields.Many2one('product.product', 'Product')
    product_quantity = fields.Integer('Quantity', default=1)
    done = fields.Boolean('Done', default=False)

    @api.constrains('product_id')
    def _check_quantity(self):
        for r in self:
            if r.product_id and r.product_quantity < 1:
                raise exceptions.ValidationError(_("The quantity of a product cannot be less than 0."))

    def add_product_to_sale_order(self):
        if self.product_id:
            task = self.env['project.task'].search([('id', '=', self.res_id)], limit=1)

        sale_order_line = self.env['sale.order.line']
        order_line = sale_order_line.search([('order_id', '=', task.sale_order_id.id), ('product_id', '=', self.product_id.id)], limit=1)

        if order_line:
            order_line.write({
                'product_uom_qty': order_line.product_uom_qty + self.product_quantity,
            })
        else:
            sale_order_line.create({
                'order_id': task.sale_order_id.id,
                'product_id': self.product_id.id,
                'project_id': task.project_id.id,
                'task_id': task.id,
                'product_uom_qty': self.product_quantity,
                'product_uom': self.product_id.product_tmpl_id.uom_id.id,
            })

    def action_done_schedule_next(self):
        """override"""
        """ Wrapper without feedback because web button add context as
        parameter, therefore setting context to feedback """
        self.add_product_to_sale_order()
        return self.action_feedback_schedule_next()

    def action_done(self):
        """override"""
        """ Wrapper without feedback because web button add context as
        parameter, therefore setting context to feedback """

        self.add_product_to_sale_order()
        messages, next_activities = self._action_done()
        return messages.ids and messages.ids[0] or False

    def action_feedback(self, feedback=False, attachment_ids=None):
        """override"""
        self.add_product_to_sale_order()
        self = self.with_context(clean_context(self.env.context))
        messages, next_activities = self._action_done(feedback=feedback, attachment_ids=attachment_ids)
        return messages.ids and messages.ids[0] or False

    def action_feedback_schedule_next(self, feedback=False):
        """override"""
        self.add_product_to_sale_order()
        ctx = dict(
            clean_context(self.env.context),
            default_previous_activity_type_id=self.activity_type_id.id,
            activity_previous_deadline=self.date_deadline,
            default_res_id=self.res_id,
            default_res_model=self.res_model,
        )
        messages, next_activities = self._action_done(feedback=feedback)  # will unlink activity, dont access self after that
        if next_activities:
            return False
        return {
            'name': _('Schedule an Activity'),
            'context': ctx,
            'view_mode': 'form',
            'res_model': 'mail.activity',
            'views': [(False, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    def _action_done(self, feedback=False, attachment_ids=None):
        """override"""
        """ Private implementation of marking activity as done: posting a message, deleting activity
            (since done), and eventually create the automatical next activity (depending on config).
            :param feedback: optional feedback from user when marking activity as done
            :param attachment_ids: list of ir.attachment ids to attach to the posted mail.message
            :returns (messages, activities) where
                - messages is a recordset of posted mail.message
                - activities is a recordset of mail.activity of forced automically created activities
        """
        # marking as 'done'
        messages = self.env['mail.message']
        next_activities_values = []

        # Search for all attachments linked to the activities we are about to unlink. This way, we
        # can link them to the message posted and prevent their deletion.
        attachments = self.env['ir.attachment'].search_read([
            ('res_model', '=', self._name),
            ('res_id', 'in', self.ids),
        ], ['id', 'res_id'])

        activity_attachments = defaultdict(list)
        for attachment in attachments:
            activity_id = attachment['res_id']
            activity_attachments[activity_id].append(attachment['id'])

        for activity in self:
            # extract value to generate next activities
            if activity.force_next:
                activity_obj = self.env['mail.activity'].with_context(
                    activity_previous_deadline=activity.date_deadline)  # context key is required in the onchange to set deadline
                vals = activity_obj.default_get(activity_obj.fields_get())

                vals.update({
                    'previous_activity_type_id': activity.activity_type_id.id,
                    'res_id': activity.res_id,
                    'res_model': activity.res_model,
                    'res_model_id': self.env['ir.model']._get(activity.res_model).id,
                })
                virtual_activity = activity_obj.new(vals)
                virtual_activity._onchange_previous_activity_type_id()
                virtual_activity._onchange_activity_type_id()
                next_activities_values.append(virtual_activity._convert_to_write(virtual_activity._cache))

            # post message on activity, before deleting it
            record = self.env[activity.res_model].browse(activity.res_id)
            record.message_post_with_view(
                'mail.message_activity_done',
                values={
                    'activity': activity,
                    'feedback': feedback,
                    'display_assignee': activity.user_id != self.env.user
                },
                subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_activities'),
                mail_activity_type_id=activity.activity_type_id.id,
                attachment_ids=[(4, attachment_id) for attachment_id in attachment_ids] if attachment_ids else [],
            )

            # Moving the attachments in the message
            # TODO: Fix void res_id on attachment when you create an activity with an image
            # directly, see route /web_editor/attachment/add
            activity_message = record.message_ids[0]
            message_attachments = self.env['ir.attachment'].browse(activity_attachments[activity.id])
            if message_attachments:
                message_attachments.write({
                    'res_id': activity_message.id,
                    'res_model': activity_message._name,
                })
                activity_message.attachment_ids = message_attachments
            messages |= activity_message
        self.write({'done': True})

        next_activities = self.env['mail.activity'].create(next_activities_values)

        return messages, next_activities
