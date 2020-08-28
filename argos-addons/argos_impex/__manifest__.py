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
    'name': 'Argos Impex',
    'summary': 'Manage Import/Export file from web interface',
    'description': '',
    'author': 'ArkeUp',
    'website': 'https://arkeup.fr',
    'category': 'Tools',
    'version': '0.1',
    'sequence': -94,
    'depends': ['arkeup_impex', 'arkeup_ftp', 'argos_contact', 'queue_job_subscribe', 'queue_job_cron'],
    'data': [
        # data
        'data/server_ftp_data.xml',
        'data/ir_model_import_template_data.xml',
        # security
        'security/ir.model.access.csv',
        # views
        'views/ir_model_import_template.xml',
    ],
}
