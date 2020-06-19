# -*- coding: utf-8 -*-

import logging
import requests
from odoo import http, _, fields
from odoo.http import request

from . import tools

_logger = logging.getLogger(__name__)


class KeyyoController(http.Controller):

	@http.route('/web/keyyo/makecall', type='json', auth='user', methods=['POST'])
	def makecall(self, **kw):
		"""
			This function is called from web page to make a call
		"""
		if kw.get('source') not in ('phone', 'mobile'):
			return {'status': 401, 'msg': _('unknown source!')}
		keyyo_line_name = request.env.user.keyyo_line_server_id.name
		partner_obj = request.env['res.partner']
		log_obj = request.env['call.log']
		if not keyyo_line_name:
			return {'status': 404, 'msg': _('Your keyyo line is not defined. Please fill your keyyo line in preferences!')}
		endpoint = request.env['ir.config_parameter'].sudo().get_param('keyyo.makecall.endpoint')
		if not endpoint:
			return {'status': 404, 'msg': _("""The keyyo EndPoint is not defined. 
			Please fill it in system parameters or contact the system administrator!""")}
		if kw.get('source') == 'phone':
			domain = [('phone', '=', kw.get('callee'))]
		else:
			domain = [('mobile', '=', kw.get('callee'))]
		callee = tools.remove_space(kw.get('callee'))
		callee_name = kw.get('callee_name')
		payload = {'ACCOUNT': tools.remove_space(keyyo_line_name), 'CALLEE': callee, 'CALLEE_NAME': callee_name}
		vals = {
			'user_id': request.env.user.id,
			'caller_number': keyyo_line_name,
			'date': fields.Datetime.now(),
			'callee_number': kw.get('callee'),
			'partner_id': partner_obj.search(domain, limit=1).id
		}
		try:
			_logger.info('start calling endpoint %s with parameters %s' % (endpoint, payload))
			res = requests.get(endpoint, params=payload)
			msg = res.text
			_logger.info('result of calling endpoint: [%s]', msg)
			vals.update({'status': res.status_code, 'url': res.url, 'message': msg})
			log_obj.create(vals)
			if res.status_code != 200:
				return {'status': res.status_code, 'msg': msg}
			return {'status': res.status_code, 'msg': _('Call in progress to %s') % callee}
		except Exception as e:
			_logger.error(repr(e))
			vals.update({'status': 401, 'message': repr(e)})
			log_obj.create(vals)
			return {'status': 401, 'msg': repr(e)}

	@http.route('/web/keyyo/notifycall', type='http', auth='public', methods=['GET'], website=True)
	def notifycall(self, account='', caller='', callee='', call_ref='', n_type='', version=1, dref='', dref_replace='', session_id='',
	               is_acd=False, redirecting_number=''):
		"""
		:param account:
		:param caller:
		:param callee:
		:param call_ref:
		:param n_type:
		:param version:
		:param dref:
		:param dref_replace:
		:param session_id:
		:param is_acd:
		:param redirecting_number:
		"""
		_logger.info("""
		/web/keyyo/notifycall called with this parameters : [account: %s], [caller: %s], [callee: %s], [call_ref: %s], [n_type: %s], 
		[version: %s], [dref: %s], [dref_replace: %s], [session_id: %s], [is_acd: %s], [redirecting_number: %s]""" %
		             (account, caller, callee, call_ref, n_type, version, dref, dref_replace, session_id, is_acd, redirecting_number))
		keyyo_user = request.env.ref('arkeup_keyyo.keyyo_cti_user', raise_if_not_found=True)
		keyyo_line_server_obj = request.env['keyyo.line.server'].with_user(keyyo_user)
		keyyo_line_server = keyyo_line_server_obj.search([('name', '=', account)], limit=1)
		if not keyyo_line_server:
			_logger.info(_('Keyyo Line not defined!'))
			return _('Keyyo Line not defined!')
		callee = callee.replace(' ', '')
		callee_inter_format = '+' + callee
		callee_national_format = '0' + callee[2:]
		user_callee = keyyo_line_server.user_ids.filtered(lambda usr: usr.sip in [callee, callee_inter_format, callee_national_format])
		if not user_callee:
			_logger.info(_('User callee not found.'))
			return _('User callee not found.')
		vals = {
			'user_id': keyyo_user.id,  # keyyo user
			'caller_number': caller,
			'date': fields.Datetime.now(),
			'partner_id': user_callee.partner_id.id,
			'callee_number': callee,
			'type': 'incoming',
			'status': 200,
			'message': 'OK',
			'url': """
				account: %s,
				caller: %s,
				callee: %s,
				call_ref: %s,
				n_type: %s,
				version: %s,
				dref: %s,
				dref_replace: %s,
				session_id: %s,
				is_acd: %s,
				redirecting_number: %s				
			""" % (account, caller, callee, call_ref, n_type, version, dref, dref_replace, session_id, is_acd, redirecting_number),
		}
		call_log_obj = request.env['call.log'].with_user(keyyo_user)
		call_log_obj.create(vals)
		# notify the commercial
		partner_obj = request.env['res.partner'].with_user(keyyo_user)
		channel_obj = request.env['mail.channel'].with_user(keyyo_user)
		result = channel_obj.channel_get([user_callee.partner_id.id])
		vals = {
			'partner_ids': [],
			'channel_ids': [],
			'body': partner_obj._get_contact_url(caller),
			'attachment_ids': [],
			'canned_response_ids': [],
			'subtype': 'mail.mt_comment'
		}
		if result:
			channel = channel_obj.browse(result.get('id'))
			channel.message_post(message_type='comment', **vals)
		_logger.info('OK')
		return 'OK'
