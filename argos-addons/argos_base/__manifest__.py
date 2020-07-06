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
    'depends': ['base', 'web', 'l10n_fr', 'product','contacts','operating_unit','arkeup_keyyo'],
    'data': [
        'security/ir.model.access.csv',
        # views
        'views/product_template.xml',
        'views/animal_views.xml',
        'views/animal_category_views.xml',
        'views/animal_race_views.xml',
        'views/animal_robe_views.xml',
        'views/animal_insurance_views.xml',
        'views/living_environment_views.xml',
        'views/animal_diet_views.xml',
        'views/animal_pathology_views.xml',
        'views/family_views.xml',
        'views/res_partner_views.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
}
