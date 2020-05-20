# Copyright (C) 2020 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
	'name': 'Sale Brand',
	'summary': 'Send branded sales orders',
	'version': '13.0.1.0',
	'category': 'Sales Management',
	'website': 'https://github.com/OCA/sale-workflow',
	'author': 'Odoo Community Association (OCA)',
	'license': 'AGPL-3',
	'depends': [
		'sale',
		'brand',
		'account_brand',
	],
	'data': [
		'views/sale_views.xml',
	],
	'installable': True,
	'development_status': 'Beta',
	'maintainers': ['osi-scampbell'],
}
