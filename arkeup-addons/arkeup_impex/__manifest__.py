# -*- encoding: utf-8 -*-

{
    'name': 'ArkeUp IMPEX',
    'summary': 'Manage import / export file from interface using smile_impex',
    'description': '',
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'category': 'Tools',
    'version': '0.1',
    'depends': [
        'smile_impex',
        'web_widget_binary_filter',
    ],
    'data': [
        # views
        'views/ir_model_export_template_view.xml',
        'views/ir_model_import_template_view.xml',
    ],
}
