# -*- coding: utf-8 -*-
{
    'name': "Search more shorcut",

    'summary': """
        This module add a shortcut on the search more item in many2one drowpdown""",

    'author': "Samuel RAMAROSELY",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_setup'],

    # always loaded
    'data': [
        'views/assets_backend.xml',
    ],
}
