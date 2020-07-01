# -*- coding: utf-8 -*-
# Copyright 2018 Jose ANDRIANANTOAVINA <joseandrianatoavina@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Web Widget - Binary Filter",
    "summary": "Binary file widget to accept only specified file extensions",
    "version": "11.0.1.0.0",
    "category": "web",
    "author": "Jose ANDRIANATOAVINA v.10, Harifetra RAKOTOMALALA v.11",
    "license": "LGPL-3",
    "application": False,
    'installable': True,
    "data": [
        "views/assets.xml",
    ],
    "depends": [
        "web",
    ],
    "qweb": [
        "static/src/xml/web_widget_binary_filter.xml",
    ]
}
