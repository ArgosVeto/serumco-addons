# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018 ArkeUp (<http://www.arkeup.fr>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Arkeup Impex',
    'summary': """
        Manage import / export file from interface using smile_impex
    """,
    'description': """
        Manage import / export file from interface using smile_impex
        Suggestions & Feedback to j.andrinirina@etechconsulting-mg.com
    """,
    'author': 'ArkeUp',
    'website': 'http://www.arkeup.fr',
    'category': 'Tools',
    'version': '0.1',
    'depends': [
        'smile_impex',
        'web_widget_binary_filter',
    ],
    'data': [
        'views/import_template_view.xml',
    ],
}
