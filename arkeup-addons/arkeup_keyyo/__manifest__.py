# -*- coding: utf-8 -*-

{
	'name': 'ArkeUp Keyyo CTI',
	'version': '1.0',
	'category': 'Tools',
	'sequence': -52,
	'summary': 'Manage Keyyo API',
	'author': 'Arkeup',
	'website': 'www.arkeup.com',
	'description': """
Manage Keyyo CTI 
================
- ClickToCall    
- Call log    
- User record feedback
""",
	'depends': ['contacts'],
	'data': [
		# data
		'data/ir_config_parameter.xml',
		'data/res_users_data.xml',
		# security
		'security/ir.model.access.csv',
		# views
		'views/res_users_view.xml',
		'views/call_log_view.xml',
		'views/keyyo_line_server_view.xml',
		'views/templates.xml',
	],
	'license': 'AGPL-3',
	'qweb': [],
	'demo': [],
	'installable': True,
	'application': False,
}
