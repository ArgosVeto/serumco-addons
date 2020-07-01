.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================
Web Widget - Binary Filter
==========================

Description
-----------

This module was written to extend the functionality of the field binary widget to accept only specified file extensions.

Usage
=====

You need to declare a binary field::

    ...
    binary_file = fields.Binary(string="Binary file")
    binary_file_name = fields.Char(string="Binary file name")
    ...

In the view declaration, put widget='file_filter' and options="{'accept': '.xls, .xlsx'}" attributes in the field tag::

    ...
    <field name="arch" type="xml">
        <tree string="View name">
            ...
            <field name="name"/>
            <field name="binary_file" widget="file_filter" options="{'accept': '.xls, .xlsx'}"/>
            <field name="binary_file_name" invisible="1"/>
            ...
        </tree>
    </field>
    ...

Contributors
------------

* Jose ANDRIANATOAVINA <joseandrianatoavina@gmail.com> [v.10]
* Harifetra RAKOTOMALALA <haricod3r@gmail.com> [v.11]
