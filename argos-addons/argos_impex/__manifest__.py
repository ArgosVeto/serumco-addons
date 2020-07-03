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
    'name': "argos_impex",

    'summary': """
        Manage import / export file from interface using smile_impex and arkeup_impex
    """,

    'description': """
        Manage import / export file from interface using smile_impex and arkeup_impex
    """,

    'author': "ArkeUp",
    'website': "http://www.arkeup.fr",

    'category': 'Tools',
    'version': '0.1',
    'sequence': -12,

    'depends': ['arkeup_impex', 'argos_base'],

    'data': [
        # security
        'security/ir.model.access.csv',

        # data

        # views
        'views/ir_model_import_template.xml',
    ],

}