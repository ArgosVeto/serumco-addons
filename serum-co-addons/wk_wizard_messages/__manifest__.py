# -*- coding: utf-8 -*-
{
  "name"                 :  "Webkul Message Wizard",
  "summary"              :  """To show messages/warnings in Odoo""",
  "category"             :  "Tools",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Apagen Solutions Pvt. Ltd.",
  "description"          :  """""",
  "data"                 :  ['wizard/wizard_message_view.xml'],
  "images"               :  ['static/description/Banner.png'],
  "installable"          :  True,
  "pre_init_hook"        :  "pre_init_check",
}