# -*- coding: utf-8 -*-

from odoo.tests import HttpCase


class TestReceiveCall(HttpCase):
    """
        Tests for making call from odoo
    """

    def setUp(self):
        super(TestReceiveCall, self).setUp()
        self.server_keyyo = self.env['keyyo.line.server'].create({'name': 'KEYYO-LINE'})
        self.commercial = self.env['res.users'].create({'name': 'Commercial Test',
                                                        'login': 'commercial-test',
                                                        'sip': 'COMMERCIAL-PHONE-NUMBER',
                                                        'keyyo_line_server_id': self.server_keyyo.id})
        self.contact = self.env['res.partner'].create({'name': 'CONTACT TEST', 'phone': 'CONTACT-PHONE-NUMBER'})

    def test_receive_call_001(self):
        """
            1. check if a new log is created after call receive
            2. search created log and check if corresponding to the contact
        :return:
        """
        count = self.env['call.log'].search_count([])
        resp = self.url_open('/web/keyyo/notifycall?account=%s&caller=%s&callee=%s' % ('KEYYO-LINE', 'CONTACT-PHONE-NUMBER',
                                                                                       'COMMERCIAL-PHONE-NUMBER'))
        self.assertEqual(resp.status_code, 200, 'Waiting 200')
        logs = self.env['call.log'].search([])
        # 1. check if a new log is created after call receive
        self.assertEqual(count + 1, len(logs))
        # 2. search created log and check if corresponding to the contact
        log = logs[0]  # the last created one
        self.assertEqual(log.type, 'incoming')
        self.assertEqual(log.partner_id, self.commercial.partner_id)
        self.assertEqual(log.caller_number, 'CONTACT-PHONE-NUMBER')
