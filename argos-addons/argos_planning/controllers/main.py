# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class PlanningWebservice(http.Controller):

    @http.route('/mrdv/listEvent', type='json', auth='user', method=['GET'])
    def list_event(self, timeMin=False, timeMax=False, OdooCalendarIds=[]):
        """
        :param timeMin:
        :param timeMax:
        :param OdooCalendarIds:
        :return:
        """
        try:
            slot_obj = request.env['planning.slot']
            planning_ids = slot_obj.search([('start_datetime', '>=', timeMin), ('end_datetime', '<=', timeMax),
                                            ('id', 'in', OdooCalendarIds)])
            plannings = [{
                'mrdvEventId': planning.mrdv_event_id,
                'mrdvJobId': planning.mrdv_job_id,
                'OdooCalendarId': planning.id,
                'source': planning.source,
                'type': planning.role_id.role_type,
                'title': planning.name,
                'status': planning.state,
                'petName': planning.animal_id.name,
                'animalName': planning.animal_id.category_id.name,
                'customerName': planning.partner_id.name,
                'customerPhone': planning.partner_id.phone,
                'customerMoreInfo': planning.more_info,
                'consultationName': planning.consultation_type_id.name,
                'startDate': planning.start_datetime,
                'endDate': planning.end_datetime,
                'location': planning.operating_unit_id.name
            } for planning in planning_ids]
            return plannings
        except Exception as e:
            return {'message': repr(e)}

    @http.route('/mrdv/cancelEvent', type='json', auth='user', method=['GET'])
    def cancel_event(self, mdrvEventId=False, mdrvJobId=False, OdooCalendarId=False):
        """
        :param mdrvEventId:
        :param mdrvJobId:
        :param OdooCalendarId:
        :return:
        """
        try:
            slot_obj = request.env['planning.slot']
            slot = slot_obj.search([('mrdv_event_id', '=', mdrvEventId), ('mrdv_job_id', '=', mdrvJobId), ('id', '=', OdooCalendarId)])
            slot.write({'state': 'cancel'})
            return {'message': 'OK'}
        except Exception as e:
            return {'message': repr(e)}

    @http.route('/mrdv/archiveEvent', type='json', auth='user', method=['GET'])
    def archive_event(self, mdrvEventId=False, mdrvJobId=False, OdooCalendarId=False):
        """
        :param mdrvEventId:
        :param mdrvJobId:
        :param OdooCalendarId:
        :return:
        """
        try:
            slot_obj = request.env['planning.slot']
            slot = slot_obj.search([('mrdv_event_id', '=', mdrvEventId), ('mrdv_job_id', '=', mdrvJobId), ('id', '=', OdooCalendarId)])
            slot.write({'active': False})
            return {'message': 'OK'}
        except Exception as e:
            return {'message': repr(e)}

    @http.route('/mrdv/pushEvent', type='json', auth='user', method=['POST'])
    def push_event(self, **post):
        """
        :param post:
        :return:
        """
        try:
            slot_obj = request.env['planning.slot']
            vals = slot_obj._prepare_slot_data(post)
            slot_obj.create(vals)
            return {'message': 'OK'}
        except Exception as e:
            return {'message': repr(e)}
