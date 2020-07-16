# -*- coding: utf-8 -*-
{
    'name': 'Mail Messages Easy Pro:'
            ' Show Lost Message, Move Message, Reply, Forward, Move, Edit or Delete from Chatter, Filter Messages in Chatter',
    'version': '13.0.4.2',
    'summary': """Extra features for free 'Mail Messages Easy' app""",
    'author': 'Ivan Sokolov, Cetmix',
    'license': 'OPL-1',
    'price': 69.00,
    'currency': 'EUR',
    'category': 'Discuss',
    'support': 'odooapps@cetmix.com',
    'website': 'https://cetmix.com',
    'live_test_url': 'https://demo.cetmix.com',
    'description': """
Show Lost Message, Move Message, Reply, Forward, Move, Edit or Delete from Chatter, Filter Messages in Chatter
""",
    'depends': ['prt_mail_messages', 'mail'],
    'data': [
        'security/groups.xml',
        'views/prt_mail_pro.xml',
        'views/mail_assign.xml',
        'data/templates.xml'
    ],

    'images': ['static/description/banner_pro.png'],

    'qweb': [
        'static/src/xml/qweb.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False
}
