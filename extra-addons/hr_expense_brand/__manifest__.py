# Copyright (C) 2020 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
	'name': 'HR Expense Brand',
	'summary': 'Send branded hr expenses orders',
	'version': '13.0.1.0',
	'category': 'HR',
	'website': 'https://arkeup.com',
	'author': 'ArkeUp SAS',
	'license': 'AGPL-3',
	'depends': [
		'brand',
		'hr_expense',
	],
	'data': [
		'views/hr_expense_view.xml',
	],
	'installable': True,
	'application': False,
	'auto_install': False
}
