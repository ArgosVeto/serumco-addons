# Copyright (C) 2020 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
	'name': 'Account Brand',
	'summary': 'Send branded invoices and refunds',
	'version': '13.0.1.0',
	'category': 'Accounting Management',
	'website': 'https://github.com/OCA/account-invoicing',
	'author': 'Odoo Community Association (OCA)',
	'license': 'AGPL-3',
	'depends': [
		'account',
		'brand',
		'analytic',
	],
	'data': [
		'views/account_move_view.xml',
		'views/account_analytic_account_view.xml',
	],
	'installable': True,
	'auto_install': True,
	'application': False,
}
