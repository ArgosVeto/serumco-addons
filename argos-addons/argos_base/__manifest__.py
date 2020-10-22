# -*- coding: utf-8 -*-
{
    'name': 'Argos Base',
    'summary': '',
    'category': 'Base',
    'version': '1.0',
    'sequence': -99,
    'author': 'Omar OUHARI',
    'license': 'AGPL-3',
    'website': 'https://arkeup.com',
    'description': '',
    'depends': [
        'l10n_fr',
        'product',
        'contacts',
        'operating_unit',
        'documents',
        'maintenance',
        'website_crm_partner_assign',
        'partner_firstname',
        'jitsi_meet_integration',
        'prt_mail_messages_pro',
        'arkeup_saop_wsdl_log',
        'smile_anonymization',
        'many2one_item_limit',
        'search_more_shortcut'
    ],
    'data': [
        # data
        'data/res_users_data.xml',
        'data/mail_template_data.xml',
        'data/res_config_parameter_data.xml',
        # security
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        # views
        'views/assets.xml',
        'views/product_template_views.xml',
        'views/res_partner_views.xml',
        'views/res_company_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
