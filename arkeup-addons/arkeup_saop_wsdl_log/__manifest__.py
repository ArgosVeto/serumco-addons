# -*- coding: utf-8 -*-

{
	'name': 'ArkeUp SOAP WSDL Logs',
	'version': '1.0',
	'category': 'Tools',
	'sequence': -40,
	'summary': 'Log call of saop wsdl log and give possibility to re-call',
	'author': 'Arkeup',
	'website': 'https://arkeup.com',
	'description': """
Manage log of ws call
=====================
- Log call
- Retry call
""",
	'depends': ['base'],
	'data': [
		# data
		'data/ir_sequence.xml',
		# security
		'security/ir.model.access.csv',
		# views
		'views/soap_wsdl_log_view.xml',
		'views/ir_ui_menu.xml',
	],
	'license': 'AGPL-3',
	'qweb': [],
	'demo': [],
	'installable': True,
	'application': False,
	'auto_install': False,
}
