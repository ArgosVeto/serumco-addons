{
    'name': "Jitsi Online Meeting",
    'version': '13.0.1.2.0',
    'summary': """
        Full integration of Jitsi Video Conferencing in Flectra Calendar""",
    'author': "Jamotion GmbH, Jamotion GmbH",
    'website': "https://jamotion.ch",
    'category': 'Events',
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 65,
    'currency': 'EUR',
    'depends': [
        'calendar',
        'website',
    ],
    'data': [
        'data/mail_templates.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [],
    'qweb': [
        'static/src/xml/templates.xml',
    ],
    'css': [],
    'images': ['static/description/module-banner.png', ],
}
