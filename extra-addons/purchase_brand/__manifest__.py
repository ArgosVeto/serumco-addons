# Copyright (C) 2020 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
	'name': 'Purchase Brand',
	'summary': 'Send branded purchase orders',
	'version': '13.0.1.0',
	'category': 'Purcahses',
	'website': 'https://arkeup.com',
	'author': 'ArkeUp SAS',
	'license': 'AGPL-3',
	'depends': [
		'brand',
		'purchase',
	],
	'data': [
		'views/purchase_views.xml',
	],
	'installable': True,
	'development_status': 'Beta',
}
