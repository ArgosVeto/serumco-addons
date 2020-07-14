# -*- coding: utf-8 -*-

{
	'name': 'ArkeUp Xml Parser',
	'version': '1.0',
	'category': 'Tools',
	'sequence': -2,
	'summary': 'Allow to parse Xml datas',

	'author': 'Arkeup',
	'website': 'https://arkeup.com',
	'description': '',
	'depends': ['base'],
	'data': [
		# data
		'data/ir_sequence.xml',
		# security
		'security/ir.model.access.csv',
		# views
		'views/xml_parser_view.xml',
		'views/fields_mapping.xml',
	],
	'license': 'AGPL-3',
	'qweb': [],
	'demo': [],
	'installable': True,
	'application': False,
	'auto_install': False,
}
