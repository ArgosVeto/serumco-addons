# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)
KEY = "secret"


class PlanningWebservice(http.Controller):

    @http.route('/mrdv/listEvent', type='json', auth="user", method=['GET'])
    def list_event(self, timeMin=False, timeMax=False, OdooCalendarIds=[]):
        try:
            planning_ids = request.env['planning.slot'].search(
                [('start_datetime', '>=', timeMin), ('end_datetime', '<=', timeMax), ('id', 'in', OdooCalendarIds)])
            plannings = [{
                'mrdvEventId': planning.mrdv_event_id,
                'mrdvJobId': planning.mrdv_job_id,
                'OdooCalendarId': planning.id,
                'source': planning.source,
                'type': planning.role_id.role_type if planning.role_id else False,
                'title': planning.name,
                'status': planning.state,
                'petName': planning.animal_id.name if planning.animal_id else False,
                'animalName': planning.animal_id.category_id.name if (
                        planning.animal_id and planning.animal.category_id) else False,
                'customerName': planning.partner_id.name if planning.partner_id else False,
                'customerPhone': planning.partner_id.phone if planning.partner_id else False,
                'customerMoreInfo': planning.more_info,
                'consultationName': planning.consultation_type_id.name if planning.consultation_type_id else False,
                'startDate': planning.start_datetime,
                'endDate': planning.end_datetime,
                'location': planning.operating_unit_id.name if planning.operating_unit_id else False
            } for planning in planning_ids]
            return plannings
        except Exception as e:
            return {'message': repr(e)}

    @http.route('/mrdv/cancelEvent', type='json', auth='user', method=['GET'])
    def cancel_event(self, mdrvEventId=False, mdrvJobId=False, OdooCalendarId=False):
        try:
            slot = request.env['planning.slot'].search(
                [('mrdv_event_id', '=', mdrvEventId), ('mrdv_job_id', '=', mdrvJobId), ('id', '=', OdooCalendarId)])
            slot.write({'state': 'cancel'})
            return {'message': 'OK'}
        except Exception as e:
            return {'message': repr(e)}

    @http.route('/mrdv/archiveEvent', type='json', auth='user', method=['GET'])
    def archive_event(self, mdrvEventId=False, mdrvJobId=False, OdooCalendarId=False):
        try:
            slot = request.env['planning.slot'].search(
                [('mrdv_event_id', '=', mdrvEventId), ('mrdv_job_id', '=', mdrvJobId), ('id', '=', OdooCalendarId)])
            slot.write({'active': False})
            return {'message': 'OK'}
        except Exception as e:
            return {'message': repr(e)}

    @http.route('/mrdv/pushEvent', type='json', auth="user", method=['POST'])
    def push_event(self, **post):
        try:
            slot_obj = request.env['planning.slot']
            vals = slot_obj._prepare_slot_data(post)
            slot_obj.create(vals)
            return {'message': 'OK'}
        except Exception as e:
            return {'message': repr(e)}
