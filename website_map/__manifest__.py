
{
    'name': 'Website  Maps',
    'category': 'Website',
    'version': '13.0.0.0',
    'summary': '''Website Maps''',
    'author':'',
    'description': """Website Maps""",
    'depends': [
        'argos_hr',
        'operating_unit',
        'website_argos',
        'hr_recruitment',
        'website_hr_recruitment',
    ],
    'data': [
        'views/website_map.xml',
        'views/slider_snippets.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application': True,
}